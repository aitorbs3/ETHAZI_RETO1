"""Arranque compartido de la JVM con los controladores JDBC del proyecto."""

# Importar Path para construir y gestionar rutas de archivos y directorios.
from pathlib import Path

# Importar JPype, una biblioteca que permite interactuar con Java desde Python
# e iniciar una máquina virtual de Java (JVM) dentro del proceso de Python.
import jpype


# Obtener la ruta absoluta de la carpeta principal del backend.
# __file__ representa la ruta de este archivo (jvm.py).
# resolve() convierte la ruta en absoluta y normaliza sus componentes.
# parents[1] sube dos niveles en la jerarquía de directorios:
# parents[0] es la carpeta que contiene este archivo.
# parents[1] es la carpeta superior a esa.
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Construir la ruta de la carpeta donde se almacenan los controladores JDBC.
# Se presupone que existe una carpeta llamada drivers dentro del backend.
DRIVERS_DIR = BACKEND_DIR / "drivers"


def iniciar_jvm():
    """
    Inicia la máquina virtual de Java (JVM) con los drivers JDBC
    necesarios para conectar con las bases de datos del proyecto.

    La JVM solo se inicia una vez. Si ya está iniciada, se reutiliza
    para evitar intentar arrancarla de nuevo.
    """

    # Comprobar si la JVM ya está iniciada dentro del proceso de Python.
    # JPype no permite iniciar una segunda JVM en el mismo proceso.
    if jpype.isJVMStarted():
        # Si ya está iniciada, no es necesario hacer nada más.
        return

    # Buscar todos los archivos JAR dentro de la carpeta de drivers,
    # incluyendo los que estén almacenados en subcarpetas.
    # Los archivos JAR contienen clases Java, entre ellas las necesarias
    # para implementar los controladores JDBC de las bases de datos.
    #
    # rglob("*.jar") busca recursivamente archivos cuya extensión sea .jar.
    # str(jar) convierte cada objeto Path en una cadena con su ruta.
    jars = [
        str(jar)
        for jar in DRIVERS_DIR.rglob("*.jar")
    ]

    # Comprobar que se ha encontrado al menos un archivo JAR.
    # Sin los controladores necesarios, la aplicación podría no ser capaz
    # de establecer conexiones JDBC con las bases de datos.
    if not jars:
        # Lanzar una excepción indicando la carpeta en la que se buscaron.
        raise FileNotFoundError(
            f"No se encontraron drivers JDBC en {DRIVERS_DIR}"
        )

    # Iniciar la máquina virtual de Java mediante JPype.
    jpype.startJVM(
        # Obtener la ruta de la JVM predeterminada de la instalación de Java.
        # Esta ruta apunta a la biblioteca de la JVM que JPype necesita cargar.
        jpype.getDefaultJVMPath(),

        # Establecer el classpath con las rutas de los archivos JAR encontrados.
        # Esto permite que Java localice las clases de los controladores JDBC.
        classpath=jars,

        # Solicitar que las cadenas Java se conviertan automáticamente
        # en cadenas Python cuando JPype devuelve valores de tipo String.
        convertStrings=True,
    )