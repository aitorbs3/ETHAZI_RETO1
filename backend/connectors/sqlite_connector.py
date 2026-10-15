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
    Crea automáticamente las tablas SQLite necesarias.
    Actualiza las columnas de sincronización si faltan.
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

            # Alumnos nuevos de Hogwarths
            conn.execute("""
                CREATE TABLE IF NOT EXISTS alumnos (
                    id TEXT PRIMARY KEY NOT NULL,
                    nombre TEXT NOT NULL,
                    casa TEXT NOT NULL,
                    especie TEXT,
                    genero TEXT,
                    nacimiento TEXT,
                    nacionalidad TEXT,
                    patronus TEXT,
                    imagen TEXT
                )
            """)

            # Operaciones pendientes
            conn.execute("""
                CREATE TABLE IF NOT EXISTS pending_operations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    operation TEXT NOT NULL,
                    student_id TEXT NOT NULL,
                    nombre TEXT,
                    nombre_editado TEXT,
                    payload TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                    attempts INTEGER NOT NULL DEFAULT 0,
                    last_error TEXT
                )
            """)

            # Migración automática para bases antiguas
            columnas = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(pending_operations)"
                )
            }

            if "attempts" not in columnas:
                conn.execute("""
                    ALTER TABLE pending_operations
                    ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0
                """)

            if "last_error" not in columnas:
                conn.execute("""
                    ALTER TABLE pending_operations
                    ADD COLUMN last_error TEXT
                """)

        print("SQLite inicializada correctamente.")

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