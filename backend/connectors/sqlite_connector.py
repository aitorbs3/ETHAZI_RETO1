import sqlite3
import os
from pathlib import Path


def get_sqlite_connection():
    # Obtiene la ruta desde el entorno o la ruta local por defecto
    ruta_db = os.getenv(
        "SQLITE_DATABASE",
        "./backend/database/sqlite_reto.db"
    )

    # Crea la carpeta contenedora si no existe
    path_db = Path(ruta_db)
    path_db.parent.mkdir(parents=True, exist_ok=True)

    conn = sqlite3.connect(ruta_db)

    # Permite acceder a las columnas por nombre
    conn.row_factory = sqlite3.Row

    return conn


def init_sqlite_db():
    """
    Crea la tabla de caché SQLite con la estructura
    correspondiente al modelo Student.
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
        cursor = conn.cursor()
        cursor.execute(query)
        conn.commit()