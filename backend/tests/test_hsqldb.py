"""Prueba manual de conexión y consultas a la base histórica HSQLDB."""

# Importamos la función encargada de establecer la conexión
# con la base de datos HSQLDB.
from backend.connectors.hsqldb_connector import conectar_hsqldb


def test_conexion_hsqldb():
    """
    Comprueba que se puede establecer una conexión
    con la base de datos HSQLDB.

    Si la conexión se realiza correctamente, se muestra
    un mensaje por consola y posteriormente se cierra.
    """

    # Intentamos establecer la conexión con HSQLDB.
    # Si la conexión falla, se producirá una excepción.
    conexion = conectar_hsqldb()

    try:
        # Si hemos llegado hasta aquí, significa que la función
        # ha devuelto una conexión correctamente.
        print("Conexión con HSQLDB realizada correctamente.")

    finally:
        # Cerramos la conexión después de realizar la prueba.
        # El bloque finally se ejecuta aunque se produzca un error
        # dentro del bloque try.
        conexion.close()


# Comprobamos si este archivo se está ejecutando directamente.
# Si se importa desde otro módulo, la función no se ejecutará automáticamente.
if __name__ == "__main__":

    # Ejecutamos la prueba de conexión con HSQLDB.
    test_conexion_hsqldb()