"""Pruebas de creación local y posterior sincronización de alumnos."""

# Importar el modelo Student para representar al alumno.
from models.student import Student

# Importar el repositorio que gestiona las operaciones sobre los alumnos.
from backend.repositories.student_repository import StudentRepository

# Importar la función que permite conectarse a la base de datos SQLite local.
from connectors.sqlite_connector import get_sqlite_connection


def comprobar_base_datos():
    """
    Comprueba la ruta de SQLite y las tablas disponibles.
    """

    # Obtener una conexión con la base de datos SQLite que utiliza la aplicación.
    # Esto permite comprobar que se está trabajando con el archivo correcto.
    connection = get_sqlite_connection()

    try:
        # Consultar la ruta real de la base de datos abierta.
        # PRAGMA database_list devuelve información sobre las bases conectadas.
        ruta = connection.execute(
            "PRAGMA database_list"
        ).fetchone()[2]

        # Consultar los nombres de las tablas existentes en SQLite.
        # sqlite_master contiene información sobre los objetos de la base de datos.
        tablas = connection.execute(
            """
            SELECT name
            FROM sqlite_master
            WHERE type = 'table'
            ORDER BY name
            """
        ).fetchall()

        # Crear una lista con los nombres de las tablas encontradas.
        nombres_tablas = [fila["name"] for fila in tablas]

        # Mostrar la ruta de la base de datos y las tablas disponibles.
        print("\n========== COMPROBACIÓN SQLITE ==========")
        print(f"Base de datos utilizada: {ruta}")
        print(f"Tablas disponibles: {nombres_tablas}")

        # Comprobar que existe la tabla donde se almacenan los alumnos.
        # Si falta, lanzar una excepción indicando el problema.
        if "alumnos" not in nombres_tablas:
            raise RuntimeError(
                "La base de datos utilizada no contiene la tabla "
                "'alumnos'. Comprueba la inicialización del esquema "
                "y la ruta configurada en SQLITE_DATABASE."
            )

        # Comprobar que existe la tabla donde se registran las operaciones
        # pendientes de sincronización con la base de datos central.
        if "pending_operations" not in nombres_tablas:
            raise RuntimeError(
                "La base de datos no contiene la tabla "
                "'pending_operations'. Ejecuta el script SQL "
                "de creación de esa tabla antes de continuar."
            )

    finally:
        # Cerrar la conexión tanto si la comprobación termina correctamente
        # como si se produce alguna excepción.
        connection.close()


def probar_alta_con_sincronizacion():
    """
    Comprueba que crear un alumno:
    1. Genera un UUID.
    2. Guarda el alumno en SQLite.
    3. Registra una operación CREATE pendiente de sincronizar.
    """

    # Comprobar que la base de datos contiene las tablas necesarias
    # antes de intentar registrar un alumno.
    comprobar_base_datos()

    # Crear el repositorio encargado de gestionar los alumnos.
    repository = StudentRepository()

    # Crear un objeto Student con los datos del alumno de prueba.
    # El ID se deja vacío para comprobar si el repositorio genera un UUID.
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

    # Mostrar el encabezado de la prueba.
    print("\n========== PRUEBA DE ALTA Y SINCRONIZACIÓN ==========")

    # Registrar el alumno mediante el repositorio.
    # Se espera que genere un UUID, lo guarde en SQLite y registre
    # una operación CREATE pendiente de sincronización.
    creado = repository.create_student(student)

    # Mostrar el identificador generado y el nombre del alumno registrado.
    print(f"ID generado: {creado.id}")
    print(f"Nombre: {creado.nombre}")

    # Comprobar que el alumno tiene un identificador.
    # Si está vacío, la prueba falla porque no se ha generado el UUID esperado.
    if not creado.id:
        raise AssertionError("No se ha generado el UUID del alumno.")

    # Comprobar que el nombre del alumno coincide con el esperado.
    if creado.nombre != "Alumno UUID Prueba":
        raise AssertionError("El nombre del alumno no coincide.")

    # Abrir una conexión para verificar directamente los datos almacenados
    # en las tablas alumnos y pending_operations.
    connection = get_sqlite_connection()

    try:
        # Buscar el alumno en la tabla local utilizando su UUID.
        # El signo ? representa un parámetro que se proporciona por separado,
        # evitando insertar el identificador directamente en la consulta SQL.
        alumno = connection.execute(
            """
            SELECT id, nombre
            FROM alumnos
            WHERE id = ?
            """,
            (creado.id,),
        ).fetchone()

        # Buscar la operación CREATE pendiente asociada al mismo alumno.
        # Se recuperan los datos principales de la operación y su payload.
        # ORDER BY id DESC y LIMIT 1 permiten obtener el registro más reciente.
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

        # Comprobar que el alumno realmente existe en la tabla local.
        if alumno is None:
            raise AssertionError(
                "El alumno no se ha guardado en la tabla alumnos."
            )

        # Comprobar que se ha registrado la operación pendiente de creación.
        if operacion is None:
            raise AssertionError(
                "No se ha registrado la operación CREATE pendiente."
            )

        # Mostrar los datos del alumno recuperados directamente de SQLite.
        print("\nAlumno guardado correctamente:")
        print(f"  ID: {alumno['id']}")
        print(f"  Nombre: {alumno['nombre']}")

        # Mostrar los datos de la operación pendiente.
        # Esto permite comprobar que existe información preparada
        # para una futura sincronización.
        print("\nOperación pendiente:")
        print(f"  ID de operación: {operacion['id']}")
        print(f"  Tipo: {operacion['operation']}")
        print(f"  ID del alumno: {operacion['student_id']}")
        print(f"  Nombre: {operacion['nombre']}")
        print(f"  Nombre editado: {operacion['nombre_editado']}")
        print(f"  Payload: {operacion['payload']}")

        # Verificar que la operación pendiente está asociada al mismo alumno
        # que se acaba de crear.
        if operacion["student_id"] != creado.id:
            raise AssertionError(
                "El UUID de la operación no coincide con el alumno."
            )

        # Informar de que todas las comprobaciones han finalizado correctamente.
        print("\nPRUEBA COMPLETADA CORRECTAMENTE.")

    finally:
        # Cerrar la conexión utilizada para consultar ambas tablas.
        connection.close()


# Comprobar si este archivo se está ejecutando directamente.
if __name__ == "__main__":

    # Ejecutar la prueba completa de creación y registro de sincronización.
    probar_alta_con_sincronizacion()