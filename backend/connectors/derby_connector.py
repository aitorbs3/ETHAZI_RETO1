"""Conexión JDBC y acceso de solo lectura a la base histórica de Derby."""

# Importamos Path de pathlib para gestionar rutas de archivos de manera robusta
# y multiplataforma (independientemente de si se ejecuta en Windows o Linux).
from pathlib import Path

# Importamos jaydebeapi, la librería que permite conectar Python con bases de datos Java mediante JDBC.
import jaydebeapi

# Importamos funciones y clases del propio backend del proyecto ETHAZI_RETO1.
from utils.config import obtener_variable
from connectors.base import BaseConnector
from utils.jvm import iniciar_jvm

# Definimos la ruta raíz del repositorio (ETHAZI_RETO1/) subiendo dos niveles desde este archivo.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Definimos la ruta de la carpeta backend subiendo un nivel.
BACKEND_DIR = Path(__file__).resolve().parents[1]


def conectar_derby(crear=False):
    """Conecta con Derby incrustado; crear=True solo en la carga inicial."""
    
    # Obtenemos la ruta de la base de datos configurada en el archivo .env.
    ruta = Path(obtener_variable("DERBY_DATABASE"))
    
    # Si la ruta no es absoluta, la resolvemos de forma relativa desde la raíz del proyecto,
    # evitando problemas si la API se arranca desde un directorio distinto en la terminal.
    if not ruta.is_absolute():
        ruta = PROJECT_ROOT / ruta
        
    # Comprobamos y creamos automáticamente la carpeta contenedora si no existe.
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # Apache Derby necesita obligatoriamente los tres archivos JAR que se distribuyen
    # dentro de la estructura del propio proyecto backend para poder funcionar.
    drivers = BACKEND_DIR / "drivers" / "derby"
    
    # Creamos una lista con las rutas completas de cada uno de los drivers JAR necesarios.
    jars = [str(drivers / nombre) for nombre in (
        "derby.jar", "derbyshared.jar", "derbytools.jar"
    )]
    
    # Recorremos cada archivo JAR para verificar que existe físicamente en el disco.
    for archivo in jars:
        if not Path(archivo).is_file():
            # Si falta algún driver, lanzamos un error claro para evitar fallos crípticos de Java.
            raise FileNotFoundError(f"Driver Derby no encontrado: {archivo}")

    # Iniciamos la Máquina Virtual Java (JVM). Esta JVM se comparte de forma segura
    # con los demás conectores JDBC del sistema (como H2 o HSQLDB).
    iniciar_jvm()
    
    # Construimos la URL de conexión JDBC específica para el motor embebido de Apache Derby.
    # Añadimos ';create=true' al final solo si el parámetro crear es True (para la carga inicial).
    url = f"jdbc:derby:{ruta}" + (";create=true" if crear else "")
    
    # Establecemos y devolvemos la conexión JDBC utilizando jaydebeapi,
    # indicando el driver de Java, la URL, las credenciales vacías [] y la lista de JARs.
    return jaydebeapi.connect(
        "org.apache.derby.jdbc.EmbeddedDriver", url, [], jars,
    )


class DerbyConnector(BaseConnector):
    """Solo lectura para los alumnos históricos de Gryffindor."""

    def _connect(self):
        """Abre una conexión Derby existente, sin crear la base de datos."""
        
        # Llamamos a conectar_derby por defecto sin argumentos (crear=False),
        # garantizando que este conector funcione estrictamente en modo de solo lectura
        # para proteger los datos históricos de la casa Gryffindor.
        return conectar_derby()