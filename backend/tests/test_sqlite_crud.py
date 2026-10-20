"""Prueba manual de operaciones CRUD sobre la base SQLite local."""

# Importar date para crear las fechas de nacimiento de los alumnos.
from datetime import date

# Importar Path para gestionar las rutas de los archivos.
from pathlib import Path

# Importar el conector de SQLite y la función que obtiene una conexión.
from connectors.sqlite_connector import (
    SQLiteConnector,
    get_sqlite_connection,
)

# Importar el modelo Student para crear objetos que representan alumnos.
from backend.models.student import Student


def ejecutar_script_sql():
    """Ejecuta el script de esquema local para preparar la prueba CRUD."""

    # Obtener la ruta raíz del repositorio a partir de la ubicación de este archivo.
    # Así, el programa puede encontrar el script SQL independientemente
    # del directorio desde el que se ejecute.
    base_dir = Path(__file__).resolve().parents[2]

    # Construir la ruta completa del archivo SQL que crea la tabla de SQLite.
    sql_file = (
        base_dir
        / "data"
        / "sql"
        / "sqlite"
        / "crear_tabla_sqlite.sql"
    )

    # Comprobar que el archivo SQL existe antes de intentar leerlo.
    # Si no existe, lanzar una excepción indicando su ruta.
    if not sql_file.exists():
        raise FileNotFoundError(
            f"No se encuentra el script SQL: {sql_file}"
        )

    # Leer el contenido del script SQL utilizando la codificación UTF-8.
    sql = sql_file.read_text(encoding="utf-8")

    # Obtener una conexión con la base de datos SQLite local.
    connection = get_sqlite_connection()

    try:
        # Ejecutar las instrucciones SQL para preparar la estructura de la tabla.
        connection.executescript(sql)

        # Confirmar los cambios realizados en la base de datos.
        connection.commit()

        # Informar de que la preparación de la tabla ha finalizado.
        print("Tabla de SQLite preparada correctamente.")

    finally:
        # Cerrar la conexión incluso si ocurre algún error durante la ejecución.
        connection.close()


def mostrar_alumno(alumno):
    """Imprime los campos principales de un alumno."""

    # Mostrar los atributos del alumno para comprobar sus datos.
    # Esta información permite comparar el estado antes y después de modificarlo.
    print(f"ID:           {alumno.id}")
    print(f"Nombre:       {alumno.nombre}")
    print(f"Casa:         {alumno.casa}")
    print(f"Especie:      {alumno.especie}")
    print(f"Género:       {alumno.genero}")
    print(f"Nacimiento:   {alumno.nacimiento}")
    print(f"Nacionalidad: {alumno.nacionalidad}")
    print(f"Patronus:     {alumno.patronus}")
    print(f"Imagen:       {alumno.imagen}")


def mostrar_todos_los_alumnos(connector):
    """Muestra los alumnos obtenidos a través del conector SQLite."""

    # Recuperar todos los alumnos almacenados en la base de datos.
    alumnos = connector.get_students()

    # Mostrar cuántos alumnos se han recuperado.
    print(f"\nTotal de alumnos: {len(alumnos)}")

    # Si no hay alumnos, mostrar un mensaje y terminar la función.
    if not alumnos:
        print("No hay alumnos en la tabla.")
        return

    # Recorrer la lista de alumnos enumerándolos desde el número 1.
    for i, alumno in enumerate(alumnos, start=1):
        # Mostrar un encabezado para identificar cada alumno.
        print(f"\n--- Alumno {i} ---")

        # Mostrar todos los datos del alumno actual.
        mostrar_alumno(alumno)


