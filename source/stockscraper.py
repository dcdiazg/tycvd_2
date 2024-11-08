# 08/11/2024
"""StockScraper

Presenta la clase StockScraper, encargada de realizar las funciones de
webscraping y almacenamiento de datos de las acciones de las bolsas de valores
('stocks') principales de varios países del mundo.

La web que se usa para consulatr es 'https://www.tradingview.com/markets/'.

"""

import csv
from pathlib import Path
from time import perf_counter, sleep, time

import requests
from bs4 import BeautifulSoup
from more_itertools import chunked
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

COUNTRIES_CSV_HEADERS = ["Continent", "Country", "URLToken"]
RESULTS_CSV_HEADER = [
    "Timestamp",
    "Continent",
    "Country",
    "Symbol",
    "Name",
    "Price",
    "Currency",
    "Volume (M)",
    "Market Cap (M)",
    "Sector",
]

STOCKS_URL = "https://www.tradingview.com/markets/{token}/market-movers-active/"

TESTING_COUNTRY = ("North America", "USA", "stocks-usa")

TD_IDX_STOCK_NAME = 0
TD_IDX_STOCK_PRICE = 2
TD_IDX_STOCK_VOLUME = 4
TD_IDX_MARKET_CAP = 6
TD_IDX_SECTOR = -2


def q_normalize(svalue: str) -> float:
    """Normaliza cantidades en las que la magnitud se expresa con letras

    Identifica la magnitud en cuestión y la convierte siguiendo el
    siguiente criterio:

    'K' -> * 0.001
    'M' -> * 1.0
    'B' -> * 1_000.0
    'T' -> * 1_000_000.0

    Si no se identifica ninguna magnitud, se devuelve el valor original.
    Devuelve el valor normalizado como un número en coma flotante.

    """
    if svalue.endswith("K"):
        return float(svalue.removesuffix("K")) * 0.001
    elif svalue.endswith("M"):
        return float(svalue.removesuffix("M"))
    elif svalue.endswith("B"):
        return float(svalue.removesuffix("B")) * 1_000
    elif svalue.endswith("T"):
        return float(svalue.removesuffix("T")) * 1_000_000
    else:
        return float(svalue)


