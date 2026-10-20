"""Conexión y esquema local SQLite para datos y cola de sincronización."""

# Importamos os para interactuar con las variables de entorno del sistema operativo.
import os
# Importamos sqlite3, la librería estándar de Python para gestionar bases de datos SQLite locales.
import sqlite3
# Importamos Path de pathlib para gestionar rutas de archivos de manera robusta y multiplataforma.
from pathlib import Path

# Importamos la clase base CRUD para dotar a SQLite de capacidades completas de lectura y escritura.
from connectors.base_crud import BaseCRUDConnector


def get_sqlite_connection():
    """
    Obtiene una conexión a SQLite usando la ruta configurada
    en SQLITE_DATABASE o la ruta predeterminada.
    """

    # Obtenemos la ruta de la base de datos desde las variables de entorno (o usamos ./data/databases/sqlite_reto.db por defecto).
    # Esto permite personalizar la ubicación sin modificar el código de despliegue.
    ruta_db = os.getenv(
        "SQLITE_DATABASE",
        "./data/databases/sqlite_reto.db"
    )

    path_db = Path(ruta_db)

    # Si la ruta configurada no es absoluta, la resolvemos de forma relativa desde la raíz del proyecto,
    # garantizando que funcione de manera idéntica en Windows, Linux y contenedores Docker.
    if not path_db.is_absolute():
        base_dir = Path(__file__).resolve().parents[2]
        path_db = base_dir / path_db

    # Creamos automáticamente la estructura de directorios contenedores si no existen en el disco.
    path_db.parent.mkdir(parents=True, exist_ok=True)

    # Establecemos la conexión SQLite y configuramos row_factory como sqlite3.Row
    # para permitir acceder a las columnas de las filas mediante su nombre (clave-valor) además de por índice numérico.
    conn = sqlite3.connect(path_db)
    conn.row_factory = sqlite3.Row

    return conn


def get_sqlite_connection_legacy():
    """
    Conserva el nombre de conexión anterior para compatibilidad.

    Returns:
        Conexión SQLite con las filas accesibles por nombre de columna.
    """
    # Mantener este alias como función de compatibilidad evita romper llamadas en módulos antiguos del proyecto.
    return get_sqlite_connection()


def init_sqlite_db():
    """
    Crea automáticamente las tablas SQLite necesarias.
    Actualiza las columnas de sincronización si faltan.
    No elimina datos existentes.
    """

    # Obtenemos la conexión SQLite para agrupar la inicialización del esquema en una transacción.
    conn = get_sqlite_connection()

    try:
        # Usamos la conexión como gestor de contexto transaccional (commit/rollback automático).
        with conn:
            # 1. Caché local de alumnos históricos (procedentes de las fuentes externas de solo lectura).
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

            # 2. Tabla principal de alumnos locales gestionados por el sistema.
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

            # 3. Cola de operaciones pendientes para la sincronización de datos.
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

            # Mecanismo de migración ligera: consulta las columnas actuales de la tabla pending_operations
            # para actualizar instalaciones previas sin destruir la caché ni la cola de sincronización existente.
            columnas = {
                row["name"]
                for row in conn.execute(
                    "PRAGMA table_info(pending_operations)"
                )
            }

            # Si la columna 'attempts' no está presente, se añade dinámicamente mediante ALTER TABLE.
            if "attempts" not in columnas:
                conn.execute("""
                    ALTER TABLE pending_operations
                    ADD COLUMN attempts INTEGER NOT NULL DEFAULT 0
                """)

            # Si la columna 'last_error' no está presente, se añade para registrar fallos de sincronización.
            if "last_error" not in columnas:
                conn.execute("""
                    ALTER TABLE pending_operations
                    ADD COLUMN last_error TEXT
                """)

        print("Base de datos SQLite inicializada correctamente.")

    finally:
        # Nos aseguramos de cerrar siempre la conexión para liberar los recursos del archivo de base de datos local.
        conn.close()


class SQLiteConnector(BaseCRUDConnector):
    """
    Conector SQLite con lectura heredada de BaseConnector
    y operaciones CRUD heredadas de BaseCRUDConnector.
    """

    # Definimos la tabla principal sobre la que se ejecutarán las operaciones CRUD heredadas.
    TABLE_NAME = "alumnos"

    @property
    def placeholder(self) -> str:
        """Devuelve el marcador de parámetros utilizado por SQLite."""
        
        # SQLite utiliza signos de interrogación ('?') para sus parámetros posicionales en consultas SQL parametrizadas.
        return "?"

    def _connect(self):
        """Abre una conexión a la base SQLite local."""
        
        # Reutilizar el helper centralizado aplica automáticamente la ruta configurada y la row_factory de SQLite.
        return get_sqlite_connection()