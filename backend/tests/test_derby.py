from backend.connectors.derby_connector import conectar_derby


def test_conexion_derby():
    conexion = conectar_derby()

    try:
        cursor = conexion.cursor()
        cursor.execute("SELECT * FROM alumnos")

        filas = cursor.fetchall()

        for fila in filas:
            print(fila)

        cursor.close()

    finally:
        conexion.close()


if __name__ == "__main__":
    test_conexion_derby()