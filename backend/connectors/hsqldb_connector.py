from pathlib import Path

import jaydebeapi

from utils.config import obtener_variable
from connectors.base import BaseConnector
from utils.jvm import iniciar_jvm


PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]


def conectar_hsqldb():
    """Abre HSQLDB en Windows/Linux, siempre en <directorio>/slytherin."""
    carpeta = Path(obtener_variable("HSQLDB_DATABASE"))
    if not carpeta.is_absolute():
        carpeta = PROJECT_ROOT / carpeta
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_bd = carpeta / "slytherin"

    jar = BACKEND_DIR / "drivers" / "hsqldb" / "hsqldb.jar"
    if not jar.is_file():
        raise FileNotFoundError(f"Driver HSQLDB no encontrado: {jar}")
    iniciar_jvm()

    return jaydebeapi.connect(
        "org.hsqldb.jdbc.JDBCDriver",
        f"jdbc:hsqldb:file:{ruta_bd}",
        ["SA", ""],
        str(jar),
    )


class HSQLDBConnector(BaseConnector):
    """Solo lectura para los alumnos históricos de Slytherin."""

    def _connect(self):
        return conectar_hsqldb()
