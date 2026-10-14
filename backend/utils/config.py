import os
from pathlib import Path

from dotenv import load_dotenv


ROOT_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = ROOT_DIR / ".env"

load_dotenv(ENV_FILE)


def obtener_variable(nombre: str, obligatoria: bool = True) -> str | None:
    """
    Obtiene una variable de entorno.

    Args:
        nombre: Nombre de la variable.
        obligatoria: Indica si la variable debe existir.

    Returns:
        Valor de la variable o None.

    Raises:
        RuntimeError: Si la variable es obligatoria y no existe.
    """
    valor = os.getenv(nombre)

    if obligatoria and not valor:
        raise RuntimeError(
            f"La variable de entorno '{nombre}' no está configurada."
        )

    return valor