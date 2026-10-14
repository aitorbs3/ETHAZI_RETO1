from models.student import Student
from backend.repositories.student_repository import StudentRepository
from connectors.sqlite_connector import get_sqlite_connection


def comprobar_base_datos():
    """
    Comprueba la ruta de SQLite y las tablas disponibles.
    """
    connection = get_sqlite_connection()

    try:
        ruta = connection.execute(
            "PRAGMA database_list"
        ).fetchone()[2]

        tablas = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        nombres_tablas = [fila["name"] for fila in tablas]

        print("\n========== COMPROBACIÓN SQLITE ==========")
        print(f"Base de datos utilizada: {ruta}")
        print(f"Tablas disponibles: {nombres_tablas}")

        if "alumnos" not in nombres_tablas:
            raise RuntimeError(
                "La base de datos utilizada no contiene la tabla "
                "'alumnos'. Comprueba la inicialización del esquema "
                "y la ruta configurada en SQLITE_DATABASE."
            )

        if "pending_operations" not in nombres_tablas:
            raise RuntimeError(
                "La base de datos no contiene la tabla "
                "'pending_operations'. Ejecuta el script SQL "
                "de creación de esa tabla antes de continuar."
            )

    finally:
        connection.close()


def probar_alta_con_sincronizacion():
    """
    Comprueba que crear un alumno:
    1. Genera un UUID.
    2. Guarda el alumno en SQLite.
    3. Registra una operación CREATE pendiente de sincronizar.
    """

    comprobar_base_datos()

    repository = StudentRepository()

    student = Student(
        id="",
        nombre="Alumno UUID Prueba",
        casa="Hogwarts",
        especie="Humano",
        genero="Masculino",
        nacimiento=None,
        nacionalidad="Británica",
        patronus=None,
        imagen=None,
    )

    print("\n========== PRUEBA DE ALTA Y SINCRONIZACIÓN ==========")

    creado = repository.create_student(student)

    print(f"ID generado: {creado.id}")
    print(f"Nombre: {creado.nombre}")

    if not creado.id:
        raise AssertionError("No se ha generado el UUID del alumno.")

    if creado.nombre != "Alumno UUID Prueba":
        raise AssertionError("El nombre del alumno no coincide.")

    connection = get_sqlite_connection()

    try:
        alumno = connection.execute(
            """
            SELECT id, nombre
            FROM alumnos
            WHERE id = ?
            """,
            (creado.id,),
        ).fetchone()

        operacion = connection.execute(
            """
            SELECT
                id,
                operation,
                student_id,
                nombre,
                nombre_editado,
                payload
            FROM pending_operations
            WHERE student_id = ?
              AND operation = 'CREATE'
            ORDER BY id DESC
            LIMIT 1
            """,
            (creado.id,),
        ).fetchone()

        if alumno is None:
            raise AssertionError(
                "El alumno no se ha guardado en la tabla alumnos."
            )

        if operacion is None:
            raise AssertionError(
                "No se ha registrado la operación CREATE pendiente."
            )

        print("\nAlumno guardado correctamente:")
        print(f"  ID: {alumno['id']}")
        print(f"  Nombre: {alumno['nombre']}")

        print("\nOperación pendiente:")
        print(f"  ID de operación: {operacion['id']}")
        print(f"  Tipo: {operacion['operation']}")
        print(f"  ID del alumno: {operacion['student_id']}")
        print(f"  Nombre: {operacion['nombre']}")
        print(f"  Nombre editado: {operacion['nombre_editado']}")
        print(f"  Payload: {operacion['payload']}")

        if operacion["student_id"] != creado.id:
            raise AssertionError(
                "El UUID de la operación no coincide con el alumno."
            )

        print("\nPRUEBA COMPLETADA CORRECTAMENTE.")

    finally:
        connection.close()


if __name__ == "__main__":
    probar_alta_con_sincronizacion()