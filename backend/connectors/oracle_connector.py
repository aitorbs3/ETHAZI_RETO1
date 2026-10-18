"""Conexión Oracle y adaptación de sus consultas de solo lectura."""

# Importamos oracledb, la librería oficial y moderna de Python para conectar con bases de datos Oracle.
import oracledb

# Importamos las herramientas de configuración del proyecto ETHAZI_RETO1 y la clase base de lectura.
from utils.config import obtener_variable
from connectors.base import BaseConnector


def conectar_oracle():
    """
    Crea y devuelve una conexión con la base de datos Oracle configurada.

    Returns:
        oracledb.Connection: conexión activa con Oracle.
    """

    # Construir el DSN (Data Source Name) por partes permite configurar de forma limpia 
    # el host, el puerto y el nombre de servicio de la base de datos desde las variables de entorno.
    host = obtener_variable("ORACLE_HOST")
    port = int(obtener_variable("ORACLE_PORT"))
    service_name = obtener_variable("ORACLE_SERVICE_NAME")
    user = obtener_variable("ORACLE_USER")
    password = obtener_variable("ORACLE_PASSWORD")

    # Generamos la cadena de conexión DSN requerida por el driver de Oracle.
    dsn = oracledb.makedsn(
        host,
        port,
        service_name=service_name
    )

    # Establecemos y devolvemos la conexión activa utilizando las credenciales y el DSN generado.
    return oracledb.connect(
        user=user,
        password=password,
        dsn=dsn
    )


class OracleConnector(BaseConnector):
    """
    Conector de Oracle enfocado en la lectura de datos históricos.
    Hereda de BaseConnector y sobrescribe el método de búsqueda por nombre 
    para adaptarlo a la sintaxis específica de Oracle.
    """

    def _connect(self):
        """Abre una conexión con Oracle usando la configuración del entorno."""
        
        # El helper centraliza la construcción del DSN y utiliza el driver oracledb.
        return conectar_oracle()

    def get_student(self, name: str) -> list:
        """
        Busca coincidencias parciales por nombre, sin distinguir mayúsculas,
        adaptado a las restricciones de sintaxis del motor Oracle.

        Args:
            name: Nombre o fragmento que se buscará.

        Returns:
            Alumnos que coinciden con el patrón indicado.
        """

        connection = self._connect()

        try:
            cursor = connection.cursor()

            # Oracle utiliza obligatoriamente parámetros con nombre (ej. :nombre), 
            # a diferencia de los drivers JDBC (?) o MariaDB (%s).
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

            # Se reutiliza el método estático de la clase base para homogeneizar 
            # el resultado y transformarlo en objetos de modelo Student válidos.
            return [
                self.row_to_student(row)
                for row in rows
            ]

        finally:
            # Nos aseguramos de cerrar siempre la conexión para liberar los recursos de Oracle.
            connection.close()