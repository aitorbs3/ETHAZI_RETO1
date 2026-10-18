"""Conexión y operaciones de escritura sobre la base central MariaDB."""

# Importamos pymysql, la librería de Python estándar para conectar y ejecutar comandos SQL en MariaDB y MySQL.
import pymysql

# Importamos BaseCRUDConnector en lugar de BaseConnector, ya que MariaDB es la base central 
# del sistema y soporta operaciones completas de escritura (CRUD).
from connectors.base_crud import BaseCRUDConnector

# Importamos la utilidad centralizada para leer las variables de entorno de forma segura.
from utils.config import obtener_variable


def conectar_mariadb():
    """
    Crea y devuelve una conexión con la base de datos central MariaDB.
    """
    
    # La conexión utiliza exclusivamente la configuración externa del archivo .env a través de obtener_variable.
    # Indicamos el juego de caracteres utf8mb4 para garantizar la compatibilidad total con acentos y símbolos especiales.
    return pymysql.connect(
        host=obtener_variable("MARIADB_HOST"),
        port=int(obtener_variable("MARIADB_PORT")),
        user=obtener_variable("MARIADB_USER"),
        password=obtener_variable("MARIADB_PASSWORD"),
        database=obtener_variable("MARIADB_DATABASE"),
        charset="utf8mb4",
    )


class MariaDBConnector(BaseCRUDConnector):
    """
    Conector principal para MariaDB. 
    Heda de BaseCRUDConnector para implementar todas las operaciones de inserción, actualización, 
    borrado y consulta mediante PyMySQL.
    """

    @property
    def placeholder(self):
        """
        Devuelve el marcador que PyMySQL admite obligatoriamente en consultas parametrizadas.
        """
        # A diferencia de JDBC o SQLite que usan '?', PyMySQL requiere el marcador '%s' 
        # para todas las consultas parametrizadas, incluso para valores numéricos o booleanos.
        return "%s"

    def _connect(self):
        """
        Abre y devuelve una conexión física a la base de datos central.
        """
        # Toda la parametrización de red y credenciales se concentra en la función auxiliar conectar_mariadb.
        return conectar_mariadb()


def init_mariadb_db():
    """
    Crea automáticamente la tabla de alumnos en MariaDB si esta no existe previamente.
    Es una función idempotente: prepara instalaciones nuevas sin destruir los registros existentes.
    """
    
    # Abrimos una conexión directa para la inicialización del esquema de base de datos.
    connection = conectar_mariadb()

    try:
        # Usamos el cursor como gestor de contexto para asegurar una ejecución limpia.
        with connection.cursor() as cursor:
            # Sentencia DDL idempotente (CREATE TABLE IF NOT EXISTS) para la tabla central de alumnos.
            # Se especifica el motor InnoDB para garantizar transacciones ACID e integridad referencial,
            # junto con utf8mb4 como codificación predeterminada.
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

        # Confirmamos los cambios en la estructura de la base de datos (Commit).
        connection.commit()
        print("Base de datos MariaDB inicializada correctamente.")

    except Exception:
        # Si ocurre cualquier error durante la creación del esquema, revertimos la transacción 
        # para evitar dejar la base de datos en un estado inconsistente.
        connection.rollback()
        raise

    finally:
        # Nos aseguramos de cerrar siempre la conexión para liberar los recursos del servidor de base de datos.
        connection.close()