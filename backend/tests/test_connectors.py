from connectors.connector_factory import get_connector

"""""""""
$env:JAVA_HOME = "C:\Program Files\Java\jdk-21.0.12.1"
$env:Path = "$env:JAVA_HOME\bin;$env:Path"

$env:PYTHONPATH="backend"

derby:
python -c "from connectors.connector_factory import get_connector; c=get_connector('derby'); print(c.get_student('Albus'))"

h2:
python -c "from connectors.connector_factory import get_connector; c=get_connector('h2'); print(c.get_student('Cedric'))"

hsqldb:
python -c "from connectors.connector_factory import get_connector; c=get_connector('hsqldb'); print(c.get_student('Salazar'))"

todo junto:
python backend/tests/test_connectors.py
"""""""""
def probar_conector(nombre, nombre_busqueda):
    print("\n" + "=" * 60)
    print(f"PROBANDO CONECTOR: {nombre.upper()}")
    print("=" * 60)

    try:
        connector = get_connector(nombre)

        print("\n--- get_students() ---")

        estudiantes = connector.get_students()

        print(f"Total de estudiantes encontrados: {len(estudiantes)}")

        for estudiante in estudiantes:
            print(estudiante)

        print("\n--- get_student() ---")
        print(f"Buscando: {nombre_busqueda}")

        encontrados = connector.get_student(nombre_busqueda)

        print(f"Resultados encontrados: {len(encontrados)}")

        for estudiante in encontrados:
            print(estudiante)

        print(f"\n✓ {nombre.upper()} FUNCIONA CORRECTAMENTE")

    except Exception as error:
        print(f"\n✗ ERROR EN {nombre.upper()}")
        print(f"Tipo de error: {type(error).__name__}")
        print(f"Mensaje: {error}")


if __name__ == "__main__":

    probar_conector("derby", "Albus")
    probar_conector("h2", "Cedric")
    probar_conector("hsqldb", "Salazar")