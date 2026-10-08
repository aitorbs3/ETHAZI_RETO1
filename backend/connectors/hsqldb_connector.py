from pathlib import Path

import jaydebeapi

from utils.config import obtener_variable
from connectors.base import BaseConnector



def conectar_hsqldb():
    """
    Crea una conexión con la base de datos HSQLDB configurada.

    La conexión utiliza el driver JDBC de HSQLDB y el fichero JAR
    incluido dentro del proyecto.

    Returns:
        Connection: conexión activa con la base de datos HSQLDB.
    """

    # Obtenemos la carpeta backend del proyecto.
    backend_dir = Path(__file__).resolve().parent.parent

    # Localizamos la carpeta donde se encuentra el driver JDBC de HSQLDB.
    drivers_dir = backend_dir / "drivers" / "hsqldb"

    # Obtenemos desde el archivo .env la ubicación de la base de datos.
    hsqldb_database = obtener_variable("HSQLDB_DATABASE")

    # Indicamos el JAR que contiene el driver JDBC de HSQLDB.
    jars = [
        str(drivers_dir / "hsqldb.jar"),
    ]

    # Nombre de la clase del driver JDBC de HSQLDB.
    driver = "org.hsqldb.jdbc.JDBCDriver"

    # Construimos la URL JDBC utilizando la ruta configurada.
    url = f"jdbc:hsqldb:file:{hsqldb_database}\\database"

    # Creamos y devolvemos la conexión mediante JayDeBeApi.
    return jaydebeapi.connect(
        driver,
        url,
        ["SA", ""],
        jars,
    )


class HSQLDBConnector(BaseConnector):
    """
    Conector de HSQLDB.

    HSQLDB se utiliza como base de datos de origen
    y solamente permite operaciones de lectura.
    """

    def _connect(self):
        """
        Devuelve una conexión con HSQLDB.
        """

        return conectar_hsqldb()