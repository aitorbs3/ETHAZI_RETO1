from backend.connectors.oracle_connector import conectar_oracle


def test_conexion_oracle():
    conexion = conectar_oracle()

    try:
        cursor = conexion.cursor()

        cursor.execute("SELECT 1 FROM DUAL")
        resultado = cursor.fetchone()

        print(resultado)

        cursor.close()

    finally:
        conexion.close()


if __name__ == "__main__":
    test_conexion_oracle()