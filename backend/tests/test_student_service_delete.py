
from services.student_service import StudentService
from connectors.sqlite_connector import get_sqlite_connection
from connectors.mariadb_connector import conectar_mariadb


NOMBRE_ALUMNO = "Prueba Sync Actualizada 2"


def test_borrado_y_sincronizacion():
    service = StudentService()

    # 1. Comprobar que el alumno existe en SQLite.
    conn = get_sqlite_connection()
    try:
        local = conn.execute(
            "SELECT id, nombre FROM alumnos "
            "WHERE LOWER(nombre) = LOWER(?)",
            (NOMBRE_ALUMNO,),
        ).fetchone()
    finally:
        conn.close()

    if local is None:
        raise RuntimeError(
            f"No se encuentra '{NOMBRE_ALUMNO}' en SQLite."
        )

    uuid_alumno = local["id"]

    # 2. Eliminar mediante el servicio, buscando por nombre.
    eliminado = service.delete_student(NOMBRE_ALUMNO)

    assert eliminado, "El servicio no confirmó el borrado"

    print("Alumno eliminado:", NOMBRE_ALUMNO)
    print("UUID:", uuid_alumno)
    print("Resultado de sincronización:", service.ultima_sincronizacion)

    # 3. Comprobar que ya no existe en SQLite.
    conn = get_sqlite_connection()
    try:
        local_despues = conn.execute(
            "SELECT id FROM alumnos WHERE id = ?",
            (uuid_alumno,),
        ).fetchone()
    finally:
        conn.close()

    assert local_despues is None, (
        "El alumno sigue existiendo en SQLite"
    )

    # 4. Comprobar que ya no existe en MariaDB.
    conn = conectar_mariadb()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id FROM alumnos WHERE id = %s",
                (uuid_alumno,),
            )
            central_despues = cursor.fetchone()
    finally:
        conn.close()

    assert central_despues is None, (
        "El alumno sigue existiendo en MariaDB"
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
        f"Quedan {pendientes} operaciones pendientes"
    )

    print(
        "Correcto: alumno eliminado de SQLite y MariaDB, "
        "y cola vacía."
    )


if __name__ == "__main__":
    test_borrado_y_sincronizacion()
