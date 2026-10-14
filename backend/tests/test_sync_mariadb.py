from connectors.sqlite_connector import get_sqlite_connection
from connectors.mariadb_connector import MariaDBConnector
from backend.services.sync_service import SyncService


NOMBRE_PRUEBA = "Alumno UUID Prueba"


def probar_sincronizacion_mariadb():
    print("\n========== PRUEBA DE SINCRONIZACIÓN ==========")

    # 1. Comprobar que el alumno existe en SQLite.
    sqlite_conn = get_sqlite_connection()

    try:
        alumno = sqlite_conn.execute(
            """
            SELECT id, nombre
            FROM alumnos
            WHERE nombre = ?
            """,
            (NOMBRE_PRUEBA,),
        ).fetchone()

        if alumno is None:
            raise RuntimeError(
                f"No existe '{NOMBRE_PRUEBA}' en SQLite. "
                "Ejecuta primero test_student_creation_sync."
            )

        student_id = alumno["id"]

        pendiente = sqlite_conn.execute(
            """
            SELECT id, operation, student_id
            FROM pending_operations
            WHERE operation = 'CREATE'
              AND student_id = ?
            ORDER BY id DESC
            LIMIT 1
            """,
            (student_id,),
        ).fetchone()

        print(f"Alumno en SQLite: {alumno['nombre']}")
        print(f"UUID: {student_id}")

        if pendiente is None:
            print(
                "No hay una operación CREATE pendiente para este alumno. "
                "Se comprobará si ya está sincronizado en MariaDB."
            )
        else:
            print(
                f"Operación pendiente encontrada: {pendiente['id']}"
            )

    finally:
        sqlite_conn.close()

    # 2. Ejecutar el servicio de sincronización.
    if pendiente is not None:
        print("\nEjecutando SyncService...")

        servicio = SyncService()
        resultado = servicio.sincronizar_pendientes()

        print("\nResultado de sincronización:")
        print(f"Procesadas: {resultado['procesadas']}")
        print(f"Fallidas: {resultado['fallidas']}")

        for detalle in resultado["detalles"]:
            print(detalle)

    # 3. Comprobar que el alumno existe en MariaDB.
    mariadb = MariaDBConnector()
    connection = mariadb._connect()
    cursor = connection.cursor()

    try:
        cursor.execute(
            """
            SELECT id, nombre
            FROM alumnos
            WHERE id = %s
            """,
            (student_id,),
        )

        alumno_mariadb = cursor.fetchone()

        if alumno_mariadb is None:
            raise AssertionError(
                "El alumno no aparece en MariaDB. "
                "Comprueba los errores de sincronización y la conexión."
            )

        # PyMySQL devuelve tuplas por defecto.
        id_mariadb, nombre_mariadb = alumno_mariadb

        if str(id_mariadb) != str(student_id):
            raise AssertionError(
                "El UUID de MariaDB no coincide con el de SQLite."
            )

        print("\nAlumno verificado en MariaDB:")
        print(f"UUID: {id_mariadb}")
        print(f"Nombre: {nombre_mariadb}")

    finally:
        cursor.close()
        connection.close()

    # 4. Comprobar que la operación ya no está pendiente.
    sqlite_conn = get_sqlite_connection()

    try:
        pendiente_final = sqlite_conn.execute(
            """
            SELECT id
            FROM pending_operations
            WHERE operation = 'CREATE'
              AND student_id = ?
            """,
            (student_id,),
        ).fetchone()

        if pendiente_final is not None:
            raise AssertionError(
                "El alumno está en MariaDB, pero sigue existiendo "
                "una operación CREATE pendiente en SQLite."
            )

    finally:
        sqlite_conn.close()

    print("\nPRUEBA COMPLETADA CORRECTAMENTE.")
    print("El alumno existe en SQLite y MariaDB.")
    print("El UUID se ha conservado.")
    print("La operación CREATE ya no está pendiente.")


if __name__ == "__main__":
    probar_sincronizacion_mariadb()