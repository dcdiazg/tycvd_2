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
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webdriver import WebDriver
from webdriver_manager.chrome import ChromeDriverManager

from source.countries_selector_wizard import CountriesSelector
from source.utils import VerbosePrinter, check_path, q_normalize

ScrapedRow = tuple[str, str, float, str, float, float | None, str | None]

DEFAULT_DATA_DIR = Path(__file__).parent.parent / "data"

COUNTRIES_CSV_HEADERS = ["Continent", "Country", "URLToken"]
RESULTS_CSV_HEADER = [
    "Timestamp",
    "Region",
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

T_MIN_WAIT = 3.0

VERBOSE_SILENT = 0
VERBOSE_NORMAL = 1
VERBOSE_DEBUG = 2


class StockScraper:
    """Realiza webscraping de datos de acciones de bolsas de valores

    El constructor argumento opcional la ruta a un ejecutable de ChromeDriver,
    para cuando se use Selenium. Por defecto, lo descargará automáticamente
    mediante 'webdriver_manager'. También se puede especificar el nivel de
    verbosidad de los mensajes de salida. Un nivel 0 desactiva todos, un nivel
    1 (por defecto) muestra mensajes informativos, y un nivel 2 muestra
    mensajes de depuración.

    """

    def __init__(
        self,
        selenium_webdriver_executable: Path | str = "",
        *,
        verbose_mode: int = VERBOSE_NORMAL,
    ) -> None:
        self._executable = selenium_webdriver_executable
        self._verbose = verbose_mode
        DEFAULT_DATA_DIR.mkdir(exist_ok=True)

    # Público

    def choose_countries(
        self,
        *,
        all: bool = False,
        output_dir: str | Path | None = None,
    ) -> None:
        """Permite escoger los países de cuyos mercados se desean obtener
        datos.

        Por defecto, carga todos los países disponibles en la web, y le muestra
        al usuario una interfaz sencilla donde seleccionar o deseleccionar sus
        preferencias. Alternativamente, si se llama con 'all=True', se
        garantiza que todos los países posible serán seleccionados.

        En última instancia, genera un archivo CSV ('countries.csv') en el que
        se indican los países seleccionados junto con la URL de sus mercados.
        Por defecto, se almacena en la carpeta 'data' del directorio de
        trabajo, pero se puede modificar la ruta de salida con el argumento
        'output_dir'.

        No se devuelve ningún valor.

        """
        vprint = VerbosePrinter(self._verbose)

        countries = []
        # Setup del WebDriver, modo silencioso
        driver = self._setup_webdriver()
        vprint.debug("WebDriver correctamente configurado")
        # Cargamos la web
        vprint.info("Cargando todos los países disponibles...")
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
                vprint.debug(f"{continent} | {country} | {token}")
        # Cerrar el WebDriver
        driver.quit()
        # Si indicamos que NO queremos todos los países, mostrar interfaz
        if not all:
            vprint.debug("Mostrando interfaz para seleccionar países...")
            app = CountriesSelector(countries)
            app.mainloop()
            countries = [
                (continent, country, token)
                for (continent, country, token), var in app.check_vars.items()
                if var.get()
            ]
        # Si se indica un 'output_dir', comprobamos que existe Y es un directorio
        if output_dir:
            output_dir = check_path(output_dir, is_dir=True, raises=True)
        else:
            output_dir = DEFAULT_DATA_DIR
        # Guardamos como CSV
        with open(output_dir / "countries.csv", "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(COUNTRIES_CSV_HEADERS)
            writer.writerows(countries)
        vprint.info(
            f"Nueva selección de países guardada en {output_dir / 'countries.csv'}"
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
        cadena vacía, tratará de ubicar el archivo 'countries.csv' en la
        carpeta 'data' del directorio de trabajo, y si no existe, generará uno
        mediante 'choose_countries(all=True)'. Si 'countries' vale 'testing',
        se usará únicamente el stock de EEUU, a modo de prueba. En caso
        contrario, 'countries' debe ser la ruta al archivo CSV con los países y
        las URLs de sus mercados, generadas previamente mediante
        'choose_countries()'.

        'loops' indica el número de veces que se realizará el scraping,
        esperando 'wait' minutos entre cada iteración (mínimo, 3, para respetar
        la política de uso de la web).

        'output_dir' debe ser la ruta al directorio donde se guardarán los
        resultados en formato CSV, 'results.csv'. Si no se indica nada, se
        guardará en el la carepta 'data' del directorio de trabajo.

        'verbose' indica si se mostrarán mensajes informativos durante la
        ejecución.

        Devuelve la ruta al archivo CSV con los datos de las acciones de los
        países seleccionados, y el instante en el que fueron descargados.

        """
        vprint = VerbosePrinter(self._verbose)

        # Comprobamos 'countries' y generamos la lista de países
        if countries == "testing":
            countries = [TESTING_COUNTRY]
            vprint.info("Modo prueba activado, sólo se consultará el mercado de EEUU")
        else:
            if not countries:
                # Busca primero en el directorio de trabajo actual
                if not check_path(DEFAULT_DATA_DIR / "countries.csv"):
                    # Si no existe, se generan los países desde 0
                    vprint.info("No existe archivo de países, generando uno nuevo...")
                    self.choose_countries(all=True)
                countries_path = DEFAULT_DATA_DIR / "countries.csv"
            else:
                countries_path = Path(countries)
            # Si sí se indica un path, se comprueba que exista
            countries_path = check_path(countries_path, raises=True)
            vprint.info("Usando archivo de países", countries_path)
            # Y, finalmente, se carga la lista de países
            countries = []
            with open(countries_path) as file:
                reader = csv.reader(file)
                next(reader)  # Salta la cabecera
                countries.extend(reader)
        n_countries = len(countries)
        vprint.info(f"Se consultarán mercados de {n_countries} países")

        # Comprobamos que la carpeta de salida exista
        if output_dir:
            output_dir = check_path(output_dir, is_dir=True, raises=True)
        else:
            output_dir = DEFAULT_DATA_DIR

        # Ejecutamos el scraping, 'loops' veces, esperando 'wait' minutos
        wait = max(wait, T_MIN_WAIT)
        results = []
        for i in range(loops):
            vprint.info(f"\nIteración {i + 1} de {loops} ({i/loops:.0%})")
            # Iniciamos el contador de tiempo
            tstart = perf_counter()
            timestamp = time()
            # Por cada país, realizamos el scraping
            for j, (continent, country, url_token) in enumerate(countries, start=1):
                url = STOCKS_URL.format(token=url_token)
                _p = (j - 1) / n_countries
                vprint.info(
                    f"| {_p: >6.2%}  {j:02}/{n_countries}  -  Consultando {url!r}"
                )
                for row in self._url_scrape(url):
                    results.append((timestamp, continent, country, *row))
                vprint.debug(f"+ {len(results)} filas totales (última: {results[-1]})")
            vprint.info(
                f"Iteración {i + 1} finalizada en {perf_counter()-tstart:.2f} segundos"
            )
            # Si quedan iteraciones, esperamos 'wait' minutos
            if i < loops - 1:
                vprint.info(f"Esperando {wait} minutos a la siguiente iteración...")
                sleep(wait * 60)

        # Guardamos los resultados en un CSV
        with open(
            output_dir / "results.csv", "w", newline="", encoding="utf-8"
        ) as file:
            writer = csv.writer(file)
            writer.writerow(RESULTS_CSV_HEADER)
            writer.writerows(results)
        vprint.info(f"\nResultados guardados en {output_dir / 'results.csv'}")
        return output_dir / "results.csv"

    # Privados

    def _setup_webdriver(self) -> WebDriver:
        """Configura el WebDriver de Selenium"""
        if not self._executable:
            service = ChromeDriverManager().install()
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--log-level=3")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            return webdriver.Chrome(service=Service(service), options=options)
        else:
            if not Path(self._executable).exists():
                raise FileNotFoundError(
                    f"No se ha encontrado el ejecutable del WebDriver en {self._executable!r}"
                )
            options = webdriver.ChromeOptions()
            options.add_argument("--headless=new")
            options.add_argument("--log-level=3")
            options.add_experimental_option("excludeSwitches", ["enable-logging"])
            return webdriver.Chrome(executable_path=self._executable, options=options)

    def _url_scrape(self, url: str) -> list[ScrapedRow]:
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
            market_cap_raw = "".join(cells[TD_IDX_MARKET_CAP].text.split()[:-1])
            if not market_cap_raw:
                market_cap = None
            else:
                market_cap = q_normalize(market_cap_raw)
            # Sector/es
            sector = cells[TD_IDX_SECTOR].text
            sector = sector if sector != "—" else None
            # Almacenar datos
            data.append(
                (
                    symbol,
                    name,
                    round(price, 6),
                    currency,
                    round(volume, 6),
                    round(market_cap, 6) if market_cap else market_cap,
                    sector,
                )
            )
        return data
