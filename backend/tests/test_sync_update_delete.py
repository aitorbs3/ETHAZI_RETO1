"""Pruebas de sincronización y consistencia para actualizaciones y borrados."""

# Importar json para convertir el diccionario con los datos del alumno
# en una cadena JSON que pueda almacenarse en la cola de sincronización.
import json

# Importar la función que permite conectarse a la base de datos local SQLite.
from connectors.sqlite_connector import get_sqlite_connection

# Importar el conector para acceder a la base de datos central MariaDB.
from connectors.mariadb_connector import MariaDBConnector

# Importar el servicio que procesa las operaciones pendientes de sincronización.
from backend.services.sync_service import SyncService


# Nombre inicial del alumno que se utilizará en las pruebas.
NOMBRE_ORIGINAL = "Alumno UUID Prueba"

# Nuevo nombre que se asignará al alumno durante la prueba UPDATE.
NOMBRE_EDITADO = "Alumno UUID Prueba Editado"


def obtener_alumno_sqlite(nombre):
    """Busca en SQLite una fila por nombre sin mantener abierta la conexión."""

    # Abrir una conexión local para consultar los datos del alumno.
    # Utilizar una conexión independiente para cada consulta evita mantenerla
    # abierta más tiempo del necesario.
    conn = get_sqlite_connection()

    try:
        # Buscar al alumno por su nombre.
        # LOWER() permite comparar los nombres sin distinguir entre
        # mayúsculas y minúsculas.
        # El marcador ? permite pasar el nombre como parámetro de SQLite.
        # Se recuperan todos los campos necesarios para reconstruir el alumno.
        return conn.execute(
            """
            SELECT
                id, nombre, casa, especie, genero, nacimiento,
                nacionalidad, patronus, imagen
            FROM alumnos
            WHERE LOWER(nombre) = LOWER(?)
            """,
            (nombre,),
        ).fetchone()

    finally:
        # Cerrar la conexión tanto si la consulta funciona como si se produce
        # una excepción.
        conn.close()


def obtener_alumno_mariadb(nombre):
    """Busca en MariaDB una fila por nombre y cierra sus recursos."""

    # Crear el conector de MariaDB y abrir una conexión con la base central.
    # Esta consulta permite comprobar el estado remoto del alumno.
    mariadb = MariaDBConnector()
    conn = mariadb._connect()

    # Crear un cursor para ejecutar consultas SQL en MariaDB.
    cursor = conn.cursor()

    try:
        # Buscar al alumno por su nombre, ignorando las diferencias
        # entre mayúsculas y minúsculas.
        # En PyMySQL, el marcador %s se utiliza para pasar parámetros.
        cursor.execute(
            """
            SELECT
                id, nombre, casa, especie, genero, nacimiento,
                nacionalidad, patronus, imagen
            FROM alumnos
            WHERE LOWER(nombre) = LOWER(%s)
            """,
            (nombre,),
        )

        # Devolver la primera fila encontrada.
        # Si no existe ningún alumno con ese nombre, devuelve None.
        return cursor.fetchone()

    finally:
        # Cerrar primero el cursor y después la conexión para liberar
        # los recursos utilizados por MariaDB.
        cursor.close()
        conn.close()


def sincronizar_y_comprobar(tipo, nombre_esperado):
    """Ejecuta la cola y falla si la operación esperada no se sincroniza."""

    # Ejecutar el servicio que procesa las operaciones almacenadas
    # en pending_operations y trata de sincronizarlas con MariaDB.
    resultado = SyncService().sincronizar_pendientes()

    # Mostrar un resumen de las operaciones procesadas.
    print(f"\nResultado de sincronización {tipo}:")
    print(f"Procesadas: {resultado['procesadas']}")
    print(f"Fallidas: {resultado['fallidas']}")

    # Mostrar los detalles devueltos por el servicio para conocer
    # el resultado de cada operación procesada.
    for detalle in resultado["detalles"]:
        print(detalle)

    # Si el servicio informa de operaciones fallidas, detener la prueba.
    # Así se evita considerar correcta una sincronización con errores.
    if resultado["fallidas"] > 0:
        raise AssertionError(
            f"Hay operaciones fallidas durante la sincronización {tipo}. "
            "Revisa los detalles anteriores."
        )

    # Comprobar que entre los detalles exista una operación del tipo esperado
    # cuyo resultado sea exactamente "Sincronizada".
    # any() devuelve True si al menos un elemento cumple ambas condiciones.
    if not any(
        detalle["operacion"] == tipo
        and detalle["resultado"] == "Sincronizada"
        for detalle in resultado["detalles"]
    ):
        # Si no se encuentra una operación confirmada, la prueba falla.
        raise AssertionError(
            f"No se ha confirmado ninguna operación {tipo} sincronizada."
        )


