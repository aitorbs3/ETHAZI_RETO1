
from models.student import StudentCreate
from services.student_service import StudentService
from connectors.sqlite_connector import get_sqlite_connection
from connectors.mariadb_connector import conectar_mariadb


NOMBRE = "Prueba Sync Recuperacion 2026"


def test_fallo_y_recuperacion():
    service = StudentService()

    # Evitar duplicados.
    conn = get_sqlite_connection()
    try:
        existente = conn.execute(
            "SELECT id FROM alumnos WHERE LOWER(nombre) = LOWER(?)",
            (NOMBRE,),
        ).fetchone()
    finally:
        conn.close()

    if existente:
        raise RuntimeError(
            f"Ya existe '{NOMBRE}'. Cambia NOMBRE antes de repetir."
        )

    # Simular un fallo de sincronización sin parar MariaDB.
    sincronizar_original = service.sync_service.sincronizar_pendientes

    def simular_fallo():
        raise ConnectionError("Fallo simulado: MariaDB no disponible")

    service.sync_service.sincronizar_pendientes = simular_fallo

    try:
        datos = StudentCreate(
            nombre=NOMBRE,
            casa="Hogwarts",
            especie="Humano",
            genero="Masculino",
            nacimiento=None,
            nacionalidad="Británica",
            patronus=None,
            imagen=None,
        )

        creado = service.create_student(datos)
    finally:
        # Restaurar el método original siempre.
        service.sync_service.sincronizar_pendientes = sincronizar_original

    print("Alumno guardado en SQLite:", creado.nombre)
    print("UUID:", creado.id)

    # Comprobar que SQLite conserva el alumno y la operación pendiente.
    conn = get_sqlite_connection()
    try:
        local = conn.execute(
            "SELECT id, nombre FROM alumnos WHERE id = ?",
            (creado.id,),
        ).fetchone()

        pendiente = conn.execute(
            """
            SELECT id, operation, student_id
            FROM pending_operations
            WHERE student_id = ?
            """,
            (creado.id,),
        ).fetchone()
    finally:
        conn.close()

    assert local is not None, "El alumno no se guardó en SQLite"
    assert pendiente is not None, "No se guardó la operación pendiente"

    print("Correcto: el alumno sigue en SQLite.")
    print("Operación pendiente:", dict(pendiente))

    # Simular la recuperación: intentar sincronizar normalmente.
    resultado = service.sync_service.sincronizar_pendientes()
    print("Resultado tras recuperar la conexión:", resultado)

    assert resultado["fallidas"] == 0, (
        "Ha fallado alguna operación durante la recuperación"
    )

    # Verificar que el alumno existe en MariaDB.
    conn = conectar_mariadb()
    try:
        with conn.cursor() as cursor:
            cursor.execute(
                "SELECT id, nombre FROM alumnos WHERE id = %s",
                (creado.id,),
            )
            central = cursor.fetchone()
    finally:
        conn.close()

    assert central is not None, "El alumno no llegó a MariaDB"
    assert str(central[0]) == str(creado.id), "El UUID no coincide"
    assert central[1] == NOMBRE, "El nombre no coincide"

    # Comprobar que la cola vuelve a quedar vacía.
    conn = get_sqlite_connection()
    try:
        pendiente_final = conn.execute(
            "SELECT COUNT(*) FROM pending_operations WHERE student_id = ?",
            (creado.id,),
        ).fetchone()[0]
    finally:
        conn.close()

    assert pendiente_final == 0, (
        "La operación sigue pendiente después de sincronizar"
    )

    print(
        "Correcto: el alumno se conservó en SQLite durante el fallo, "
        "se sincronizó con MariaDB al recuperarse y la cola quedó vacía."
    )


if __name__ == "__main__":
    test_fallo_y_recuperacion()