class StockScraper:
    """Realiza webscraping de datos de acciones de bolsas de valores

    El constructor puede recibir, como único argument, la ruta al ejecutable
    del WebDriver requerido para Selenium (sólo se admite Chrome). En caso de
    no indicarse ninguno, se utilizará la librería 'webdriver-manager' para
    obtenerlo.

    """

    def __init__(self, selenium_webdriver_executable: Path | str = "") -> None:
        self._executable = selenium_webdriver_executable

    # Público

    def choose_countries(
        self,
        *,
        all: bool = False,
        output_dir: str | Path | None = None,
        verbose: bool = False,
    ) -> None:
        """Permite escoger los países de cuyos mercados se desean obtener
        datos.

        Por defecto, carga todos los países disponibles en la web, y le muestra
        al usuario una interfaz sencilla donde seleccionar o deseleccionar sus
        preferencias. Alternativamente, si se llama con 'all=True', se
        garantiza que todos los países posible serán seleccionados.

        En última instancia, genera un archivo CSV ('countries.csv') en el que
        se indican los países seleccionados junto con la URL de sus mercados.
        Por defecto, se almacena en el directorio de trabajo, pero se puede
        modificar la ruta de salida con el argumento 'output_dir'.

        Si 'verbose' es True, se mostrarán mensajes informativos durante la
        ejecución.

        No se devuelve ningún valor.

        """
        countries = []
        # Setup del WebDriver, modo silencioso
        driver = self._setup_webdriver()
        if verbose:
            print(">>> WebDriver correctamente configurado")
        # Cargamos la web
        driver.get(STOCKS_URL.format(token=TESTING_COUNTRY[-1]))
        driver.implicitly_wait(10)
        # Clicamos el botón de "US stocks", que nos lleva a un menú para seleccionar países
        all_buttons = driver.find_elements(By.TAG_NAME, "button")
        target = [button for button in all_buttons if button.text == "US stocks"][0]
        target.click()
        # Ubicamos el menú y recogemos el continent, país, y URL a su mercado
        driver.implicitly_wait(5)
        dialog = driver.find_element(By.XPATH, "//div[starts-with(@class, 'dialog-')]")
        content = dialog.find_element(By.XPATH, "./div/div[3]")
        for continent_div, countries_div in chunked(
            content.find_elements(By.XPATH, "./div")[1:], 2
        ):
            continent = continent_div.text.title()
            for country_item in countries_div.find_elements(By.TAG_NAME, "a"):
                country, url = country_item.text.split("\n")[
                    0
                ], country_item.get_attribute("href")
                token = url.split("/")[-3]
                countries.append((continent, country, token))
                if verbose:
                    print(f">>> {continent} | {country} | {token}")
        # Cerrar el WebDriver
        driver.quit()
        # Si indicamos que NO queremos todos los países, mostrar interfaz
        if not all:
            pass  # TODO: Implementar selección de países (tkinter)
        # Si se indica un 'output_dir', comprobamos que existe Y es un directorio
        if output_dir:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                raise FileNotFoundError(
                    f"No se ha encontrado el directorio {output_dir!r}"
                )
            if not output_dir.is_dir():
                raise NotADirectoryError(f"{output_dir!r} no es un directorio válido")
        else:
            output_dir = Path.cwd()
        # Guardamos como CSV
        with open(output_dir / "countries.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(COUNTRIES_CSV_HEADERS)
            writer.writerows(countries)
        if verbose:
            print(
                f">>> Países seleccionados guardados en {output_dir / 'countries.csv'}"
            )

    def scrape(
        self,
        countries: str | Path | None = "",
        *,
        loops: int = 1,
        wait: float = 5.0,
        output_dir: str | Path | None = None,
        verbose: bool = False,
    ) -> Path:
        """Realiza el scraping de los mercados de valores de los países

        'countries' indica qué países se van a consultar. Si es None, o una
        cadena vacía, tratará de ubicar el archivo 'countries.csv' en el
        directorio de trabajo, y si no existe, generará uno mediante
        'choose_countries(all=True)'. Si 'countries' vale 'testing', se usará
        únicamente el stock de EEUU, a modo de prueba. En caso contrario,
        'countries' debe ser la ruta al archivo CSV con los países y las URLs
        de sus mercados, generadas previamente mediante 'choose_countries()'.

        'loops' indica el número de veces que se realizará el scraping,
        esperando 'wait' minutos entre cada iteración (mínimo, 5, para respetar
        la política de uso de la web).

        'output_dir' debe ser la ruta al directorio donde se guardarán los
        resultados en formato CSV, 'results.csv'. Si no se indica nada, se
        guardará en el directorio de trabajo.

        'verbose' indica si se mostrarán mensajes informativos durante la
        ejecución.

        Devuelve la ruta al archivo CSV con los datos de las acciones de los
        países seleccionados, y el instante en el que fueron descargados.

        """
        # Comprobamos 'countries' y generamos la lista de países
        _countries_path = countries
        countries = []

        if _countries_path == "testing":
            countries.append(TESTING_COUNTRY)
        else:
            if not _countries_path:
                # Busca primero en el directorio de trabajo actual
                _countries_path = Path.cwd() / "countries.csv"
                if not _countries_path.exists():
                    # Si no existe, se generan los países
                    self.choose_countries(all=True)
                    _countries_path = Path.cwd() / "countries.csv"
            # Comprueba que el archivo está disponible y carga los países
            if not _countries_path.exists():
                raise FileNotFoundError(
                    f"No se ha encontrado el archivo de países {_countries_path!r}"
                )
            with open(_countries_path) as file:
                reader = csv.reader(file)
                next(reader)  # Salta la cabecera
                countries.extend(reader)
            if verbose:
                print(">>> Usando archivo de países", _countries_path)
        if verbose:
            print(f">>> Se consultarán mercados de {len(countries)} países")

        # Ejecutamos el scraping, 'loops' veces, esperando 'wait' minutos
        wait = max(wait, 5.0)
        results = []
        for i in range(loops):
            if verbose:
                print(f"\n>>> Iteración {i + 1} de {loops} ({(i+1)/loops:.0%})")
            # Iniciamos el contador de tiempo
            tstart = perf_counter()
            timestamp = time()
            # Por cada país, realizamos el scraping
            for j, (continent, country, url_token) in enumerate(countries, start=1):
                url = STOCKS_URL.format(token=url_token)
                if verbose:
                    print(f">>> [{j:02}/{len(countries)}] Consultando {url!r}")
                for row in self._url_scrape(url):
                    results.append((timestamp, continent, country, *row))
                if verbose:
                    print(
                        f">>>  \\ {len(results)} filas totales (última: {results[-1]})"
                    )
            print(f">>> Iteración finalizada en {perf_counter()-tstart:.2f} segundos")
            # Si quedan iteraciones, esperamos 'wait' minutos
            if i < loops - 1:
                if verbose:
                    print(f">>> Esperando {wait} minutos...")
                sleep(wait * 60)

        # Guardamos los resultados en un CSV
        if output_dir:
            output_dir = Path(output_dir)
            if not output_dir.exists():
                raise FileNotFoundError(
                    f"No se ha encontrado el directorio {output_dir!r}"
                )
            if not output_dir.is_dir():
                raise NotADirectoryError(f"{output_dir!r} no es un directorio válido")
        else:
            output_dir = Path.cwd()
        with open(
            output_dir / "results.csv", "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(RESULTS_CSV_HEADER)
            writer.writerows(results)
        if verbose:
            print(f"\n>>> Resultados guardados en {output_dir / 'results.csv'}")
        return output_dir / "results.csv"

    # Privados

    def _setup_webdriver(self) -> WebDriver:
        """Configura el WebDriver de Selenium"""
        if not self._executable:
            service = ChromeDriverManager().install()
            options = Options()
            options.add_argument("--headless")
            return webdriver.Chrome(service=Service(service), options=options)
        else:
            if not Path(self._executable).exists():
                raise FileNotFoundError(
                    f"No se ha encontrado el ejecutable del WebDriver en {self._executable!r}"
                )
            options = Options()
            options.add_argument("--headless")
            return webdriver.Chrome(executable_path=self._executable, options=options)

    def _url_scrape(self, url: str) -> tuple[tuple]:
        """Realiza el scraping de una URL de mercado de valores

        Utiliza BeautifulSoup para analizar el HTML de la página.

        Devuelve una matriz con los resultados de las acciones del país en el
        instante de tiempo.

        """
        res = requests.get(url)
        if res.status_code == 200:
            soup = BeautifulSoup(res.text, "html.parser")
        table = soup.find_all("table")[0]
        rows = table.find_all("tr")
        data = []
        for row in rows[1:]:
            cells = row.find_all("td")
            # Símbolo y nombre de la acción
            symbol = cells[TD_IDX_STOCK_NAME].find("a").text
            name = cells[TD_IDX_STOCK_NAME].find("sup").text
            # Precio y moneda de la acción
            price_raw, currency = cells[TD_IDX_STOCK_PRICE].text.split()
            price = float(price_raw.replace(",", ""))
            # Volumen de la acción
            volume = q_normalize(cells[TD_IDX_STOCK_VOLUME].text)
            # Capitalización de mercado
            market_cap_raw, *_ = cells[TD_IDX_MARKET_CAP].text.split()
            try:
                market_cap = q_normalize(market_cap_raw)
            except ValueError:
                # ERROR: El valor es nulo, habrá que manejarlo en el futuro
                market_cap = None
            # Sector/es
            sector = cells[TD_IDX_SECTOR].text
            # Almacenar datos
            data.append((symbol, name, price, currency, volume, market_cap, sector))
        return tuple(data)
