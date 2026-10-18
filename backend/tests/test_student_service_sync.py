"""Pruebas de creación de alumnos y vaciado de la cola de sincronización."""

# Importar StudentCreate para crear y validar los datos de entrada del alumno.
from models.student import StudentCreate

# Importar el servicio que gestiona la creación de alumnos y su sincronización.
from services.student_service import StudentService

# Importar la función que permite conectarse a la base de datos SQLite local.
from connectors.sqlite_connector import get_sqlite_connection

# Importar la función que permite conectarse a la base de datos central MariaDB.
from connectors.mariadb_connector import conectar_mariadb


def test_creacion_y_sincronizacion():
    """Comprueba que crear un alumno encola y sincroniza la operación."""

    # Definir el nombre del alumno que se utilizará en esta prueba.
    nombre = "Prueba Sync Automatica 2026"

    # Crear una instancia del servicio encargado de gestionar los alumnos.
    service = StudentService()

    # Comprobar si ya existe un alumno con el mismo nombre en SQLite.
    # Esto evita insertar registros duplicados al repetir la prueba.
    conn = get_sqlite_connection()

    existente = conn.execute(
        "SELECT id FROM alumnos WHERE LOWER(nombre) = LOWER(?)",
        (nombre,),
    ).fetchone()

    # Cerrar la conexión después de realizar la consulta.
    conn.close()

    # Si el alumno ya existe, detener la prueba e indicar cómo continuar.
    if existente:
        raise RuntimeError(
            f"Ya existe '{nombre}' en SQLite. "
            "Cambia el nombre de prueba antes de continuar."
        )

    # Crear el objeto StudentCreate con los datos del nuevo alumno.
    # Los campos opcionales que no tienen valor se inicializan con None.
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

    # Crear el alumno a través del servicio.
    # Se espera que el alumno se guarde en SQLite y que se intente
    # sincronizar la operación con la base de datos central.
    creado = service.create_student(datos)

    # Mostrar los datos principales del alumno y el resultado
    # de la última operación de sincronización.
    print("Alumno creado en SQLite:", creado.nombre)
    print("UUID:", creado.id)
    print("Resultado de sincronización:", service.ultima_sincronizacion)

    # Comprobar que el alumno se ha guardado correctamente en SQLite.
    # Se utiliza el UUID generado para identificar el registro.
    conn = get_sqlite_connection()

    local = conn.execute(
        "SELECT id, nombre FROM alumnos WHERE id = ?",
        (creado.id,),
    ).fetchone()

    # Cerrar la conexión una vez recuperado el registro.
    conn.close()

    # Si la consulta no devuelve ningún resultado, el alumno no existe
    # en la base de datos local y la prueba debe fallar.
    assert local is not None, "El alumno no aparece en SQLite"

    # Comprobar que el alumno también se encuentra en MariaDB.
    # Esto permite verificar que los datos se han propagado a la base central.
    conn = conectar_mariadb()

    try:
        # Abrir un cursor para ejecutar la consulta SQL en MariaDB.
        with conn.cursor() as cursor:

            # Buscar al alumno utilizando su UUID.
            # En esta consulta se utiliza %s como marcador del parámetro.
            cursor.execute(
                "SELECT id, nombre FROM alumnos WHERE id = %s",
                (creado.id,),
            )

            # Recuperar el registro encontrado, o None si no existe.
            central = cursor.fetchone()

    finally:
        # Cerrar la conexión incluso si se produce un error en la consulta.
        conn.close()

    # Comprobar que el alumno existe en la base de datos central.
    assert central is not None, "El alumno no aparece en MariaDB"

    # Informar de que las comprobaciones de existencia han sido satisfactorias.
    print("Correcto: el alumno existe en SQLite y MariaDB.")


# Comprobar si el archivo se está ejecutando directamente.
if __name__ == "__main__":

    # Ejecutar la prueba de creación y sincronización del alumno.
    test_creacion_y_sincronizacion()