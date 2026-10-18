"""Carga y valida la configuración del backend desde variables de entorno."""

# Importar os para acceder a las variables de entorno del sistema.
import os

# Importar Path para trabajar con rutas de archivos y directorios
# de forma independiente del sistema operativo.
from pathlib import Path

# Importar load_dotenv para cargar las variables definidas en un archivo .env.
from dotenv import load_dotenv


# Obtener la ruta absoluta del directorio raíz del proyecto.
# __file__ representa la ruta de este archivo Python.
# resolve() convierte la ruta en una ruta absoluta.
# parents[2] sube dos niveles desde el directorio que contiene este archivo.
ROOT_DIR = Path(__file__).resolve().parents[2]

# Construir la ruta completa del archivo .env situado en la raíz del proyecto.
# El operador / de Path permite unir componentes de una ruta.
ENV_FILE = ROOT_DIR / ".env"

# Cargar las variables del archivo .env en el entorno del proceso.
# Al utilizar una ruta explícita, el archivo puede localizarse aunque
# el backend se inicie desde un directorio de trabajo diferente.
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

    # Leer el valor de la variable de entorno.
    # os.getenv() devuelve una cadena si la variable existe,
    # o None si no está definida.
    valor = os.getenv(nombre)

    # Si la variable es obligatoria y su valor está vacío o no existe,
    # lanzar una excepción para detectar el problema inmediatamente.
    # Esto evita errores posteriores más difíciles de diagnosticar,
    # por ejemplo, al intentar conectarse a una base de datos.
    if obligatoria and not valor:
        raise RuntimeError(
            f"La variable de entorno '{nombre}' no está configurada."
        )

    # Devolver el valor obtenido.
    # Si la variable es opcional y no existe, se devuelve None.
    return valor