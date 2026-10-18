"""Pruebas de actualización local y sincronización posterior con MariaDB."""

# Importar el modelo Student, que representa los datos de un alumno.
from models.student import Student

# Importar el servicio encargado de gestionar las operaciones sobre los alumnos
# y coordinar su sincronización entre las bases de datos.
from services.student_service import StudentService

# Importar la función que permite conectarse a la base de datos local SQLite.
from connectors.sqlite_connector import get_sqlite_connection

# Importar la función que permite conectarse a la base de datos central MariaDB.
from connectors.mariadb_connector import conectar_mariadb


# Nombre que tiene inicialmente el alumno que se va a actualizar.
NOMBRE_ORIGINAL = "Prueba Sync Actualizada 2026"

# Nuevo nombre que se asignará al alumno durante la prueba.
NOMBRE_NUEVO = "Prueba Sync Actualizada 2"


def test_actualizacion_y_sincronizacion():
    """Comprueba la actualización local y su sincronización con MariaDB."""

    # Crear una instancia del servicio que gestiona las operaciones con alumnos.
    service = StudentService()

    # 1. Buscar al alumno en SQLite utilizando su nombre actual.
    # LOWER() permite comparar los nombres sin distinguir entre mayúsculas
    # y minúsculas.
    conn = get_sqlite_connection()
    try:
        fila = conn.execute(
            "SELECT * FROM alumnos WHERE LOWER(nombre) = LOWER(?)",
            (NOMBRE_ORIGINAL,),
        ).fetchone()
    finally:
        # Cerrar la conexión incluso si la consulta produce un error.
        conn.close()

    # Si no se encuentra el alumno, detener la prueba e indicar el motivo.
    if fila is None:
        raise RuntimeError(
            f"No se encuentra '{NOMBRE_ORIGINAL}' en SQLite. "
            "Comprueba el nombre actual del alumno."
        )

    # Convertir la fila obtenida en un diccionario para acceder a sus campos
    # mediante sus nombres, por ejemplo, datos["nombre"].
    datos = dict(fila)

    # Modificar únicamente el nombre del alumno.
    # El resto de sus datos, incluido el identificador, se conservan.
    datos["nombre"] = NOMBRE_NUEVO

    # Crear un objeto Student a partir de los datos del diccionario.
    # El operador ** desempaqueta el diccionario y pasa cada campo
    # como un argumento con nombre al constructor de Student.
    alumno = Student(**datos)

    # 2. Actualizar el alumno mediante el servicio.
    # Se proporciona el nombre original para localizarlo y el objeto
    # Student con los datos actualizados.
    # El servicio se encarga de realizar la actualización y gestionar
    # la sincronización con MariaDB según su implementación.
    actualizado = service.update_student(
        NOMBRE_ORIGINAL,
        alumno,
    )

    # Mostrar información sobre el resultado de la operación.
    print("Alumno actualizado:", actualizado.nombre)

    # Mostrar el UUID para comprobar que el identificador se conserva.
    print("UUID conservado:", actualizado.id)

    # Mostrar el resultado que el servicio haya registrado para la sincronización.
    print("Resultado de sincronización:", service.ultima_sincronizacion)

    # 3. Verificar que el alumno se ha actualizado correctamente en SQLite.
    conn = get_sqlite_connection()
    try:
        # Buscar al alumno por su identificador único.
        # Se utiliza el UUID en lugar del nombre porque el nombre ha cambiado.
        local = conn.execute(
            "SELECT id, nombre FROM alumnos WHERE id = ?",
            (actualizado.id,),
        ).fetchone()
    finally:
        # Cerrar la conexión local después de realizar la consulta.
        conn.close()

    # Comprobar que el alumno sigue existiendo en SQLite.
    assert local is not None, "El alumno no aparece en SQLite"

    # Comprobar que el nombre almacenado coincide con el nuevo nombre.
    assert local["nombre"] == NOMBRE_NUEVO, (
        "El nombre no se actualizó correctamente en SQLite"
    )

    # Comprobar que el identificador del alumno no ha cambiado.
    assert local["id"] == actualizado.id, (
        "El UUID ha cambiado en SQLite"
    )

    # 4. Verificar que el cambio también se ha aplicado en MariaDB.
    conn = conectar_mariadb()
    try:
        # Abrir un cursor para ejecutar consultas SQL en MariaDB.
        with conn.cursor() as cursor:
            # Buscar el alumno por su UUID.
            # En PyMySQL, el marcador %s se utiliza para pasar parámetros
            # de forma segura a la consulta.
            cursor.execute(
                "SELECT id, nombre FROM alumnos WHERE id = %s",
                (actualizado.id,),
            )

            # Recuperar la primera fila del resultado.
            central = cursor.fetchone()
    finally:
        # Cerrar la conexión con MariaDB incluso si ocurre un error.
        conn.close()

    # Comprobar que el alumno existe en la base de datos central.
    assert central is not None, "El alumno no aparece en MariaDB"

    # PyMySQL devuelve una tupla por defecto cuando no se configura
    # para devolver diccionarios.
    # La tupla contiene primero el UUID y después el nombre.
    central_id, central_nombre = central

    # Comparar los UUID como cadenas para evitar diferencias de tipo,
    # por ejemplo, entre un UUID almacenado como texto y otro como objeto.
    assert str(central_id) == str(actualizado.id), (
        "El UUID no coincide en MariaDB"
    )

    # Comprobar que MariaDB contiene el nombre actualizado.
    assert central_nombre == NOMBRE_NUEVO, (
        "El nombre no se actualizó correctamente en MariaDB"
    )

    # 5. Comprobar que la cola local de sincronización está vacía.
    # La tabla pending_operations almacena las operaciones que todavía
    # están pendientes de sincronizar, según el diseño del proyecto.
    conn = get_sqlite_connection()
    try:
        # COUNT(*) devuelve el número total de operaciones pendientes.
        # fetchone()[0] obtiene el primer valor de la fila devuelta.
        pendientes = conn.execute(
            "SELECT COUNT(*) FROM pending_operations"
        ).fetchone()[0]
    finally:
        # Cerrar la conexión con SQLite.
        conn.close()

    # Asegurarse de que no quedan operaciones pendientes.
    # Si el número es distinto de cero, se muestra cuántas quedan.
    assert pendientes == 0, (
        f"Quedan {pendientes} operaciones pendientes en SQLite"
    )

    # Mostrar el mensaje final únicamente si todas las comprobaciones
    # anteriores se han superado.
    print(
        "Correcto: alumno actualizado en SQLite y MariaDB, "
        "UUID conservado y cola vacía."
    )


# Ejecutar la prueba únicamente cuando este archivo se ejecute directamente.
# Si se importa desde otro módulo, la prueba no se ejecutará automáticamente.
if __name__ == "__main__":
    test_actualizacion_y_sincronizacion()