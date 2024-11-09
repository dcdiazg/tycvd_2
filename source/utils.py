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
            raise FileNotFoundError(f"La ruta requerida {path} no existe")
        return None
    if is_dir and not path.is_dir():
        if raises:
            raise NotADirectoryError(f"La ruta requerida {path} debe ser un directorio")
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


class VerbosePrinter:
    """Clase para imprimir mensajes en función de los diferentes niveles
    de verbosidad.

    Define tres niveles:
    - 0: No imprime nada
    - 1: Imprime sólo mensajes INFO
    - 2: Imprime mensajes INFO y DEBUG

    Para imprimir, se definen los métodos 'info' y 'debug', que pueden
    recibir los mismos argumentos que un 'print' normal; pero sólo funcionarán
    si el nivel de verbosidad es suficiente.

    El constructor recibe el nivel de verbosidad inicial, que por defecto es 1.
    Se puede cambiar sobre la marcha con el método 'set'.

    """

    def __init__(self, mode: int = 1) -> None:
        self._mode = mode

    def set(self, mode: int) -> None:
        """Cambia el nivel de verbosidad"""
        self._mode = mode

    def info(self, *args, **kwargs) -> None:
        """Imprime un mensaje INFO"""
        if self._mode >= 1:
            print(*args, **kwargs)

    def debug(self, *args, **kwargs) -> None:
        """Imprime un mensaje DEBUG"""
        if self._mode >= 2:
            print(*args, **kwargs)

    def __call__(self, *args, **kwargs) -> None:
        """Permite llamar a la instancia directamente para imprimir mensajes INFO"""
        return self.info(*args, **kwargs)
