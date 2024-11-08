# 08/11/2024
"""Funciones de ayuda para StockScraper."""

from pathlib import Path


def check_path(
    path: str | Path, *, is_dir: bool = False, raises: bool = False
) -> Path | None:
    """Comprueba si la ruta existe

    Si 'is_dir' es True, comprueba también si la ruta es un directorio.

    Si la ruta no existe, o no se cumple alguna de las demás condiciones,
    por defecto se devuelve None. Si 'raises' es True, en vez de ello, se
    lanza una excepción adecuada. Por otro lado, si todos los criterios se
    cumplen, se devuelve la ruta como un objeto de tipo Path.

    """
    path = Path(path)
    if not path.exists():
        if raises:
            raise FileNotFoundError(f"No se encontró la ruta: {path}")
        return None
    if is_dir and not path.is_dir():
        if raises:
            raise NotADirectoryError(f"No es un directorio: {path}")
        return None
    return path


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
    svalue = svalue.replace(",", "")  # Eliminar comas de los miles
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


class _VerbosePrinter:
    """Clase auxiliar para imprimir mensajes sólo en modo 'verbose'

    Define un único objeto 'vprint' que se debe utilizar para imprimir de
    forma equivalente a 'print', pero sólo lo hará si se configuró previamente
    'vprint.verbose = True' o 'vprint.set()'.

    """

    def __init__(self) -> None:
        self.verbose = False

    def set(self, verbose: bool = True) -> None:
        self.verbose = verbose

    def __call__(self, *args, **kwargs) -> None:
        if self.verbose:
            print(*args, **kwargs)


vprint = _VerbosePrinter()
