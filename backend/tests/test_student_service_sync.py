from models.student import StudentCreate
from services.student_service import StudentService
from connectors.sqlite_connector import get_sqlite_connection
from connectors.mariadb_connector import conectar_mariadb


def test_creacion_y_sincronizacion():
    nombre = "Prueba Sync Automatica 2026"
    service = StudentService()

    # Evitar duplicados si ya se ejecutó la prueba.
    conn = get_sqlite_connection()
    existente = conn.execute(
        "SELECT id FROM alumnos WHERE LOWER(nombre) = LOWER(?)",
        (nombre,),
    ).fetchone()
    conn.close()

    if existente:
        raise RuntimeError(
            f"Ya existe '{nombre}' en SQLite. "
            "Cambia el nombre de prueba antes de continuar."
        )

    datos = StudentCreate(
        nombre=nombre,
        casa="Hogwarts",
        especie="Humano",
        genero="Masculino",
        nacimiento=None,
        nacionalidad="Británica",
        patronus=None,
        imagen=None,
    )

    # Crear a través del servicio: SQLite primero y sincronización después.
    creado = service.create_student(datos)
    print("Alumno creado en SQLite:", creado.nombre)
    print("UUID:", creado.id)
    print("Resultado de sincronización:", service.ultima_sincronizacion)

    # Verificar SQLite.
    conn = get_sqlite_connection()
    local = conn.execute(
        "SELECT id, nombre FROM alumnos WHERE id = ?",
        (creado.id,),
    ).fetchone()
    conn.close()

    assert local is not None, "El alumno no aparece en SQLite"

    # Verificar MariaDB.
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

    assert central is not None, "El alumno no aparece en MariaDB"
    print("Correcto: el alumno existe en SQLite y MariaDB.")


if __name__ == "__main__":
    test_creacion_y_sincronizacion()