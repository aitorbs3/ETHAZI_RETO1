"""Conexión JDBC y acceso de solo lectura a la base histórica H2."""

# Importamos Path de pathlib para gestionar de forma robusta y multiplataforma
# las rutas de los archivos de base de datos y los drivers en el equipo.
from pathlib import Path

# Importamos jaydebeapi para posibilitar la comunicación JDBC entre Python y la base de datos Java H2.
import jaydebeapi

# Importamos las herramientas de configuración, la clase base y el gestor de la JVM del proyecto ETHAZI_RETO1.
from utils.config import obtener_variable
from connectors.base import BaseConnector
from utils.jvm import iniciar_jvm

# Definimos la ruta raíz del proyecto (ETHAZI_RETO1/) subiendo dos niveles desde este archivo.
PROJECT_ROOT = Path(__file__).resolve().parents[2]

# Definimos la ruta de la carpeta backend subiendo un nivel.
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Localizamos el archivo JAR específico del driver de H2 dentro de la estructura de drivers del backend.
H2_JAR = BACKEND_DIR / "drivers" / "h2" / "h2.jar"


def obtener_conexion_h2():
    """Abre H2 usando la ruta y las credenciales configuradas."""
    
    # Obtenemos la ruta de la base de datos H2 desde las variables de entorno (.env).
    ruta = Path(obtener_variable("H2_DATABASE"))
    
    # Si la ruta especificada es relativa, la anclamos a la raíz del proyecto
    # para asegurar que funcione independientemente de dónde se ejecute la terminal.
    if not ruta.is_absolute():
        ruta = PROJECT_ROOT / ruta
        
    # Verificamos y creamos automáticamente las carpetas contenedoras si no existen.
    ruta.parent.mkdir(parents=True, exist_ok=True)

    # Comprobamos físicamente que el archivo del driver H2 exista en el disco antes de continuar.
    if not H2_JAR.is_file():
        # Si no se encuentra el archivo JAR, lanzamos un error descriptivo.
        raise FileNotFoundError(f"Driver H2 no encontrado: {H2_JAR}")

    # Inicializamos la Máquina Virtual Java (JVM) de forma compartida con el resto de conectores JDBC.
    iniciar_jvm()
    
    # Establecemos la conexión JDBC utilizando jaydebeapi:
    # - Indicamos el driver de H2 ("org.h2.Driver").
    # - Construimos la URL JDBC añadiendo parámetros de optimización y estabilidad (como AUTO_SERVER y DB_CLOSE_DELAY).
    # - Pasamos las credenciales de usuario y contraseña leyendo las variables de entorno u otorgando valores por defecto ("sa", "").
    # - Indicamos la ruta del driver JAR de H2.
    return jaydebeapi.connect(
        "org.h2.Driver",
        f"jdbc:h2:{ruta};AUTO_SERVER=TRUE;DB_CLOSE_DELAY=-1",
        [obtener_variable("H2_USER", obligatoria=False) or "sa",
         obtener_variable("H2_PASSWORD", obligatoria=False) or ""],
        str(H2_JAR),
    )


class H2Connector(BaseConnector):
    """Solo lectura para los alumnos históricos de Hufflepuff."""

    def _connect(self):
        """Obtiene una conexión con la base H2 ya configurada."""
        
        # Invocamos la función auxiliar para aplicar la ruta, el driver JDBC y las credenciales
        # definidas en el entorno, proporcionando acceso de lectura a los datos históricos de Hufflepuff.
        return obtener_conexion_h2()