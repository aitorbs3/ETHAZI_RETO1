"""Prueba manual de conexión y lectura de la base histórica Oracle."""

# Importa la clase encargada de conectarse a la base de datos Oracle.
from backend.connectors.oracle_connector import OracleConnector


def test_oracle():
    """Muestra alumnos de Oracle y verifica una búsqueda parcial por nombre."""

    # Muestra una línea separadora para identificar el inicio de la prueba.
    print("=" * 60)
    print("PROBANDO CONECTOR: ORACLE")
    print("=" * 60)

    # Crea un objeto OracleConnector para acceder a los datos de Oracle.
    connector = OracleConnector()

    try:
        # 1. Obtener todos los alumnos.
        print("\n--- get_students() ---")

        # Llama al método get_students() para recuperar todos los estudiantes.
        estudiantes = connector.get_students()

        # Muestra el número total de estudiantes recuperados.
        print(f"Total de estudiantes encontrados: {len(estudiantes)}")

        # Indica que solo se mostrarán los primeros 20 estudiantes.
        print("Mostrando los primeros 20 alumnos:\n")

        # Recorre los primeros 20 estudiantes de la lista obtenida.
        for estudiante in estudiantes[:20]:
            # Muestra el identificador, el nombre y la casa de cada estudiante.
            print(
                f"ID: {estudiante.id} | "
                f"Nombre: {estudiante.nombre} | "
                f"Casa: {estudiante.casa}"
            )

        # 2. Buscar alumnos por nombre.
        # Define el nombre que se utilizará para realizar la búsqueda.
        nombre_busqueda = "Alannis"

        print("\n--- get_student() ---")
        print(f"Buscando: {nombre_busqueda}")

        # Busca estudiantes cuyo nombre coincida parcial o totalmente
        # con el texto indicado, según la implementación del conector.
        encontrados = connector.get_student(nombre_busqueda)

        # Muestra el número de estudiantes que cumplen la búsqueda.
        print(f"Resultados encontrados: {len(encontrados)}")

        # Recorre los estudiantes encontrados y muestra cada objeto.
        for estudiante in encontrados:
            print(estudiante)

        # Si se llega hasta aquí, las operaciones anteriores no han
        # generado ninguna excepción.
        print("\nORACLE FUNCIONA CORRECTAMENTE")

    except Exception as error:
        # Captura cualquier excepción producida durante la prueba.
        print("\nERROR EN ORACLE")

        # Muestra el nombre de la clase de la excepción, por ejemplo,
        # OperationalError o ValueError, según el error producido.
        print(f"Tipo de error: {type(error).__name__}")

        # Muestra el mensaje descriptivo del error.
        print(f"Mensaje: {error}")

    finally:
        # Este bloque se ejecuta siempre, haya ocurrido un error o no.
        # Sirve para indicar que la prueba ha terminado.
        print("\nPrueba finalizada.")


# Comprueba si este archivo se está ejecutando directamente.
# Si se importa desde otro módulo, test_oracle() no se ejecutará
# automáticamente.
if __name__ == "__main__":
    # Ejecuta la prueba manual de conexión y lectura de Oracle.
    test_oracle()