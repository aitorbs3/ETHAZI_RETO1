"""Pruebas de conservación local de cambios cuando MariaDB no responde."""

# Importar StudentCreate para validar y preparar los datos del nuevo alumno.
from models.student import StudentCreate

# Importar el servicio que gestiona los alumnos y su sincronización.
from services.student_service import StudentService

# Importar la función para conectarse a la base de datos SQLite local.
from connectors.sqlite_connector import get_sqlite_connection

# Importar la función para conectarse a la base de datos central MariaDB.
from connectors.mariadb_connector import conectar_mariadb


# Definir un nombre exclusivo para identificar al alumno de esta prueba.
NOMBRE = "Prueba Sync Recuperacion 2026"


def test_fallo_y_recuperacion():
    """Verifica que un fallo de MariaDB conserva la operación para reintentarla."""

    # Crear una instancia del servicio que gestiona las operaciones
    # de los alumnos y la sincronización entre las bases de datos.
    service = StudentService()

    # Comprobar que no existe previamente un alumno con el mismo nombre.
    # Así se evitan duplicados al ejecutar la prueba varias veces.
    conn = get_sqlite_connection()

    try:
        # Buscar el alumno en SQLite sin distinguir entre mayúsculas
        # y minúsculas.
        existente = conn.execute(
            "SELECT id FROM alumnos WHERE LOWER(nombre) = LOWER(?)",
            (NOMBRE,),
        ).fetchone()

    finally:
        # Cerrar la conexión después de consultar la base de datos.
        conn.close()

    # Si el alumno ya existe, detener la prueba para evitar duplicados.
    if existente:
        raise RuntimeError(
            f"Ya existe '{NOMBRE}'. Cambia NOMBRE antes de repetir."
        )

    # Guardar una referencia al método original de sincronización.
    # Después se restaurará para permitir la sincronización real.
    sincronizar_original = service.sync_service.sincronizar_pendientes

    def simular_fallo():
        """Simula que MariaDB no está disponible durante el primer intento."""

        # Lanzar una excepción para simular un error de conexión.
        # No se detiene ni se modifica el servicio real de MariaDB.
        raise ConnectionError("Fallo simulado: MariaDB no disponible")

    # Sustituir temporalmente el método de sincronización por la función
    # que simula el fallo de conexión.
    service.sync_service.sincronizar_pendientes = simular_fallo

    try:
        # Crear el objeto con los datos del alumno que se va a registrar.
        # StudentCreate permite preparar y validar los datos de entrada.
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

        # Crear el alumno mediante el servicio.
        # Se espera que se guarde localmente aunque falle la sincronización.
        creado = service.create_student(datos)

    finally:
        # Restaurar siempre el método original de sincronización.
        # De esta manera, el fallo simulado no afecta a las siguientes pruebas.
        service.sync_service.sincronizar_pendientes = sincronizar_original

    # Mostrar los datos principales del alumno que se ha creado.
    print("Alumno guardado en SQLite:", creado.nombre)
    print("UUID:", creado.id)

    # Comprobar que el alumno se conserva localmente y que existe
    # una operación pendiente para sincronizarlo posteriormente.
    conn = get_sqlite_connection()

    try:
        # Buscar el alumno en la tabla local utilizando su UUID.
        local = conn.execute(
            "SELECT id, nombre FROM alumnos WHERE id = ?",
            (creado.id,),
        ).fetchone()

        # Buscar la operación pendiente asociada al alumno.
        # Se comprueba que el sistema ha registrado el cambio pendiente.
        pendiente = conn.execute(
            """
            SELECT id, operation, student_id
            FROM pending_operations
            WHERE student_id = ?
            """,
            (creado.id,),
        ).fetchone()

    finally:
        # Cerrar la conexión después de las consultas.
        conn.close()

    # Verificar que el alumno se ha guardado en SQLite a pesar del fallo.
    assert local is not None, "El alumno no se guardó en SQLite"

    # Verificar que se ha registrado la operación pendiente de sincronización.
    assert pendiente is not None, "No se guardó la operación pendiente"

    # Mostrar el resultado de las comprobaciones locales.
    print("Correcto: el alumno sigue en SQLite.")
    print("Operación pendiente:", dict(pendiente))

    # Simular la recuperación de la conexión ejecutando de nuevo
    # el método original de sincronización.
    # Ahora el método ya no está sustituido por la función de fallo.
    resultado = service.sync_service.sincronizar_pendientes()

    # Mostrar el resultado devuelto por el proceso de sincronización.
    print("Resultado tras recuperar la conexión:", resultado)

    # Comprobar que ninguna operación ha fallado durante el reintento.
    assert resultado["fallidas"] == 0, (
        "Ha fallado alguna operación durante la recuperación"
    )

    # Verificar que el alumno se ha sincronizado con la base de datos central.
    conn = conectar_mariadb()

    try:
        # Abrir un cursor para consultar los datos del alumno en MariaDB.
        with conn.cursor() as cursor:

            # Buscar el alumno por su UUID en la tabla central.
            # En MariaDB se utiliza %s como marcador del parámetro.
            cursor.execute(
                "SELECT id, nombre FROM alumnos WHERE id = %s",
                (creado.id,),
            )

            # Recuperar el resultado de la consulta.
            central = cursor.fetchone()

    finally:
        # Cerrar la conexión con MariaDB después de la consulta.
        conn.close()

    # Comprobar que el alumno ya existe en la base de datos central.
    assert central is not None, "El alumno no llegó a MariaDB"

    # Verificar que el identificador de MariaDB coincide con el UUID local.
    # Se convierten ambos valores a texto para evitar diferencias de tipo.
    assert str(central[0]) == str(creado.id), "El UUID no coincide"

    # Comprobar que el nombre almacenado en MariaDB es el esperado.
    assert central[1] == NOMBRE, "El nombre no coincide"

    # Comprobar que la operación pendiente del alumno se ha eliminado
    # después de completar correctamente la sincronización.
    conn = get_sqlite_connection()

    try:
        # Contar las operaciones pendientes asociadas al UUID del alumno.
        pendiente_final = conn.execute(
            "SELECT COUNT(*) FROM pending_operations WHERE student_id = ?",
            (creado.id,),
        ).fetchone()[0]

    finally:
        # Cerrar la conexión con SQLite.
        conn.close()

    # Verificar que ya no quedan operaciones pendientes para este alumno.
    assert pendiente_final == 0, (
        "La operación sigue pendiente después de sincronizar"
    )

    # Mostrar el mensaje final si todas las comprobaciones han sido correctas.
    print(
        "Correcto: el alumno se conservó en SQLite durante el fallo, "
        "se sincronizó con MariaDB al recuperarse y la cola quedó vacía."
    )


# Comprobar si el archivo se está ejecutando directamente.
if __name__ == "__main__":

    # Ejecutar la prueba de fallo y recuperación de la sincronización.
    test_fallo_y_recuperacion()