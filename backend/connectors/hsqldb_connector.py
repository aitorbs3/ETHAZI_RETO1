"""Conexión JDBC y acceso de solo lectura a la base histórica HSQLDB."""

# Importamos Path de pathlib para gestionar de forma robusta y multiplataforma
# las rutas de las carpetas de bases de datos y los drivers del proyecto.
from pathlib import Path

# Importamos jaydebeapi para establecer la pasarela JDBC entre Python y el motor Java de HSQLDB.
import jaydebeapi

# Importamos las herramientas de configuración, la clase base y el gestor de la JVM de ETHAZI_RETO1.
from utils.config import obtener_variable
from connectors.base import BaseConnector
from utils.jvm import iniciar_jvm


# Definimos la ruta raíz del proyecto (ETHAZI_RETO1/) subiendo dos niveles desde este archivo.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Definimos la ruta de la carpeta backend subiendo un nivel.
BACKEND_DIR = Path(__file__).resolve().parents[1]


def conectar_hsqldb():
    """Abre HSQLDB en Windows/Linux, siempre en <directorio>/slytherin."""
    
    # HSQLDB espera un prefijo de fichero sin extensión en modo persistente.
    # Obtenemos la ruta base configurada en el archivo de entorno (.env).
    carpeta = Path(obtener_variable("HSQLDB_DATABASE"))
    
    # Si la ruta no es absoluta, la anclamos a la raíz del proyecto para asegurar portabilidad.
    if not carpeta.is_absolute():
        carpeta = PROJECT_ROOT / carpeta
        
    # Creamos el directorio contenedor si no existe físicamente en el disco.
    carpeta.mkdir(parents=True, exist_ok=True)
    
    # Definimos la ruta exacta del archivo de base de datos añadiendo el subfichero "slytherin" requerido.
    ruta_bd = carpeta / "slytherin"

    # Verificamos la existencia física del archivo JAR del driver de HSQLDB en el backend.
    jar = BACKEND_DIR / "drivers" / "hsqldb" / "hsqldb.jar"
    if not jar.is_file():
        # Si no se encuentra el driver, lanzamos un error claro y descriptivo.
        raise FileNotFoundError(f"Driver HSQLDB no encontrado: {jar}")
        
    # Iniciar la JVM una sola vez permite reutilizar el driver JDBC sin conflictos de memoria.
    iniciar_jvm()

    # Establecemos y devolvemos la conexión JDBC usando jaydebeapi:
    # - Indicamos el driver JDBC de HSQLDB ("org.hsqldb.jdbc.JDBCDriver").
    # - Construimos la URL en modo archivo local (file:).
    # - Pasamos las credenciales por defecto de HSQLDB (usuario "SA", contraseña vacía "").
    # - Adjuntamos la ruta del driver JAR.
    return jaydebeapi.connect(
        "org.hsqldb.jdbc.JDBCDriver",
        f"jdbc:hsqldb:file:{ruta_bd}",
        ["SA", ""],
        str(jar),
    )


class HSQLDBConnector(BaseConnector):
    """Solo lectura para los alumnos históricos de Slytherin."""

    def _connect(self):
        """Abre la base HSQLDB almacenada en la ruta configurada."""
        
        # Reutilizar el helper de conexión mantiene uniforme el arranque de la JVM
        # y asegura el acceso de solo lectura a los datos históricos de la casa Slytherin.
        return conectar_hsqldb()