from backend.connectors.hsqldb_connector import conectar_hsqldb


def test_conexion_hsqldb():
    """
    Comprueba que se puede establecer una conexión
    con la base de datos HSQLDB.

    Si la conexión se realiza correctamente, se muestra
    un mensaje por consola y posteriormente se cierra.
    """

    # Intentamos establecer la conexión con HSQLDB.
    conexion = conectar_hsqldb()

    try:
        # Si hemos llegado hasta aquí, la conexión ha sido correcta.
        print("Conexión con HSQLDB realizada correctamente.")

    finally:
        # Cerramos la conexión después de realizar la prueba.
        conexion.close()


if __name__ == "__main__":
    test_conexion_hsqldb()