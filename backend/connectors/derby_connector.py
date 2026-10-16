from pathlib import Path

import jaydebeapi

from utils.config import obtener_variable
from connectors.base import BaseConnector
from utils.jvm import iniciar_jvm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]


def conectar_derby(crear=False):
    """Conecta con Derby incrustado; crear=True solo en la carga inicial."""
    ruta = Path(obtener_variable("DERBY_DATABASE"))
    if not ruta.is_absolute():
        ruta = PROJECT_ROOT / ruta
    ruta.parent.mkdir(parents=True, exist_ok=True)

    drivers = BACKEND_DIR / "drivers" / "derby"
    jars = [str(drivers / nombre) for nombre in (
        "derby.jar", "derbyshared.jar", "derbytools.jar"
    )]
    for archivo in jars:
        if not Path(archivo).is_file():
            raise FileNotFoundError(f"Driver Derby no encontrado: {archivo}")

    iniciar_jvm()
    url = f"jdbc:derby:{ruta}" + (";create=true" if crear else "")
    return jaydebeapi.connect(
        "org.apache.derby.jdbc.EmbeddedDriver", url, [], jars,
    )


class DerbyConnector(BaseConnector):
    """Solo lectura para los alumnos históricos de Gryffindor."""

    def _connect(self):
        return conectar_derby()
