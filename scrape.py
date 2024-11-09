# 08/11/2024
"""Cliente de línea de comandos para StockScraper."""

import argparse

from source import StockScraper

USE_COUNTRIES_SELECTOR = "<<use_countries_selector>>"


def setup() -> argparse.ArgumentParser:
    """Setup de los comandos válidos

    -v --verbose
    -c --countries <path-to-countries-csv>
    -a --all-countries
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
    # Si no se proporciona, busca el del 'data' o genera uno
    # Si se proporciona sin argumento, abre el selector de países
    # Si se proporciona con argumento, usa el archivo CSV apuntado
    parser.add_argument(
        "-c",
        "--countries",
        nargs="?",
        type=str,
        const=USE_COUNTRIES_SELECTOR,
        default="",
        help="""
            Ruta al archivo CSV con los países de los que extraer datos
            Si no se proporciona, buscará el local, o generará uno nuevo con
            todos los países.
            Si se proporciona sin argumento, abrirá el selector de países.
        """,
    )
    # -a --all-countries
    parser.add_argument(
        "-a",
        "--all-countries",
        action="store_true",
        help="Fuerza a usar todos los países disponibles (ignora el archivo CSV)",
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
    scraper = StockScraper()

    if args.testing:
        scraper.scrape("testing", verbose=True)
    else:
        if args.all_countries:
            scraper.choose_countries(all=True, verbose=args.verbose)
            args.countries = ""
        elif args.countries == USE_COUNTRIES_SELECTOR:
            scraper.choose_countries(verbose=args.verbose)
            args.countries = ""  # Para que use el archivo generado

        scraper.scrape(
            args.countries,
            loops=args.loops,
            wait=args.wait,
            output_dir=args.output,
            verbose=args.verbose,
        )


if __name__ == "__main__":
    run()
