import oracledb


from utils.config import obtener_variable
from connectors.base import BaseConnector


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
    Utiliza los métodos comunes de BaseConnector,
    adaptando la búsqueda por nombre a Oracle.
    """

    def _connect(self):
        return conectar_oracle()

    def get_student(self, name: str) -> list:
        """
        Busca estudiantes por nombre en Oracle.
        Permite coincidencias parciales.
        """

        connection = self._connect()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    id,
                    nombre,
                    casa,
                    especie,
                    genero,
                    nacimiento,
                    nacionalidad,
                    patronus,
                    imagen
                FROM alumnos
                WHERE LOWER(nombre) LIKE LOWER(:nombre)
            """, {"nombre": f"%{name}%"})

            rows = cursor.fetchall()

            return [
                self.row_to_student(row)
                for row in rows
            ]

        finally:
            connection.close()