def probar_update():
    """Prepara y valida una actualización pendiente para un alumno de prueba."""

    # Mostrar un encabezado para identificar la prueba UPDATE.
    print("\n========== PRUEBA UPDATE ==========")

    # Buscar al alumno por su nombre original en SQLite.
    alumno = obtener_alumno_sqlite(NOMBRE_ORIGINAL)

    # No se puede actualizar el alumno si no existe en la base local.
    if alumno is None:
        raise RuntimeError(
            f"No existe '{NOMBRE_ORIGINAL}' en SQLite. "
            "Comprueba si ya ejecutaste una prueba anterior."
        )

    # Convertir la fila obtenida en un diccionario.
    # De esta manera se pueden modificar campos concretos sin perder
    # los demás datos del alumno.
    # El UUID se conserva porque no se modifica el campo id.
    datos = dict(alumno)

    # Cambiar el nombre y el patronus para comprobar que ambos campos
    # se actualizan correctamente en la base central.
    datos["nombre"] = NOMBRE_EDITADO
    datos["patronus"] = "Patronus de prueba actualizado"

    # Abrir una conexión con SQLite para modificar el alumno y registrar
    # la operación pendiente dentro de una misma transacción.
    conn = get_sqlite_connection()

    try:
        # Iniciar una transacción explícita.
        # Los cambios no se confirmarán hasta ejecutar conn.commit().
        conn.execute("BEGIN")

        # Actualizar el nombre y el patronus del alumno en SQLite.
        # La condición utiliza el nombre original para localizarlo.
        cursor = conn.execute(
            """
            UPDATE alumnos
            SET nombre = ?, patronus = ?
            WHERE LOWER(nombre) = LOWER(?)
            """,
            (
                NOMBRE_EDITADO,
                datos["patronus"],
                NOMBRE_ORIGINAL,
            ),
        )

        # rowcount indica cuántas filas ha modificado la consulta.
        # Se exige exactamente una para evitar actualizar cero alumnos
        # o modificar varios registros por error.
        if cursor.rowcount != 1:
            raise RuntimeError(
                "La actualización en SQLite no ha afectado exactamente "
                "a un alumno."
            )

        # Registrar la operación UPDATE en la cola de sincronización.
        # El servicio utilizará esta información para reproducir el cambio
        # en MariaDB.
        # payload almacena los datos completos del alumno en formato JSON.
        # ensure_ascii=False conserva correctamente los caracteres Unicode.
        # default=str permite convertir a texto valores no serializables
        # directamente por JSON, como determinados tipos de fecha.
        conn.execute(
            """
            INSERT INTO pending_operations
                (operation, nombre, nombre_editado, payload)
            VALUES (?, ?, ?, ?)
            """,
            (
                "UPDATE",
                NOMBRE_ORIGINAL,
                NOMBRE_EDITADO,
                json.dumps(datos, ensure_ascii=False, default=str),
            ),
        )

        # Confirmar la actualización del alumno y la inserción en la cola.
        # Ambas operaciones se guardan como una única transacción local.
        conn.commit()

    except Exception:
        # Si se produce un error, deshacer los cambios de esta transacción.
        # Así se evita guardar la actualización sin registrar su operación
        # pendiente, o viceversa.
        conn.rollback()

        # Volver a lanzar la excepción para que el error no quede oculto.
        raise

    finally:
        # Cerrar la conexión después de completar o revertir la transacción.
        conn.close()

    # Mostrar los nombres anterior y nuevo para facilitar el seguimiento.
    print(f"Nombre anterior: {NOMBRE_ORIGINAL}")
    print(f"Nombre nuevo: {NOMBRE_EDITADO}")

    # Ejecutar la sincronización y comprobar que se ha confirmado
    # una operación UPDATE.
    sincronizar_y_comprobar("UPDATE", NOMBRE_EDITADO)

    # Consultar MariaDB para comprobar que el alumno aparece con su
    # nuevo nombre después de la sincronización.
    alumno_mariadb = obtener_alumno_mariadb(NOMBRE_EDITADO)

    # Si no se encuentra, la actualización no se refleja correctamente
    # en la base de datos central.
    if alumno_mariadb is None:
        raise AssertionError(
            "El alumno actualizado no aparece en MariaDB con su nuevo nombre."
        )

    # Mostrar los datos principales del alumno recuperado de MariaDB.
    # PyMySQL devuelve una tupla por defecto.
    # Según el SELECT anterior, el orden es:
    # 0: id, 1: nombre, 2: casa, 3: especie, 4: genero,
    # 5: nacimiento, 6: nacionalidad, 7: patronus, 8: imagen.
    print("\nAlumno actualizado en MariaDB:")
    print(f"UUID: {alumno_mariadb[0]}")
    print(f"Nombre: {alumno_mariadb[1]}")
    print(f"Patronus: {alumno_mariadb[7]}")

    # Comprobar que el patronus de MariaDB coincide con el valor actualizado.
    if alumno_mariadb[7] != datos["patronus"]:
        raise AssertionError(
            "El patronus actualizado no coincide en MariaDB."
        )

    # Comprobar que el nombre anterior ya no existe en MariaDB.
    # Esto permite detectar si la actualización ha creado un registro nuevo
    # en lugar de modificar el registro existente.
    anterior = obtener_alumno_mariadb(NOMBRE_ORIGINAL)

    if anterior is not None:
        raise AssertionError(
            "El nombre anterior sigue existiendo en MariaDB."
        )

    # Informar de que todas las comprobaciones de UPDATE han terminado bien.
    print("PRUEBA UPDATE COMPLETADA CORRECTAMENTE.")


