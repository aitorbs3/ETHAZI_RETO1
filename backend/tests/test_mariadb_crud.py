from datetime import date
from pathlib import Path

from connectors.mariadb_connector import (
    MariaDBConnector,
    conectar_mariadb,
)
from backend.models.student import Student


def ejecutar_script_sql():
    """
    Ejecuta el script SQL para crear la tabla antes de las pruebas.
    """

    base_dir = Path(__file__).resolve().parents[2]
    sql_file = (
        base_dir
        / "data"
        / "sql"
        / "mariadb"
        / "crear_tabla_mariadb.sql"
    )

    if not sql_file.exists():
        raise FileNotFoundError(
            f"No se encuentra el script SQL: {sql_file}"
        )

    sql = sql_file.read_text(encoding="utf-8")

    connection = conectar_mariadb()
    cursor = None

    try:
        cursor = connection.cursor()
        cursor.execute(sql)
        connection.commit()

        print("Tabla de MariaDB preparada correctamente.")

    except Exception:
        connection.rollback()
        raise

    finally:
        if cursor is not None:
            cursor.close()
        connection.close()


def probar_mariadb_crud():
    """
    Prueba las funciones de añadir, leer, editar y borrar
    estudiantes en MariaDB.
    """

    connector = MariaDBConnector()

    alumno = Student(
        id="TEST001",
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
        id="TEST001",
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
        print("\n========== PRUEBA CRUD MARIADB ==========")

        # 1. LEER
        print("\n1. LEER ALUMNOS")

        alumnos = connector.get_students()
        print(f"Alumnos encontrados: {len(alumnos)}")

        # 2. AÑADIR
        print("\n2. AÑADIR ALUMNO")

        # Evita errores si quedó un registro de una ejecución anterior.
        connector.delete_student("TEST001")

        connector.create_student(alumno)
        print("Alumno añadido correctamente.")

        encontrados = connector.get_student("Harry Potter Prueba")

        assert any(
            estudiante.id == "TEST001"
            for estudiante in encontrados
        ), "No se ha encontrado el alumno añadido."

        print(f"Alumno encontrado: {encontrados}")

        # 3. EDITAR
        print("\n3. EDITAR ALUMNO")

        connector.update_student("TEST001", alumno_editado)

        actualizados = connector.get_student("Harry Potter Editado")

        assert any(
            estudiante.id == "TEST001"
            and estudiante.casa == "Slytherin"
            for estudiante in actualizados
        ), "Los cambios del alumno no se han guardado."

        print(f"Alumno actualizado: {actualizados}")

        # 4. BORRAR POR ID
        print("\n4. BORRAR ALUMNO POR ID")

        eliminado = connector.delete_student("TEST001")

        assert eliminado, "No se ha eliminado el alumno por ID."

        restantes = connector.get_students()

        assert not any(
            estudiante.id == "TEST001"
            for estudiante in restantes
        ), "El alumno sigue existiendo después de borrarlo."

        print("Alumno eliminado correctamente por ID.")

        # 5. BORRAR POR NOMBRE
        print("\n5. BORRAR ALUMNO POR NOMBRE")

        connector.create_student(alumno)

        eliminados = connector.delete_student_by_name(
            "Harry Potter Prueba"
        )

        assert eliminados >= 1, (
            "No se ha eliminado el alumno por nombre."
        )

        print(f"Alumnos eliminados por nombre: {eliminados}")

        print("\nTODAS LAS PRUEBAS HAN FINALIZADO CORRECTAMENTE.")

    finally:
        # Limpieza por si alguna prueba falla antes del borrado.
        connector.delete_student("TEST001")


if __name__ == "__main__":
    ejecutar_script_sql()
    probar_mariadb_crud()