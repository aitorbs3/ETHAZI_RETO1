import os
from pathlib import Path
import jaydebeapi
import jpype
from backend.utils.config import obtener_variable
from backend.connectors.base import BaseConnector

BASE_DIR = Path(__file__).resolve().parents[2]
H2_JAR = BASE_DIR / "backend" / "drivers" / "h2" / "h2.jar"
DRIVER_CLASS = "org.h2.Driver"

def obtener_conexion_h2():
    # Lee H2_DATABASE; si no existe en el .env, obtener_variable lanzará el RuntimeError automáticamente
    h2_db_path = obtener_variable("H2_DATABASE", obligatoria=True)
    
    # Construcción de la URL JDBC
    h2_url = f"jdbc:h2:{h2_db_path};AUTO_SERVER=TRUE;DB_CLOSE_DELAY=-1"
    usuario = obtener_variable("H2_USER", obligatoria=False) or "sa"
    password = obtener_variable("H2_PASSWORD", obligatoria=False) or ""

    if not H2_JAR.exists():
        raise FileNotFoundError(f"No se encontró el driver JDBC en: {H2_JAR}")

    try:
        if not jpype.isJVMStarted():
            jpype.startJVM(jpype.getDefaultJVMPath(), f"-Djava.class.path={H2_JAR}")

        return jaydebeapi.connect(
            DRIVER_CLASS,
            h2_url,
            [usuario, password],
            str(H2_JAR)
        )
    except Exception as e:
        print(f"Error al conectar con H2: {e}")
        raise e


class H2Connector(BaseConnector):
    """
    Conector de H2.

    Utiliza los métodos de lectura definidos en BaseConnector.
    """

    def _connect(self):
        """
        Utiliza la función de conexión de H2 existente.
        """

        return obtener_conexion_h2()

class H2Connector(BaseConnector):
    """
    Conector de H2.
    """

    def _connect(self):
        """
        Utiliza la función de conexión de H2 existente.
        """

        return obtener_conexion_h2()