"""Pruebas de conexión e inicialización de datos de ejemplo en H2."""

# Importamos la función que permite obtener variables de configuración,
# como la ruta de la base de datos definida en el archivo .env.
from backend.utils.config import obtener_variable

# Importamos la función que establece la conexión con la base de datos H2.
from backend.connectors.h2_connector import obtener_conexion_h2


def probar_conexion_y_crear_datos():
    """Comprueba la conexión H2 y ejecuta un ciclo básico de lectura y escritura."""

    # Mostramos un mensaje para indicar el inicio de la prueba.
    print("=== Probando Conexión e Inicialización de H2 ===")

    # 1. Obtenemos la ruta de la base de datos desde el archivo .env.
    ruta_db = obtener_variable("H2_DATABASE")

    # Mostramos la ruta obtenida para comprobar la configuración.
    print(f"Ruta configurada en .env: {ruta_db}")

    # 2. Establecemos la conexión con la base de datos H2.
    # Según la configuración del conector, la base de datos puede crearse
    # automáticamente si todavía no existe.
    conn = obtener_conexion_h2()

    # Creamos un cursor para ejecutar consultas SQL.
    cursor = conn.cursor()

    # 3. Creamos la tabla prueba_h2 únicamente si no existe.
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prueba_h2 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            mensaje VARCHAR(100) NOT NULL
        )
    """)

    # id es la clave primaria y se genera automáticamente.
    # mensaje almacena un texto de hasta 100 caracteres.
    # NOT NULL impide que mensaje tenga un valor nulo.
    print(" Tabla 'prueba_h2' verificada/creada correctamente.")

    # 4. Insertamos un registro con el mensaje 'Harry Potter'.
    # El ID se genera automáticamente, por lo que no necesitamos indicarlo.
    cursor.execute("INSERT INTO prueba_h2 (mensaje) VALUES ('Harry Potter')")

    # Confirmamos la transacción para guardar los cambios en la base de datos.
    conn.commit()

    # 5. Consultamos el ID y el mensaje de todos los registros de la tabla.
    cursor.execute("SELECT id, mensaje FROM prueba_h2")

    # Recuperamos todas las filas devueltas por la consulta.
    # fetchall() devuelve una lista de tuplas.
    filas = cursor.fetchall()

    # Mostramos un encabezado para identificar los resultados.
    print("\nRegistros encontrados en la BD H2 de prueba:")

    # Recorremos cada fila obtenida de la base de datos.
    for fila in filas:
        # fila[0] contiene el ID y fila[1] contiene el mensaje.
        print(f"  - ID: {fila[0]} | Mensaje: {fila[1]}")

    # 6. Cerramos el cursor para liberar sus recursos.
    cursor.close()

    # Cerramos la conexión con la base de datos.
    conn.close()

    # Mostramos un mensaje que indica que la prueba ha finalizado.
    print("\n Prueba completada con éxito.")


# Comprobamos si este archivo se está ejecutando directamente.
# Si se importa desde otro módulo, la función no se ejecutará automáticamente.
if __name__ == "__main__":
    # Ejecutamos la prueba de conexión, escritura y lectura.
    probar_conexion_y_crear_datos()