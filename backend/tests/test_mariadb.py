from backend.connectors.mariadb_connector import conectar_mariadb


def test_conexion_mariadb():
    conexion = conectar_mariadb()

    try:
        cursor = conexion.cursor()

        cursor.execute("SELECT 1")
        resultado = cursor.fetchone()

        print(resultado)

        cursor.close()

    finally:
        conexion.close()


if __name__ == "__main__":
    test_conexion_mariadb()