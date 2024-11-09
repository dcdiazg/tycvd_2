# StocksScraper
## Práctica de Tipología y Ciclo de Vida de los Datos
### *Diana Carolina Díaz Gordillo, Ángel Moreno Prieto*

## Objetivo
El objetivo de esta práctica es desarrollar un programa en el que se ponga el práctica procesos de webscraping.

Nuestra propuesta consiste en utilizar webscraping para **obtener datos en tiempo real del estado de diferentes mercados financieros**, centrándonos en acciones de diferentes países. Idealmente, nuestra herramienta de webscraping se ejecutaría de forma automatizada cada X tiempo (por ejemplo, 5 minutos), generando así un **histórico de datos sobre el que testear algoritmos de predicción** de evolución de mercado.

## Consideraciones
Este proyecto ha sido desarrollado en Python 3.12, y es compatible con cualquier versión
superior a ésta. Este proyecto está bajo licencia de uso libre del MIT. Cumple también
con los requisitos de uso legítimo de la [web utilizada](https://www.tradingview.com/):

```
User-agent: *
Disallow: /chat/m/
Disallow: /search/
Disallow: /idea-popup/
Disallow: /*mobileapp=true
Disallow: /*popup=true
Disallow: /*dark=false&popup=true
Disallow: /widgetembed/
Disallow: /embed-widget/
Disallow: /*?support
Disallow: /badbrowser/
Disallow: /accounts/
Sitemap: https://www.tradingview.com/sitemap.xml
```

## Instalación
### Poetry
Este proyecto utiliza [`poetry`](https://python-poetry.org/) como gestor de dependencias, a través de los archivos `pyproject.toml` y `poetry.lock`.

Una vez clonado el repositorio, se recomienda abrir una terminal y ejecutar:
```
    pip install poetry
    poetry install --no-root --without dev
```
De esta forma, se instalará `poetry`, y `poetry` gestionará todas las dependencias y los entornos virtuales.

Para ejecutar el programa, bastará entonces con realizar:
```
    poetry run python scrape.py [options]
```

### Pip
Si **no** se quiere o puede usar `poetry`, bastará con instalar las dependencias, una vez clonado el repositorio, mediante:
```
    pip install -r requirements.txt
```
Y ejecutar el programa de la forma usual:
```
    python scrape.py [options]
```

## Uso
Se puede ejecutar el programa a través del script `scrape.py`.

El programa requiere para funcionar un archivo de países, `countries.csv`, en
el que se indica información relevante de los países cuyos mercados se quieren
consultar. Este archivo es creado por el propio programa, y es configurable.
Por defecto, usará el archivo que halle en la carpeta `data/`; o creará uno
desde 0 incluyendo a todos los países disponibles en la web, si no encuentra
ningún archivo.

A su vez, el programa genera un archivo de resultados, `results.csv`, con todos
los datos obtenidos de la web mediante *scraping*. Por defecto, se almacenará
en la carpeta `data/`, pero se puede configurar.

Finalmente, por defecto el programa realizará una sola consulta a la web, para
los países escogidos. Este comportamiento puede modificarse con la opción `-l`.

Las opciones disponibles son:

#### `-c / --countries <ruta-a-archivo-de-países>`

Para indicar una ruta al archivo de países alternativo que se desee usar.

Si se incluye la opción, pero no se indica ninguna ruta, se lanzará una ventana
con todos los países disponibles, para que el usuario escoja interactivamente
aquéllos en los que esté interesado.

Se proporciona la opción alternativa `-a / --all-countries`, que sobrescribe
la opción `-c`, y garantiza que se cree un archivo nuevo en el que se incluyan
todos los países disponibles.

#### `-o / --output <ruta-a-la-carpeta-de-salida>`

Para indicar una ruta a la carpeta en la que se quiere que se almacene el
archivo CSV de salida (de nombre `results.csv`). Por defecto, se guardará en
este directorio de trabajo, en la carpeta `data/`.

#### `-l / --loops <numer-de-bucles>` y `-w / --wait <minutos>`

Permiten ajustar la cantidad de veces que se consulta la web, y el intervalo de
tiempo a esperar entre consulta y consulta. Nótese que el intervalo mínimo de
espera es de 3 minutos, para garantizar un uso ético de la web.

#### `-v / --verbose` y `-q / --quiet`

Por defecto, durante la ejecución se muestran diferentes mensajes informativos
sobre el avance del programa en cada fase. Si se quieren mostrar aun más
mensajes, se puede usar la opción `-v`. Por el contrario, si **no** se quiere
mostrar ningún mensaje, se debe usar la opción `-q`.

