"""
Descripción: Script de verificación manual para comprobar la conectividad directa
con la base de datos histórica Apache Derby (Gryffindor) y realizar consultas SQL
de conteo y paginación mediante el puente JDBC.
"""

from backend.connectors.derby_connector import conectar_derby


def ver_tabla_derby() -> None:
    """
    Consulta y muestra en consola el número total de alumnos y una muestra
    de los primeros registros almacenados en la base de datos Apache Derby.
    """
    # 1. Abrimos la conexión activa con la base de datos histórica Apache Derby.
    # Abrir y cerrar los recursos en el mismo flujo transaccional evita dejar sesiones 
    # JDBC activas o bloqueos en los ficheros de datos locales de Derby.
    conexion = conectar_derby()
    
    # 2. Creamos un cursor asociado a la conexión para enviar y ejecutar sentencias SQL.
    cursor = conexion.cursor()

    try:
        # 3. Ejecutamos una función de agregación (COUNT) para conocer el volumen total de alumnos.
        cursor.execute("SELECT COUNT(*) FROM alumnos")
        
        # Recuperamos la primera columna de la primera fila devuelta con el resultado numérico.
        cantidad = cursor.fetchone()[0]

        print(f"Total de alumnos en Derby: {cantidad}")
        print()

        # 4. Ejecutamos una consulta SELECT estructurada utilizando la cláusula estándar 
        # 'FETCH FIRST 20 ROWS ONLY' para limitar la salida en pantalla y optimizar el rendimiento.
        cursor.execute(
            """
            SELECT
                id,
                nombre,
                casa,
                especie,
                genero,
                nacimiento,
                nacionalidad,
                patronus
            FROM alumnos
            FETCH FIRST 20 ROWS ONLY
            """
        )

        # Iteramos mediante fetchall() sobre el conjunto de resultados y mostramos cada tupla por consola.
        for alumno in cursor.fetchall():
            print(alumno)

    finally:
        # 5. Bloque de limpieza obligatoria (Garantía de liberación de recursos):
        # Cerramos explícitamente el cursor y la conexión en el bloque finally 
        # para garantizar que se liberen siempre, incluso si se produce un error durante la consulta.
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    # Punto de entrada para la ejecución directa de la prueba unitaria/manual desde la terminal.
    ver_tabla_derby()