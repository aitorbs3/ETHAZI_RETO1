from backend.connectors.oracle_connector import OracleConnector


def test_oracle():
    print("=" * 60)
    print("PROBANDO CONECTOR: ORACLE")
    print("=" * 60)

    connector = OracleConnector()

    try:
        # 1. Obtener todos los alumnos
        print("\n--- get_students() ---")

        estudiantes = connector.get_students()

        print(f"Total de estudiantes encontrados: {len(estudiantes)}")
        print("Mostrando los primeros 20 alumnos:\n")

        for estudiante in estudiantes[:20]:
            print(
                f"ID: {estudiante.id} | "
                f"Nombre: {estudiante.nombre} | "
                f"Casa: {estudiante.casa}"
            )

        # 2. Buscar alumnos por nombre
        nombre_busqueda = "Alannis"

        print("\n--- get_student() ---")
        print(f"Buscando: {nombre_busqueda}")

        encontrados = connector.get_student(nombre_busqueda)

        print(f"Resultados encontrados: {len(encontrados)}")

        for estudiante in encontrados:
            print(estudiante)

        print("\nORACLE FUNCIONA CORRECTAMENTE")

    except Exception as error:
        print("\nERROR EN ORACLE")
        print(f"Tipo de error: {type(error).__name__}")
        print(f"Mensaje: {error}")

    finally:
        print("\nPrueba finalizada.")


if __name__ == "__main__":
    test_oracle()