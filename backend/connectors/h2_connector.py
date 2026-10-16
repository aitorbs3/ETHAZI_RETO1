from pathlib import Path

import jaydebeapi

from utils.config import obtener_variable
from connectors.base import BaseConnector
from utils.jvm import iniciar_jvm

PROJECT_ROOT = Path(__file__).resolve().parents[2]
BACKEND_DIR = Path(__file__).resolve().parents[1]
H2_JAR = BACKEND_DIR / "drivers" / "h2" / "h2.jar"


def obtener_conexion_h2():
    ruta = Path(obtener_variable("H2_DATABASE"))
    if not ruta.is_absolute():
        ruta = PROJECT_ROOT / ruta
    ruta.parent.mkdir(parents=True, exist_ok=True)

    if not H2_JAR.is_file():
        raise FileNotFoundError(f"Driver H2 no encontrado: {H2_JAR}")

    iniciar_jvm()
    return jaydebeapi.connect(
        "org.h2.Driver",
        f"jdbc:h2:{ruta};AUTO_SERVER=TRUE;DB_CLOSE_DELAY=-1",
        [obtener_variable("H2_USER", obligatoria=False) or "sa",
         obtener_variable("H2_PASSWORD", obligatoria=False) or ""],
        str(H2_JAR),
    )


class H2Connector(BaseConnector):
    """Solo lectura para los alumnos históricos de Hufflepuff."""

    def _connect(self):
        return obtener_conexion_h2()
