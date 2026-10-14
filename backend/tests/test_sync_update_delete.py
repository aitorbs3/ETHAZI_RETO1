import json

from connectors.sqlite_connector import get_sqlite_connection
from connectors.mariadb_connector import MariaDBConnector
from backend.services.sync_service import SyncService


NOMBRE_ORIGINAL = "Alumno UUID Prueba"
NOMBRE_EDITADO = "Alumno UUID Prueba Editado"


def obtener_alumno_sqlite(nombre):
    conn = get_sqlite_connection()

    try:
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
        conn.close()


def obtener_alumno_mariadb(nombre):
    mariadb = MariaDBConnector()
    conn = mariadb._connect()
    cursor = conn.cursor()

    try:
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
        return cursor.fetchone()
    finally:
        cursor.close()
        conn.close()


def sincronizar_y_comprobar(tipo, nombre_esperado):
    resultado = SyncService().sincronizar_pendientes()

    print(f"\nResultado de sincronización {tipo}:")
    print(f"Procesadas: {resultado['procesadas']}")
    print(f"Fallidas: {resultado['fallidas']}")

    for detalle in resultado["detalles"]:
        print(detalle)

    if resultado["fallidas"] > 0:
        raise AssertionError(
            f"Hay operaciones fallidas durante la sincronización {tipo}. "
            "Revisa los detalles anteriores."
        )

    if not any(
        detalle["operacion"] == tipo
        and detalle["resultado"] == "Sincronizada"
        for detalle in resultado["detalles"]
    ):
        raise AssertionError(
            f"No se ha confirmado ninguna operación {tipo} sincronizada."
        )


def probar_update():
    print("\n========== PRUEBA UPDATE ==========")

    alumno = obtener_alumno_sqlite(NOMBRE_ORIGINAL)

    if alumno is None:
        raise RuntimeError(
            f"No existe '{NOMBRE_ORIGINAL}' en SQLite. "
            "Comprueba si ya ejecutaste una prueba anterior."
        )

    datos = dict(alumno)
    datos["nombre"] = NOMBRE_EDITADO
    datos["patronus"] = "Patronus de prueba actualizado"

    conn = get_sqlite_connection()

    try:
        conn.execute("BEGIN")

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

        if cursor.rowcount != 1:
            raise RuntimeError(
                "La actualización en SQLite no ha afectado exactamente "
                "a un alumno."
            )

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

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(f"Nombre anterior: {NOMBRE_ORIGINAL}")
    print(f"Nombre nuevo: {NOMBRE_EDITADO}")

    sincronizar_y_comprobar("UPDATE", NOMBRE_EDITADO)

    alumno_mariadb = obtener_alumno_mariadb(NOMBRE_EDITADO)

    if alumno_mariadb is None:
        raise AssertionError(
            "El alumno actualizado no aparece en MariaDB con su nuevo nombre."
        )

    print("\nAlumno actualizado en MariaDB:")
    print(f"UUID: {alumno_mariadb[0]}")
    print(f"Nombre: {alumno_mariadb[1]}")
    print(f"Patronus: {alumno_mariadb[7]}")

    if alumno_mariadb[7] != datos["patronus"]:
        raise AssertionError(
            "El patronus actualizado no coincide en MariaDB."
        )

    anterior = obtener_alumno_mariadb(NOMBRE_ORIGINAL)

    if anterior is not None:
        raise AssertionError(
            "El nombre anterior sigue existiendo en MariaDB."
        )

    print("PRUEBA UPDATE COMPLETADA CORRECTAMENTE.")


def probar_delete():
    print("\n========== PRUEBA DELETE ==========")

    alumno = obtener_alumno_sqlite(NOMBRE_EDITADO)

    if alumno is None:
        raise RuntimeError(
            f"No existe '{NOMBRE_EDITADO}' en SQLite."
        )

    conn = get_sqlite_connection()

    try:
        conn.execute("BEGIN")

        cursor = conn.execute(
            """
            DELETE FROM alumnos
            WHERE LOWER(nombre) = LOWER(?)
            """,
            (NOMBRE_EDITADO,),
        )

        if cursor.rowcount != 1:
            raise RuntimeError(
                "El borrado en SQLite no ha afectado exactamente "
                "a un alumno."
            )

        conn.execute(
            """
            INSERT INTO pending_operations (operation, nombre)
            VALUES (?, ?)
            """,
            ("DELETE", NOMBRE_EDITADO),
        )

        conn.commit()

    except Exception:
        conn.rollback()
        raise
    finally:
        conn.close()

    print(f"Alumno eliminado de SQLite: {NOMBRE_EDITADO}")

    sincronizar_y_comprobar("DELETE", NOMBRE_EDITADO)

    alumno_mariadb = obtener_alumno_mariadb(NOMBRE_EDITADO)

    if alumno_mariadb is not None:
        raise AssertionError(
            "El alumno sigue existiendo en MariaDB después del borrado."
        )

    alumno_sqlite = obtener_alumno_sqlite(NOMBRE_EDITADO)

    if alumno_sqlite is not None:
        raise AssertionError(
            "El alumno sigue existiendo en SQLite después del borrado."
        )

    print("Alumno eliminado de SQLite y MariaDB.")
    print("PRUEBA DELETE COMPLETADA CORRECTAMENTE.")


if __name__ == "__main__":
    probar_update()
    probar_delete()
    print("\nTODAS LAS PRUEBAS UPDATE Y DELETE HAN FINALIZADO.")