def probar_sqlite_crud():
    """Ejecuta operaciones CRUD de demostración sobre alumnos de prueba."""

    # Crear el conector que permite realizar operaciones sobre SQLite.
    connector = SQLiteConnector()

    # Crear el primer alumno de prueba con sus datos iniciales.
    alumno1 = Student(
        id="TESTSQL001",
        nombre="Harry Potter Prueba",
        casa="Gryffindor",
        especie="Humano",
        genero="Masculino",
        nacimiento=date(1980, 7, 31),
        nacionalidad="Británica",
        patronus="Ciervo",
        imagen=None,
    )

    # Crear una versión modificada del primer alumno.
    # Se mantiene el mismo ID, pero se cambia el nombre y la casa.
    alumno1_editado = Student(
        id="TESTSQL001",
        nombre="Harry Potter Editado",
        casa="Slytherin",
        especie="Humano",
        genero="Masculino",
        nacimiento=date(1980, 7, 31),
        nacionalidad="Británica",
        patronus="Ciervo",
        imagen=None,
    )

    # Crear el segundo alumno de prueba para comprobar las operaciones
    # de inserción y eliminación mediante su nombre.
    alumno2 = Student(
        id="TESTSQL002",
        nombre="Hermione Granger Prueba",
        casa="Gryffindor",
        especie="Humana",
        genero="Femenino",
        nacimiento=date(1979, 9, 19),
        nacionalidad="Británica",
        patronus="Nutria",
        imagen=None,
    )

    try:
        # Mostrar el encabezado general de las pruebas.
        print("\n========== PRUEBA CRUD SQLITE ==========")

        # Eliminar posibles registros de pruebas anteriores.
        # Esto evita conflictos al insertar alumnos con los mismos ID.
        connector.delete_student("TESTSQL001")
        connector.delete_student("TESTSQL002")

        # 1. READ: consultar y mostrar el estado inicial de la tabla.
        print("\n1. ESTADO INICIAL")
        mostrar_todos_los_alumnos(connector)

        # 2. CREATE: insertar el primer alumno en la base de datos.
        print("\n2. AÑADIR ALUMNO 1")
        connector.create_student(alumno1)

        # Mostrar los alumnos para comprobar que se ha insertado.
        mostrar_todos_los_alumnos(connector)

        # 3. CREATE: insertar el segundo alumno.
        print("\n3. AÑADIR ALUMNO 2")
        connector.create_student(alumno2)

        # Mostrar los alumnos para comprobar la segunda inserción.
        mostrar_todos_los_alumnos(connector)

        # 4. UPDATE: modificar los datos del primer alumno utilizando su ID.
        print("\n4. EDITAR ALUMNO 1")
        connector.update_student("TESTSQL001", alumno1_editado)

        # Mostrar los alumnos para comprobar los cambios realizados.
        mostrar_todos_los_alumnos(connector)

        # Consultar los alumnos por el nombre actualizado.
        actualizados = connector.get_student("Harry Potter Editado")

        # Comprobar que existe un alumno con el ID esperado y la casa modificada.
        # Si no se cumple la condición, assert lanza una excepción.
        assert any(
            a.id == "TESTSQL001" and a.casa == "Slytherin"
            for a in actualizados
        ), "El alumno no se ha actualizado correctamente."

        # 5. DELETE: eliminar el primer alumno utilizando su ID.
        print("\n5. BORRAR ALUMNO 1 POR ID")
        eliminado = connector.delete_student("TESTSQL001")

        # Comprobar que la operación ha confirmado la eliminación.
        assert eliminado, "No se ha eliminado el alumno por ID."

        # Mostrar los alumnos restantes después de la eliminación.
        mostrar_todos_los_alumnos(connector)

        # 6. DELETE: eliminar el segundo alumno utilizando su nombre.
        print("\n6. BORRAR ALUMNO 2 POR NOMBRE")
        eliminados = connector.delete_student_by_name(
            "Hermione Granger Prueba"
        )

        # Comprobar que se ha eliminado al menos un registro.
        assert eliminados >= 1, "No se ha eliminado el alumno por nombre."

        # Mostrar el estado final de la tabla.
        mostrar_todos_los_alumnos(connector)

        # Informar de que todas las comprobaciones han terminado correctamente.
        print("\nTODAS LAS PRUEBAS CRUD HAN FINALIZADO CORRECTAMENTE.")

    finally:
        # Limpiar los registros de prueba aunque se produzca algún error.
        # Así se evita dejar datos de demostración en la base de datos.
        connector.delete_student("TESTSQL001")
        connector.delete_student("TESTSQL002")


# Comprobar si el archivo se está ejecutando directamente.
if __name__ == "__main__":

    # Preparar la estructura de la base de datos antes de realizar las pruebas.
    ejecutar_script_sql()

    # Ejecutar las operaciones CRUD de demostración.
    probar_sqlite_crud()