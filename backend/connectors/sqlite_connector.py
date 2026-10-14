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
    Inicializa la tabla de caché existente.
    No elimina ni modifica sus datos.
    """

    query = """
        CREATE TABLE IF NOT EXISTS cache_students (
            id VARCHAR(50) PRIMARY KEY,
            nombre VARCHAR(100) NOT NULL,
            casa VARCHAR(50) NOT NULL,
            especie VARCHAR(50) NOT NULL,
            genero VARCHAR(50) NOT NULL,
            nacimiento DATE,
            nacionalidad VARCHAR(50) NOT NULL,
            patronus VARCHAR(100),
            imagen TEXT
        );
    """

    with get_sqlite_connection() as conn:
        conn.execute(query)
        conn.commit()


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