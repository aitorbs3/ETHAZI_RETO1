from pathlib import Path

import jpype


# Obtenemos la carpeta principal de backend.
# __file__ representa la ruta de este archivo (jvm.py).
BACKEND_DIR = Path(__file__).resolve().parents[1]

# Ruta donde se encuentran los drivers JDBC de las bases de datos.
# Dentro de esta carpeta están los JAR de Derby, H2 y HSQLDB.
DRIVERS_DIR = BACKEND_DIR / "drivers"


def iniciar_jvm():
    """
    Inicia la máquina virtual de Java (JVM) con los drivers JDBC
    necesarios para conectar con las bases de datos del proyecto.

    La JVM solo se inicia una vez. Si ya está iniciada, se reutiliza
    para evitar intentar arrancarla de nuevo.
    """

    # Comprobamos si la máquina virtual de Java ya está funcionando.
    if jpype.isJVMStarted():
        return

    # Buscamos todos los archivos JAR dentro de la carpeta de drivers,
    # incluidas sus subcarpetas.
    # Los JAR contienen las clases Java necesarias para los conectores.
    jars = [
        str(jar)
        for jar in DRIVERS_DIR.rglob("*.jar")
    ]

    # Si no encontramos ningún JAR, no podemos cargar los drivers JDBC.
    if not jars:
        raise FileNotFoundError(
            f"No se encontraron drivers JDBC en {DRIVERS_DIR}"
        )

    # Iniciamos la JVM utilizando la instalación de Java configurada.
    # classpath indica dónde están los JAR que Java debe poder utilizar.
    # convertStrings=True facilita la conversión de cadenas Java a Python.
    jpype.startJVM(
        jpype.getDefaultJVMPath(),
        classpath=jars,
        convertStrings=True,
    )