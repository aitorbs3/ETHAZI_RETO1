import json

from connectors.sqlite_connector import get_sqlite_connection


class PendingOperationsRepository:
    """
    Gestiona las operaciones pendientes de sincronizar con MariaDB.
    Cada operación identifica al alumno mediante su UUID (student_id).
    """

    def add_pending_operation(
        self,
        operation: str,
        nombre: str,
        payload: dict | None = None,
        nombre_editado: str | None = None,
        student_id: str | None = None,
    ) -> int:
        """
        Registra una operación pendiente.

        operation: CREATE, UPDATE o DELETE.
        nombre: nombre original del alumno.
        payload: datos del alumno en formato diccionario.
        nombre_editado: nuevo nombre si se modifica.
        student_id: UUID del alumno afectado.
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

        # Si no se proporciona explícitamente, intenta recuperar el UUID
        # del payload, que debe contenerlo en CREATE y UPDATE.
        if not student_id and payload:
            student_id = payload.get("id")

        if not student_id:
            raise ValueError(
                "El UUID del alumno (student_id) es obligatorio."
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
                    student_id,
                    nombre,
                    nombre_editado,
                    payload
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    operation,
                    student_id,
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
        a la más reciente, incluyendo el UUID del alumno.
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
                    student_id,
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

                # Compatibilidad con operaciones CREATE/UPDATE antiguas
                # cuyo payload ya contenía el UUID, pero no lo guardaron
                # en la columna student_id.
                if not operation.get("student_id") and operation.get("payload"):
                    operation["student_id"] = operation["payload"].get("id")

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
        """Incrementa los intentos y guarda el último error."""
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

    def delete_pending_operation(self, operation_id: int) -> bool:
        """Elimina una operación después de sincronizarla correctamente."""
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