def probar_delete():
    """Prepara y valida un borrado pendiente para un alumno de prueba."""

    # Mostrar un encabezado para identificar la prueba DELETE.
    print("\n========== PRUEBA DELETE ==========")

    # Comprobar que el alumno actualizado existe en SQLite antes de borrarlo.
    # Esto garantiza que la prueba parte del estado esperado tras UPDATE.
    alumno = obtener_alumno_sqlite(NOMBRE_EDITADO)

    # Si el alumno no existe, no hay ningún registro que borrar.
    if alumno is None:
        raise RuntimeError(
            f"No existe '{NOMBRE_EDITADO}' en SQLite."
        )

    # Abrir una conexión local para borrar el alumno y registrar
    # la operación pendiente en una misma transacción.
    conn = get_sqlite_connection()

    try:
        # Iniciar una transacción explícita.
        # El borrado y la inserción en la cola se confirmarán conjuntamente.
        conn.execute("BEGIN")

        # Eliminar el alumno de SQLite utilizando su nombre actualizado.
        cursor = conn.execute(
            """
            DELETE FROM alumnos
            WHERE LOWER(nombre) = LOWER(?)
            """,
            (NOMBRE_EDITADO,),
        )

        # Comprobar que se ha eliminado exactamente un registro.
        # Si no se elimina ninguno o se eliminan varios, se considera un error.
        if cursor.rowcount != 1:
            raise RuntimeError(
                "El borrado en SQLite no ha afectado exactamente "
                "a un alumno."
            )

        # Registrar el borrado en la cola de sincronización.
        # Aunque el alumno ya no exista en SQLite, esta operación conserva
        # la información necesaria para solicitar su eliminación en MariaDB.
        conn.execute(
            """
            INSERT INTO pending_operations (operation, nombre)
            VALUES (?, ?)
            """,
            ("DELETE", NOMBRE_EDITADO),
        )

        # Confirmar conjuntamente el borrado local y el registro pendiente.
        conn.commit()

    except Exception:
        # Si ocurre un error durante el borrado o el registro de la operación,
        # revertir los cambios para conservar la consistencia local.
        conn.rollback()

        # Propagar el error para que pueda identificarse el fallo.
        raise

    finally:
        # Cerrar la conexión con SQLite.
        conn.close()

    # Informar de que el alumno se ha eliminado de la base local.
    print(f"Alumno eliminado de SQLite: {NOMBRE_EDITADO}")

    # Procesar las operaciones pendientes y comprobar que se ha confirmado
    # una operación DELETE.
    sincronizar_y_comprobar("DELETE", NOMBRE_EDITADO)

    # Comprobar que el alumno ya no existe en MariaDB.
    alumno_mariadb = obtener_alumno_mariadb(NOMBRE_EDITADO)

    if alumno_mariadb is not None:
        raise AssertionError(
            "El alumno sigue existiendo en MariaDB después del borrado."
        )

    # Comprobar también que el alumno ya no existe en SQLite.
    alumno_sqlite = obtener_alumno_sqlite(NOMBRE_EDITADO)

    if alumno_sqlite is not None:
        raise AssertionError(
            "El alumno sigue existiendo en SQLite después del borrado."
        )

    # Mostrar el resultado de las comprobaciones del borrado.
    print("Alumno eliminado de SQLite y MariaDB.")
    print("PRUEBA DELETE COMPLETADA CORRECTAMENTE.")


# Ejecutar las dos pruebas en orden cuando este archivo se ejecute directamente.
# Primero se actualiza el alumno y después se elimina.
if __name__ == "__main__":
    probar_update()
    probar_delete()

    # Este mensaje solo se muestra si ambas funciones terminan sin excepciones.
    print("\nTODAS LAS PRUEBAS UPDATE Y DELETE HAN FINALIZADO.")