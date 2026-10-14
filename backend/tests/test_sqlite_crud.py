from datetime import date
from pathlib import Path

from connectors.sqlite_connector import (
    SQLiteConnector,
    get_sqlite_connection,
)
from backend.models.student import Student


def ejecutar_script_sql():
    base_dir = Path(__file__).resolve().parents[2]
    sql_file = (
        base_dir
        / "data"
        / "sql"
        / "sqlite"
        / "crear_tabla_sqlite.sql"
    )

    if not sql_file.exists():
        raise FileNotFoundError(
            f"No se encuentra el script SQL: {sql_file}"
        )

    sql = sql_file.read_text(encoding="utf-8")
    connection = get_sqlite_connection()

    try:
        connection.executescript(sql)
        connection.commit()
        print("Tabla de SQLite preparada correctamente.")
    finally:
        connection.close()


def mostrar_alumno(alumno):
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
    alumnos = connector.get_students()

    print(f"\nTotal de alumnos: {len(alumnos)}")

    if not alumnos:
        print("No hay alumnos en la tabla.")
        return

    for i, alumno in enumerate(alumnos, start=1):
        print(f"\n--- Alumno {i} ---")
        mostrar_alumno(alumno)


def probar_sqlite_crud():
    connector = SQLiteConnector()

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
        print("\n========== PRUEBA CRUD SQLITE ==========")

        # Limpiar posibles restos de pruebas anteriores.
        connector.delete_student("TESTSQL001")
        connector.delete_student("TESTSQL002")

        print("\n1. ESTADO INICIAL")
        mostrar_todos_los_alumnos(connector)

        print("\n2. AÑADIR ALUMNO 1")
        connector.create_student(alumno1)
        mostrar_todos_los_alumnos(connector)

        print("\n3. AÑADIR ALUMNO 2")
        connector.create_student(alumno2)
        mostrar_todos_los_alumnos(connector)

        print("\n4. EDITAR ALUMNO 1")
        connector.update_student("TESTSQL001", alumno1_editado)
        mostrar_todos_los_alumnos(connector)

        # Comprobar que la edición se ha guardado.
        actualizados = connector.get_student("Harry Potter Editado")
        assert any(
            a.id == "TESTSQL001" and a.casa == "Slytherin"
            for a in actualizados
        ), "El alumno no se ha actualizado correctamente."

        print("\n5. BORRAR ALUMNO 1 POR ID")
        eliminado = connector.delete_student("TESTSQL001")
        assert eliminado, "No se ha eliminado el alumno por ID."
        mostrar_todos_los_alumnos(connector)

        print("\n6. BORRAR ALUMNO 2 POR NOMBRE")
        eliminados = connector.delete_student_by_name(
            "Hermione Granger Prueba"
        )
        assert eliminados >= 1, "No se ha eliminado el alumno por nombre."
        mostrar_todos_los_alumnos(connector)

        print("\nTODAS LAS PRUEBAS CRUD HAN FINALIZADO CORRECTAMENTE.")

    finally:
        connector.delete_student("TESTSQL001")
        connector.delete_student("TESTSQL002")


if __name__ == "__main__":
    ejecutar_script_sql()
    probar_sqlite_crud()