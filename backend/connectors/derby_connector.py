from pathlib import Path

import jaydebeapi

from utils.config import obtener_variable
from connectors.base import BaseConnector



ROOT_DIR = Path(__file__).resolve().parents[2]


def conectar_derby(crear=False):
    """
    Abre una conexión con Apache Derby.

    Args:
        crear: crea la base de datos si todavía no existe.
    """

    drivers_dir = ROOT_DIR / "backend" / "drivers" / "derby"

    ruta_bd = Path(obtener_variable("DERBY_DATABASE"))

    if not ruta_bd.is_absolute():
        ruta_bd = ROOT_DIR / ruta_bd

    jars = [
        str(drivers_dir / "derby.jar"),
        str(drivers_dir / "derbyshared.jar"),
        str(drivers_dir / "derbytools.jar"),
    ]

    url = f"jdbc:derby:{ruta_bd}"

    if crear:
        url += ";create=true"

    return jaydebeapi.connect(
        "org.apache.derby.jdbc.EmbeddedDriver",
        url,
        [],
        jars,
    )


class DerbyConnector(BaseConnector):
    """
    Conector de Apache Derby.

    Derby se utiliza como base de datos de origen
    y solamente permite operaciones de lectura.
    """

    def _connect(self):
        """
        Devuelve una conexión con Derby.
        """

        return conectar_derby() 