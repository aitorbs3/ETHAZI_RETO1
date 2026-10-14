import json

from connectors.sqlite_connector import get_sqlite_connection


class PendingOperationsRepository:
    """
    Gestiona las operaciones pendientes de sincronizar con MariaDB.
    Todas las operaciones se identifican por el nombre del alumno.
    """

    def add_pending_operation(
        self,
        operation: str,
        nombre: str,
        payload: dict | None = None,
        nombre_editado: str | None = None,
    ) -> int:
        """
        Registra una operación pendiente.

        operation: CREATE, UPDATE o DELETE.
        nombre: nombre original del alumno.
        payload: datos del alumno en formato diccionario.
        nombre_editado: nuevo nombre si se modifica el nombre.
        """
        operation = operation.strip().upper()

        if operation not in {"CREATE", "UPDATE", "DELETE"}:
            raise ValueError(f"Operación no válida: {operation}")

        if not nombre or not nombre.strip():
            raise ValueError("El nombre del estudiante es obligatorio")

        if nombre_editado is not None and not nombre_editado.strip():
            raise ValueError("El nombre editado no puede estar vacío")

        if operation != "UPDATE" and nombre_editado is not None:
            raise ValueError(
                "nombre_editado solo se utiliza en operaciones UPDATE"
            )

        payload_json = (
            json.dumps(payload, ensure_ascii=False, default=str)
            if payload is not None
            else None
        )

        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                INSERT INTO pending_operations (
                    operation,
                    nombre,
                    nombre_editado,
                    payload
                )
                VALUES (?, ?, ?, ?)
                """,
                (
                    operation,
                    nombre.strip(),
                    nombre_editado.strip()
                    if nombre_editado is not None
                    else None,
                    payload_json,
                ),
            )

            connection.commit()
            return cursor.lastrowid

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_pending_operations(self) -> list[dict]:
        """
        Devuelve las operaciones pendientes de la más antigua
        a la más reciente.
        """
        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                SELECT
                    id,
                    operation,
                    nombre,
                    nombre_editado,
                    payload,
                    created_at,
                    attempts,
                    last_error
                FROM pending_operations
                ORDER BY id ASC
                """
            )

            rows = cursor.fetchall()
            operations = []

            for row in rows:
                operation = dict(row)

                if operation["payload"]:
                    operation["payload"] = json.loads(
                        operation["payload"]
                    )

                operations.append(operation)

            return operations

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def mark_attempt_failed(
        self,
        operation_id: int,
        error: str,
    ) -> bool:
        """
        Incrementa los intentos y guarda el último error.
        operation_id identifica la operación pendiente, no al alumno.
        """
        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                UPDATE pending_operations
                SET attempts = attempts + 1,
                    last_error = ?
                WHERE id = ?
                """,
                (str(error), operation_id),
            )

            connection.commit()
            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def delete_pending_operation(
        self,
        operation_id: int,
    ) -> bool:
        """
        Elimina una operación de la cola después de sincronizarla
        correctamente con MariaDB.
        operation_id identifica la operación pendiente.
        """
        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(
                """
                DELETE FROM pending_operations
                WHERE id = ?
                """,
                (operation_id,),
            )

            connection.commit()
            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()