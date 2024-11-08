# 08/11/2024
"""Cliente de línea de comandos para StockScraper."""

import argparse

from source import StockScraper


def setup() -> argparse.ArgumentParser:
    """Setup de los comandos válidos

    -v --verbose
    -c --countries <path-to-countries-csv>
    -o --output <path-to-dir-where-to-put-the-output-csv>
    -l --loops <loops-to-make>
    -w --wait <time-to-wait-in-minutes>
    --testing <ignore-else-and-test>

    Devuelve el parser configurado con los argumentos anteriores.

    """
    parser = argparse.ArgumentParser(
        description="Cliente de línea de comandos para StockScraper"
    )
    # -v --verbose
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="Muestra información detallada durante la ejecución",
    )
    # -c --countries
    parser.add_argument(
        "-c",
        "--countries",
        type=str,
        default="",
        help="Ruta al archivo CSV con los países de los que extraer datos",
    )
    # -o --output
    parser.add_argument(
        "-o",
        "--output",
        type=str,
        help="Ruta al directorio donde guardar el archivos CSV de salida ('results.csv')",
    )
    # -l --loops
    parser.add_argument(
        "-l",
        "--loops",
        type=int,
        default=1,
        help="Número de iteraciones a realizar",
    )
    # -w --wait
    parser.add_argument(
        "-w",
        "--wait",
        type=int,
        default=0,
        help="Tiempo de espera entre iteraciones en minutos",
    )
    # --testing
    parser.add_argument(
        "--testing",
        action="store_true",
        help="Ignora el resto de argumentos y ejecuta el scraper en modo testing",
    )

    return parser


def run() -> None:
    """Función principal del cliente de línea de comandos"""
    parser = setup()
    args = parser.parse_args()

    if args.testing:
        scraper = StockScraper()
        scraper.scrape("testing", verbose=True)
    else:
        scraper = StockScraper()
        scraper.scrape(
            args.countries,
            loops=args.loops,
            wait=args.wait,
            output_dir=args.output,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    run()
