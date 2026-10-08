import oracledb


from backend.utils.config import obtener_variable
from backend.connectors.base import BaseConnector


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

class OracleConnector(BaseConnector):
    """
    Conector de Oracle.

    Utiliza los métodos de lectura definidos en BaseConnector.
    """

    def _connect(self):
        """
        Utiliza la función de conexión de Oracle existente.
        """

        return conectar_oracle()