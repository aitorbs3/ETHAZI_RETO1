import os
import sqlite3
from pathlib import Path

from connectors.base_crud import BaseCRUDConnector


def get_sqlite_connection():
    """
    Obtiene una conexión a SQLite usando la ruta configurada
    en SQLITE_DATABASE o la ruta predeterminada.
    """

    ruta_db = os.getenv(
        "SQLITE_DATABASE",
        "./data/databases/sqlite_reto.db"
    )

    path_db = Path(ruta_db)

    if not path_db.is_absolute():
        base_dir = Path(__file__).resolve().parents[2]
        path_db = base_dir / path_db

    path_db.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(path_db)
    conn.row_factory = sqlite3.Row

    return conn


def get_sqlite_connection_legacy():
    """
    Alias de compatibilidad para el nombre de conexión anterior.
    """
    return get_sqlite_connection()



def init_sqlite_db():
    """
    Inicializa las tablas necesarias para SQLite.

    cache_students:
        Caché de las cuatro bases históricas.

    alumnos:
        Alumnos nuevos gestionados localmente.

    pending_operations:
        Operaciones pendientes de sincronizar
        con MariaDB.

    No elimina datos existentes.
    """

    conn = get_sqlite_connection()

    try:
        with conn:

            # Caché de alumnos históricos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS cache_students (
                    id TEXT PRIMARY KEY NOT NULL,
                    nombre TEXT NOT NULL,
                    casa TEXT,
                    especie TEXT,
                    genero TEXT,
                    nacimiento TEXT,
                    nacionalidad TEXT,
                    patronus TEXT,
                    imagen TEXT
                )
            """)

            # Alumnos nuevos
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alumnos (
                    id TEXT PRIMARY KEY NOT NULL,
                    nombre TEXT NOT NULL,
                    casa TEXT,
                    especie TEXT,
                    genero TEXT,
                    nacimiento TEXT,
                    nacionalidad TEXT,
                    patronus TEXT,
                    imagen TEXT
                )
            """)

            # Cola de sincronización con MariaDB
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    nombre TEXT,
                    nombre_editado TEXT,
                    payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            """)

    finally:
        conn.close()



class SQLiteConnector(BaseCRUDConnector):
    """
    Conector SQLite con lectura heredada de BaseConnector
    y operaciones CRUD heredadas de BaseCRUDConnector.
    """

    TABLE_NAME = "alumnos"

    @property
    def placeholder(self) -> str:
        return "?"

    def _connect(self):
        return get_sqlite_connection()