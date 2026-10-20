"""Pruebas de sincronización de operaciones pendientes con MariaDB."""

# Importar la función para conectarse a la base de datos local SQLite.
from connectors.sqlite_connector import get_sqlite_connection

# Importar el conector que permite acceder a la base de datos central MariaDB.
from connectors.mariadb_connector import MariaDBConnector

# Importar el servicio encargado de procesar las operaciones pendientes
# y sincronizarlas con la base de datos central.
from backend.services.sync_service import SyncService


# Nombre del alumno que se utilizará para realizar la prueba.
# Este alumno debe existir previamente en SQLite.
NOMBRE_PRUEBA = "Alumno UUID Prueba"


def probar_sincronizacion_mariadb():
    """Ejecuta una sincronización manual e imprime su resultado."""

    # Mostrar un encabezado para identificar la prueba en la consola.
    print("\n========== PRUEBA DE SINCRONIZACIÓN ==========")

    # 1. Comprobar que el alumno existe en SQLite.
    # SQLite actúa como base de datos local de la aplicación.
    sqlite_conn = get_sqlite_connection()

    try:
        # Buscar el identificador y el nombre del alumno.
        # El signo ? es el marcador de parámetros utilizado por SQLite.
        # Se pasa el nombre como parámetro para evitar construir la consulta
        # concatenando directamente el valor dentro del SQL.
        alumno = sqlite_conn.execute(
            """
            SELECT id, nombre
            FROM alumnos
            WHERE nombre = ?
            """,
            (NOMBRE_PRUEBA,),
        ).fetchone()

        # Si no existe el alumno, detener la prueba e indicar
        # qué prueba debe ejecutarse previamente.
        if alumno is None:
            raise RuntimeError(
                f"No existe '{NOMBRE_PRUEBA}' en SQLite. "
                "Ejecuta primero test_student_creation_sync."
            )

        # Guardar el UUID del alumno para utilizarlo en las consultas
        # posteriores y comprobar que se conserva entre las dos bases de datos.
        student_id = alumno["id"]

        # Buscar la operación CREATE más reciente asociada a este alumno.
        # CREATE representa una operación de creación.
        # Se consulta la cola pending_operations para comprobar si queda
        # alguna operación de creación pendiente de sincronizar.
        # ORDER BY id DESC prioriza la operación con el identificador mayor.
        # LIMIT 1 devuelve únicamente la primera coincidencia.
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

        # Mostrar los datos del alumno encontrado en la base local.
        print(f"Alumno en SQLite: {alumno['nombre']}")
        print(f"UUID: {student_id}")

        # Informar de si existe una operación de creación pendiente.
        if pendiente is None:
            # Si no hay ninguna operación pendiente, no es necesario
            # ejecutar la sincronización para este CREATE.
            # La prueba continuará comprobando si el alumno ya existe
            # en MariaDB.
            print(
                "No hay una operación CREATE pendiente para este alumno. "
                "Se comprobará si ya está sincronizado en MariaDB."
            )
        else:
            # Mostrar el identificador de la operación pendiente encontrada.
            print(
                f"Operación pendiente encontrada: {pendiente['id']}"
            )

    finally:
        # Cerrar la conexión con SQLite tanto si la consulta funciona
        # como si se produce una excepción.
        sqlite_conn.close()

    # 2. Ejecutar el servicio de sincronización únicamente si se ha
    # encontrado una operación CREATE pendiente para el alumno.
    if pendiente is not None:
        print("\nEjecutando SyncService...")

        # Crear una instancia del servicio de sincronización.
        servicio = SyncService()

        # Procesar las operaciones pendientes mediante el método del servicio.
        # Se espera que devuelva un resultado con el número de operaciones
        # procesadas, las fallidas y los detalles de ejecución.
        resultado = servicio.sincronizar_pendientes()

        # Mostrar un resumen del resultado de la sincronización.
        print("\nResultado de sincronización:")
        print(f"Procesadas: {resultado['procesadas']}")
        print(f"Fallidas: {resultado['fallidas']}")

        # Mostrar el detalle de cada operación informado por el servicio.
        for detalle in resultado["detalles"]:
            print(detalle)

    # 3. Comprobar que el alumno existe en MariaDB.
    # MariaDB es la base de datos central con la que se sincroniza SQLite.
    mariadb = MariaDBConnector()

    # Abrir una conexión utilizando el método interno del conector.
    connection = mariadb._connect()

    # Crear un cursor para ejecutar consultas SQL en MariaDB.
    cursor = connection.cursor()

    try:
        # Buscar al alumno por su UUID.
        # En PyMySQL, el marcador %s se utiliza para pasar parámetros
        # a la consulta de forma segura.
        cursor.execute(
            """
            SELECT id, nombre
            FROM alumnos
            WHERE id = %s
            """,
            (student_id,),
        )

        # Recuperar la primera fila del resultado.
        alumno_mariadb = cursor.fetchone()

        # Si el alumno no existe en MariaDB, la prueba debe fallar.
        # Esto puede indicar que la sincronización no se ha completado
        # correctamente o que existe un problema de conexión o configuración.
        if alumno_mariadb is None:
            raise AssertionError(
                "El alumno no aparece en MariaDB. "
                "Comprueba los errores de sincronización y la conexión."
            )

        # PyMySQL devuelve tuplas por defecto.
        # Como la consulta selecciona id y nombre, la tupla contiene
        # primero el identificador y después el nombre.
        id_mariadb, nombre_mariadb = alumno_mariadb

        # Comparar los UUID como cadenas para evitar diferencias de tipo
        # entre el identificador obtenido de SQLite y el de MariaDB.
        if str(id_mariadb) != str(student_id):
            raise AssertionError(
                "El UUID de MariaDB no coincide con el de SQLite."
            )

        # Mostrar los datos del alumno verificado en la base central.
        print("\nAlumno verificado en MariaDB:")
        print(f"UUID: {id_mariadb}")
        print(f"Nombre: {nombre_mariadb}")

    finally:
        # Cerrar primero el cursor y después la conexión con MariaDB,
        # incluso si alguna comprobación genera una excepción.
        cursor.close()
        connection.close()

    # 4. Comprobar que la operación CREATE ya no está pendiente en SQLite.
    sqlite_conn = get_sqlite_connection()

    try:
        # Buscar si todavía existe alguna operación CREATE asociada
        # al UUID del alumno.
        # Si fetchone() devuelve una fila, la operación sigue pendiente.
        # Si devuelve None, no se encuentra ninguna coincidencia.
        pendiente_final = sqlite_conn.execute(
            """
            SELECT id
            FROM pending_operations
            WHERE operation = 'CREATE'
              AND student_id = ?
            """,
            (student_id,),
        ).fetchone()

        # Si sigue existiendo una operación pendiente, la prueba falla.
        # Esto evita dar por completada la sincronización solo porque
        # el alumno aparezca en MariaDB.
        if pendiente_final is not None:
            raise AssertionError(
                "El alumno está en MariaDB, pero sigue existiendo "
                "una operación CREATE pendiente en SQLite."
            )

    finally:
        # Cerrar la conexión local después de comprobar la cola.
        sqlite_conn.close()

    # Mostrar el mensaje final únicamente si todas las comprobaciones
    # anteriores se han completado sin errores.
    print("\nPRUEBA COMPLETADA CORRECTAMENTE.")
    print("El alumno existe en SQLite y MariaDB.")
    print("El UUID se ha conservado.")
    print("La operación CREATE ya no está pendiente.")


# Ejecutar la prueba únicamente cuando el archivo se ejecuta directamente.
# Si se importa desde otro módulo, la función no se ejecutará automáticamente.
if __name__ == "__main__":
    probar_sincronizacion_mariadb()