from pathlib import Path

import jaydebeapi

from backend.utils.config import obtener_variable


def conectar_derby():
    """
    Crea una conexión con la base de datos Apache Derby configurada.

    Returns:
        Connection: conexión activa con Apache Derby.
    """

    backend_dir = Path(__file__).resolve().parent.parent
    drivers_dir = backend_dir / "drivers" / "derby"

    derby_database = obtener_variable("DERBY_DATABASE")

    jars = [
        str(drivers_dir / "derby.jar"),
        str(drivers_dir / "derbyshared.jar"),
        str(drivers_dir / "derbytools.jar"),
    ]

    driver = "org.apache.derby.jdbc.EmbeddedDriver"
    url = f"jdbc:derby:{derby_database}"

    return jaydebeapi.connect(
        driver,
        url,
        [],
        jars,
    )