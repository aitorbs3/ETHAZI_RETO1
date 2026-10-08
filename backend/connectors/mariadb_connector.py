import pymysql

from backend.utils.config import obtener_variable


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