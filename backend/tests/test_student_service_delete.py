"""Pruebas de borrado de alumnos y sincronización de la operación."""

# Importar el servicio encargado de gestionar las operaciones sobre alumnos.
from services.student_service import StudentService

# Importar la función que permite conectarse a la base de datos SQLite local.
from connectors.sqlite_connector import get_sqlite_connection

# Importar la función que permite conectarse a la base de datos central MariaDB.
from connectors.mariadb_connector import conectar_mariadb


# Definir el nombre del alumno que se utilizará para realizar la prueba.
NOMBRE_ALUMNO = "Prueba Sync Actualizada 2"


def test_borrado_y_sincronizacion():
    """Comprueba el borrado local y la propagación del cambio a MariaDB."""

    # Crear una instancia del servicio que gestiona la eliminación del alumno
    # y la sincronización de los cambios entre las bases de datos.
    service = StudentService()

    # 1. Comprobar que el alumno existe en la base de datos SQLite local.
    # Abrir una conexión para buscar al alumno por su nombre.
    conn = get_sqlite_connection()

    try:
        # Buscar el alumno ignorando las diferencias entre mayúsculas
        # y minúsculas. Se utiliza un parámetro para pasar el nombre
        # de forma segura a la consulta SQL.
        local = conn.execute(
            "SELECT id, nombre FROM alumnos "
            "WHERE LOWER(nombre) = LOWER(?)",
            (NOMBRE_ALUMNO,),
        ).fetchone()

    finally:
        # Cerrar la conexión incluso si se produce un error en la consulta.
        conn.close()

    # Si no se encuentra el alumno, detener la prueba e indicar el motivo.
    if local is None:
        raise RuntimeError(
            f"No se encuentra '{NOMBRE_ALUMNO}' en SQLite."
        )

    # Guardar el UUID del alumno antes de eliminarlo.
    # Este identificador permitirá comprobar su ausencia en ambas bases de datos.
    uuid_alumno = local["id"]

    # 2. Eliminar el alumno utilizando el servicio y su nombre.
    # El servicio se encarga de gestionar el borrado y la sincronización.
    eliminado = service.delete_student(NOMBRE_ALUMNO)

    # Comprobar que el servicio confirma que el alumno se ha eliminado.
    assert eliminado, "El servicio no confirmó el borrado"

    # Mostrar información sobre la eliminación y el resultado
    # de la última operación de sincronización.
    print("Alumno eliminado:", NOMBRE_ALUMNO)
    print("UUID:", uuid_alumno)
    print("Resultado de sincronización:", service.ultima_sincronizacion)

    # 3. Comprobar que el alumno ya no existe en SQLite.
    # Buscarlo por UUID, que es más preciso que utilizar el nombre.
    conn = get_sqlite_connection()

    try:
        local_despues = conn.execute(
            "SELECT id FROM alumnos WHERE id = ?",
            (uuid_alumno,),
        ).fetchone()

    finally:
        # Cerrar la conexión después de realizar la consulta.
        conn.close()

    # Si la consulta devuelve un registro, el alumno sigue existiendo.
    # La prueba falla si no se ha eliminado correctamente.
    assert local_despues is None, (
        "El alumno sigue existiendo en SQLite"
    )

    # 4. Comprobar que el alumno también se ha eliminado de MariaDB.
    # Esta es la base de datos central con la que se sincronizan los cambios.
    conn = conectar_mariadb()

    try:
        # Abrir un cursor para ejecutar consultas SQL sobre MariaDB.
        with conn.cursor() as cursor:

            # Buscar al alumno por su UUID en la tabla central.
            # En este conector se utiliza %s como marcador de parámetros.
            cursor.execute(
                "SELECT id FROM alumnos WHERE id = %s",
                (uuid_alumno,),
            )

            # Recuperar el resultado de la consulta.
            central_despues = cursor.fetchone()

    finally:
        # Cerrar la conexión con MariaDB al finalizar la comprobación.
        conn.close()

    # Verificar que el alumno tampoco existe en la base de datos central.
    assert central_despues is None, (
        "El alumno sigue existiendo en MariaDB"
    )

    # 5. Comprobar que no quedan operaciones pendientes de sincronización.
    # Abrir una conexión a SQLite para consultar la cola de operaciones.
    conn = get_sqlite_connection()

    try:
        # COUNT(*) devuelve el número total de operaciones pendientes.
        # Se obtiene directamente el primer valor de la fila devuelta.
        pendientes = conn.execute(
            "SELECT COUNT(*) FROM pending_operations"
        ).fetchone()[0]

    finally:
        # Cerrar la conexión después de consultar la cola.
        conn.close()

    # Comprobar que todas las operaciones pendientes se han procesado.
    # Si queda alguna, mostrar cuántas siguen pendientes.
    assert pendientes == 0, (
        f"Quedan {pendientes} operaciones pendientes"
    )

    # Mostrar un mensaje final si todas las comprobaciones han sido correctas.
    print(
        "Correcto: alumno eliminado de SQLite y MariaDB, "
        "y cola vacía."
    )


# Comprobar si el archivo se está ejecutando directamente.
if __name__ == "__main__":

    # Ejecutar la prueba completa de borrado y sincronización.
    test_borrado_y_sincronizacion()