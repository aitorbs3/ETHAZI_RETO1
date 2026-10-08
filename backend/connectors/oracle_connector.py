import oracledb

from utils.config import obtener_variable


def conectar_oracle():
    """
    Crea y devuelve una conexión con la base de datos Oracle configurada.

    Returns:
        oracledb.Connection: conexión activa con Oracle.
    """

    host = obtener_variable("ORACLE_HOST")
    port = int(obtener_variable("ORACLE_PORT"))
    service_name = obtener_variable("ORACLE_SERVICE_NAME")
    user = obtener_variable("ORACLE_USER")
    password = obtener_variable("ORACLE_PASSWORD")

    dsn = oracledb.makedsn(
        host,
        port,
        service_name=service_name
    )

    return oracledb.connect(
        user=user,
        password=password,
        dsn=dsn
    )