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


def probar_sqlite_crud():
    connector = SQLiteConnector()

    alumno = Student(
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

    alumno_editado = Student(
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

    try:
        print("\n========== PRUEBA CRUD SQLITE ==========")

        print("\n1. LEER ALUMNOS")
        print(f"Alumnos encontrados: {len(connector.get_students())}")

        print("\n2. AÑADIR ALUMNO")
        connector.delete_student("TESTSQL001")
        connector.create_student(alumno)

        encontrados = connector.get_student("Harry Potter Prueba")
        assert any(a.id == "TESTSQL001" for a in encontrados)
        print("Alumno añadido y encontrado correctamente.")

        print("\n3. EDITAR ALUMNO")
        connector.update_student("TESTSQL001", alumno_editado)

        actualizados = connector.get_student("Harry Potter Editado")
        assert any(
            a.id == "TESTSQL001" and a.casa == "Slytherin"
            for a in actualizados
        )
        print("Alumno editado correctamente.")

        print("\n4. BORRAR POR ID")
        assert connector.delete_student("TESTSQL001")
        print("Alumno eliminado por ID.")

        print("\n5. BORRAR POR NOMBRE")
        connector.create_student(alumno)

        eliminados = connector.delete_student_by_name(
            "Harry Potter Prueba"
        )
        assert eliminados >= 1
        print(f"Alumnos eliminados por nombre: {eliminados}")

        print("\nTODAS LAS PRUEBAS CRUD HAN FINALIZADO CORRECTAMENTE.")

    finally:
        connector.delete_student("TESTSQL001")


if __name__ == "__main__":
    ejecutar_script_sql()
    probar_sqlite_crud()