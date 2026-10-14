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


def mostrar_alumno(alumno):
    """Muestra todos los datos de un alumno."""

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
    """
    Consulta y muestra todos los alumnos de MariaDB.
    """

    alumnos = connector.get_students()

    print(f"\nTotal de alumnos: {len(alumnos)}")

    if not alumnos:
        print("No hay alumnos en la tabla.")
        return

    for i, alumno in enumerate(alumnos, start=1):
        print(f"\n--- Alumno {i} ---")
        mostrar_alumno(alumno)


def probar_mariadb_crud():
    """
    Prueba añadir, leer, editar y borrar alumnos en MariaDB.
    Muestra todos los alumnos después de cada operación.
    """

    connector = MariaDBConnector()

    alumno1 = Student(
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

    alumno1_editado = Student(
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

    alumno2 = Student(
        id="TEST002",
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
        print("\n========== PRUEBA CRUD MARIADB ==========")

        # Limpiar posibles restos de pruebas anteriores.
        connector.delete_student("TEST001")
        connector.delete_student("TEST002")

        # 1. LEER ALUMNOS
        print("\n1. LEER ALUMNOS")
        mostrar_todos_los_alumnos(connector)

        # 2. AÑADIR ALUMNO 1
        print("\n2. AÑADIR ALUMNO 1")
        connector.create_student(alumno1)
        print("Alumno 1 añadido correctamente.")
        mostrar_todos_los_alumnos(connector)

        encontrados = connector.get_student("Harry Potter Prueba")
        assert any(
            estudiante.id == "TEST001"
            for estudiante in encontrados
        ), "No se ha encontrado el alumno 1."

        # 3. AÑADIR ALUMNO 2
        print("\n3. AÑADIR ALUMNO 2")
        connector.create_student(alumno2)
        print("Alumno 2 añadido correctamente.")
        mostrar_todos_los_alumnos(connector)

        encontrados = connector.get_student("Hermione Granger Prueba")
        assert any(
            estudiante.id == "TEST002"
            for estudiante in encontrados
        ), "No se ha encontrado el alumno 2."

        # 4. EDITAR ALUMNO 1
        print("\n4. EDITAR ALUMNO 1")
        connector.update_student("TEST001", alumno1_editado)
        print("Alumno 1 editado correctamente.")
        mostrar_todos_los_alumnos(connector)

        actualizados = connector.get_student("Harry Potter Editado")
        assert any(
            estudiante.id == "TEST001"
            and estudiante.casa == "Slytherin"
            for estudiante in actualizados
        ), "Los cambios del alumno 1 no se han guardado."

        # 5. BORRAR ALUMNO 1 POR ID
        print("\n5. BORRAR ALUMNO 1 POR ID")
        eliminado = connector.delete_student("TEST001")
        assert eliminado, "No se ha eliminado el alumno 1 por ID."

        print("Alumno 1 eliminado correctamente por ID.")
        mostrar_todos_los_alumnos(connector)

        # Comprobar que el alumno 2 continúa en la tabla.
        restantes = connector.get_students()
        assert any(
            estudiante.id == "TEST002"
            for estudiante in restantes
        ), "El alumno 2 no debería haberse eliminado."

        # 6. BORRAR ALUMNO 2 POR NOMBRE
        print("\n6. BORRAR ALUMNO 2 POR NOMBRE")
        eliminados = connector.delete_student_by_name(
            "Hermione Granger Prueba"
        )

        assert eliminados >= 1, (
            "No se ha eliminado el alumno 2 por nombre."
        )

        print(f"Alumnos eliminados por nombre: {eliminados}")
        mostrar_todos_los_alumnos(connector)

        # Comprobar que ninguno de los dos sigue existiendo.
        restantes = connector.get_students()
        assert not any(
            estudiante.id in ("TEST001", "TEST002")
            for estudiante in restantes
        ), "Todavía queda algún alumno de prueba."

        print("\nTODAS LAS PRUEBAS CRUD HAN FINALIZADO CORRECTAMENTE.")

    finally:
        # Limpiar los registros de prueba si ocurre algún error.
        connector.delete_student("TEST001")
        connector.delete_student("TEST002")


if __name__ == "__main__":
    ejecutar_script_sql()
    probar_mariadb_crud()