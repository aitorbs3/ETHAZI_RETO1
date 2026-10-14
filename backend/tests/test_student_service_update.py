
from models.student import Student
from services.student_service import StudentService
from connectors.sqlite_connector import get_sqlite_connection
from connectors.mariadb_connector import conectar_mariadb


NOMBRE_ORIGINAL = "Prueba Sync Actualizada 2026"
NOMBRE_NUEVO = "Prueba Sync Actualizada 2"


def test_actualizacion_y_sincronizacion():
    service = StudentService()

    # 1. Buscar al alumno en SQLite por su nombre actual.
    conn = get_sqlite_connection()
    try:
        fila = conn.execute(
            "SELECT * FROM alumnos WHERE LOWER(nombre) = LOWER(?)",
            (NOMBRE_ORIGINAL,),
        ).fetchone()
    finally:
        conn.close()

    if fila is None:
        raise RuntimeError(
            f"No se encuentra '{NOMBRE_ORIGINAL}' en SQLite. "
            "Comprueba el nombre actual del alumno."
        )

    datos = dict(fila)
    datos["nombre"] = NOMBRE_NUEVO
    alumno = Student(**datos)

    # 2. Actualizar mediante StudentService.
    actualizado = service.update_student(
        NOMBRE_ORIGINAL,
        alumno,
    )

    print("Alumno actualizado:", actualizado.nombre)
    print("UUID conservado:", actualizado.id)
    print("Resultado de sincronización:", service.ultima_sincronizacion)

    # 3. Verificar el cambio en SQLite.
    conn = get_sqlite_connection()
    try:
        local = conn.execute(
            "SELECT id, nombre FROM alumnos WHERE id = ?",
            (actualizado.id,),
        ).fetchone()
    finally:
        conn.close()

    assert local is not None, "El alumno no aparece en SQLite"
    assert local["nombre"] == NOMBRE_NUEVO, (
        "El nombre no se actualizó correctamente en SQLite"
    )
    assert local["id"] == actualizado.id, (
        "El UUID ha cambiado en SQLite"
    )

    # 4. Verificar el cambio en MariaDB.
    conn = conectar_mariadb()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre FROM alumnos WHERE id = %s",
                (actualizado.id,),
            )
            central = cursor.fetchone()
    finally:
        conn.close()

    assert central is not None, "El alumno no aparece en MariaDB"

    # PyMySQL devuelve una tupla por defecto.
    central_id, central_nombre = central

    assert str(central_id) == str(actualizado.id), (
        "El UUID no coincide en MariaDB"
    )
    assert central_nombre == NOMBRE_NUEVO, (
        "El nombre no se actualizó correctamente en MariaDB"
    )

    # 5. Comprobar que no quedan operaciones pendientes.
    conn = get_sqlite_connection()
    try:
        pendientes = conn.execute(
            "SELECT COUNT(*) FROM pending_operations"
        ).fetchone()[0]
    finally:
        conn.close()

    assert pendientes == 0, (
        f"Quedan {pendientes} operaciones pendientes en SQLite"
    )

    print(
        "Correcto: alumno actualizado en SQLite y MariaDB, "
        "UUID conservado y cola vacía."
    )


if __name__ == "__main__":
    test_actualizacion_y_sincronizacion()
