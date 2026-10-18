"""Prueba de conexión con la base de datos central MariaDB."""

# Importamos la función encargada de establecer la conexión
# con la base de datos MariaDB.
from backend.connectors.mariadb_connector import conectar_mariadb


def test_conexion_mariadb():
    """Verifica la conexión a MariaDB ejecutando una consulta constante."""

    # SELECT 1 comprueba que podemos ejecutar una consulta sencilla
    # sin modificar los datos almacenados en la base de datos.

    # Establecemos la conexión con MariaDB.
    conexion = conectar_mariadb()

    try:
        # Creamos un cursor para ejecutar sentencias SQL.
        cursor = conexion.cursor()

        # Ejecutamos una consulta constante que devuelve el valor 1.
        cursor.execute("SELECT 1")

        # Recuperamos la primera fila del resultado de la consulta.
        # fetchone() devuelve una tupla con el resultado: (1,).
        resultado = cursor.fetchone()

        # Mostramos el resultado por consola.
        print(resultado)

        # Cerramos el cursor después de utilizarlo.
        cursor.close()

    finally:
        # Cerramos la conexión incluso si se produce un error
        # durante la ejecución de la consulta.
        conexion.close()


# Comprobamos si este archivo se está ejecutando directamente.
# Si se importa desde otro módulo, la función no se ejecutará automáticamente.
if __name__ == "__main__":

    # Ejecutamos la prueba de conexión con MariaDB.
    test_conexion_mariadb()