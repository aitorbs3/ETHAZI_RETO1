import pymysql
from connectors.base_crud import BaseCRUDConnector
from utils.config import obtener_variable


def conectar_mariadb():
    """
    Crea y devuelve una conexión con la base de datos central MariaDB.
    """

    return pymysql.connect(
        host=obtener_variable("MARIADB_HOST"),
        port=int(obtener_variable("MARIADB_PORT")),
        user=obtener_variable("MARIADB_USER"),
        password=obtener_variable("MARIADB_PASSWORD"),
        database=obtener_variable("MARIADB_DATABASE"),
        charset="utf8mb4",
    )

class MariaDBConnector(BaseCRUDConnector):

    @property
    def placeholder(self):
        return "%s"

    def _connect(self):
        return conectar_mariadb()


def init_mariadb_db():
    """
    Crea automáticamente la tabla de alumnos en MariaDB.
    No elimina los registros existentes.
    """

    connection = conectar_mariadb()

    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alumnos (
                    id VARCHAR(36) PRIMARY KEY,
                    nombre VARCHAR(150) NOT NULL,
                    casa VARCHAR(50) NOT NULL,
                    especie VARCHAR(100) NULL,
                    genero VARCHAR(50) NULL,
                    nacimiento DATE NULL,
                    nacionalidad VARCHAR(150) NULL,
                    patronus VARCHAR(150) NULL,
                    imagen TEXT NULL
                ) ENGINE=InnoDB
                DEFAULT CHARSET=utf8mb4
            """)

        connection.commit()
        print("MariaDB inicializada correctamente.")

    except Exception:
        connection.rollback()
        raise

    finally:
        connection.close()
