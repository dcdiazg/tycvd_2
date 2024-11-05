# Práctica de Tipología y Ciclo de Vida de los datos
## Diana Carolina Díaz Gordillo, Ángel Moreno Prieto
### Objetivo
El objetivo de esta práctica es desarrollar un programa en el que se ponga el práctica procesos de webscraping.

Nuestra propuesta consiste en utilizar webscraping para **obtener datos en tiempo real del estado de diferentes mercados financieros**, centrándonos en acciones de diferentes países. Idealmente, nuestra herramienta de webscraping se ejecutaría de forma automatizada cada X tiempo (por ejemplo, 5 minutos), generando así un **histórico de datos sobre el que testear algoritmos de predicción** de evolución de mercado.

### Consideraciones
#### Versión de Python
Este proyecto ha sido desarrollado en Python 3.12, y debería ser compatible también con cualquier versión superior a ésta.

#### Poetry
Este proyecto utiliza [`poetry`](https://python-poetry.org/) como gestor de dependencias, a través del archivo `pyproject.toml` y `poetry.lock`.
Una vez clonado el repositorio, se recomienda abrir una terminal y ejecutar:
```
    pip install poetry
    poetry install --no-root
```
De esta forma, se instalará `poetry`, y `poetry` gestionará todas las dependencias y los entornos virtuales.
Para ejecutar el programa, bastará entonces con realizar:
```
    poetry run python scraper.py
```

Si no se quiere usar `poetry`, bastará con instalar las dependencias mediante `pip ...`
