from backend.connectors.derby_connector import conectar_derby


def ver_tabla_derby():
    conexion = conectar_derby()
    cursor = conexion.cursor()

    try:
        cursor.execute("SELECT COUNT(*) FROM alumnos")
        cantidad = cursor.fetchone()[0]

        print(f"Total de alumnos: {cantidad}")
        print()

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

        for alumno in cursor.fetchall():
            print(alumno)

    finally:
        cursor.close()
        conexion.close()


if __name__ == "__main__":
    ver_tabla_derby()