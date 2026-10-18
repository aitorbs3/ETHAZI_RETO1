"""
Descripción: Gestiona la persistencia local en SQLite de la cola de cambios pendientes 
de sincronización con la base de datos central MariaDB. Permite registrar altas (CREATE), 
modificaciones (UPDATE) y borrados (DELETE) en escenarios offline o cuando la base central no está disponible.
"""

import json

from connectors.sqlite_connector import get_sqlite_connection


class PendingOperationsRepository:
    """
    ========================================================================
    CLASE: PendingOperationsRepository (Gestor de Cola de Sincronización)
    ========================================================================
    Implementa el patrón Repository para aislar la lógica de acceso a datos de la cola 
    de operaciones pendientes almacenada en la tabla local 'pending_operations' de SQLite.
    Garantiza la tolerancia a fallos y la persistencia de cambios ante caídas de red o de MariaDB.
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
        Registra una nueva operación pendiente de sincronización en la base de datos local SQLite.

        Args:
            operation (str): Tipo de operación ('CREATE', 'UPDATE' o 'DELETE').
            nombre (str): Nombre original del alumno afectado.
            payload (dict | None): Datos completos del alumno en formato diccionario (para CREATE/UPDATE).
            nombre_editado (str | None): Nuevo nombre del alumno en caso de que sea un UPDATE.
            student_id (str | None): Identificador único universal (UUID) del alumno.

        Returns:
            int: El identificador numérico autoincremental (`lastrowid`) de la operación registrada en la cola.

        Raises:
            ValueError: Si la operación no es válida, faltan datos obligatorios o hay inconsistencias en los parámetros.
        """
        # 1. Normalización del tipo de operación (convertir a mayúsculas y eliminar espacios en blanco)
        operation = operation.strip().upper()

        # Validación estricta: la operación debe pertenecer al conjunto permitido por el sistema
        if operation not in {"CREATE", "UPDATE", "DELETE"}:
            raise ValueError(f"Operación no válida: {operation}. Debe ser CREATE, UPDATE o DELETE.")

        # Validación defensiva: el nombre es obligatorio en cualquier operación sobre alumnos
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del estudiante es obligatorio")

        # Validación específica para UPDATE: el nombre editado no puede estar vacío si se proporciona
        if nombre_editado is not None and not nombre_editado.strip():
            raise ValueError("El nombre editado no puede estar vacío")

        # Validación de coherencia de negocio: 'nombre_editado' solo tiene sentido en actualizaciones
        if operation != "UPDATE" and nombre_editado is not None:
            raise ValueError(
                "El parámetro 'nombre_editado' solo se utiliza en operaciones de tipo UPDATE"
            )

        # Resolución automática del UUID: si no se pasa explícitamente pero existe un payload,
        # intentamos extraer el 'id' directamente de él (patrón común en CREATE y UPDATE).
        if not student_id and payload:
            student_id = payload.get("id")

        # Validación final de identificador: toda operación de sincronización requiere un UUID de alumno válido
        if not student_id:
            raise ValueError(
                "El UUID del alumno (student_id) es obligatorio para registrar la operación pendiente."
            )

        # Serialización a JSON: guardar el payload como cadena JSON permite almacenar estructuras complejas 
        # en SQLite (que no tiene tipo nativo Diccionario) y reconstruir el objeto al reintentar la sincronización.
        payload_json = (
            json.dumps(payload, ensure_ascii=False, default=str)
            if payload is not None
            else None
        )

        # Abrimos la conexión a la base de datos local SQLite utilizando el helper centralizado
        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            
            # Persistencia inmediata en la tabla 'pending_operations'. 
            # La operación se guarda localmente antes de intentar cualquier sincronización remota, 
            # asegurando que no se pierda si el proceso se interrumpe de forma inesperada.
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

            # Confirmamos la transacción (Commit) de manera atómica en la base de datos local
            connection.commit()
            
            # Devolvemos el ID numérico autoincremental de la operación insertada en la cola
            return cursor.lastrowid

        except Exception:
            # Si ocurre cualquier error imprevisto, revertimos la transacción (Rollback) para evitar estados corruptos
            connection.rollback()
            raise

        finally:
            # Bloque de limpieza garantizada: cerramos el cursor y la conexión para liberar recursos del sistema operativo
            if cursor is not None:
                cursor.close()
            connection.close()

    def get_pending_operations(self) -> list[dict]:
        """
        Recupera todas las operaciones pendientes de sincronización almacenadas en la cola local,
        ordenadas cronológicamente de la más antigua a la más reciente (orden FIFO: First In, First Out).

        Returns:
            list[dict]: Lista de diccionarios con el detalle de cada operación pendiente.
        """
        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            
            # Consultamos la tabla ordenando por ID ascendente (ORDER BY id ASC) para respetar rigurosamente 
            # la secuencia temporal en la que se produjeron los cambios del usuario.
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
                # Convertimos cada fila de resultado (sqlite3.Row) a un diccionario estándar de Python
                operation = dict(row)

                # Si la operación almacena un payload en formato JSON string, lo deserializamos de vuelta a diccionario
                if operation["payload"]:
                    operation["payload"] = json.loads(
                        operation["payload"]
                    )

                # Retrocompatibilidad (Legacy): si operaciones antiguas CREATE/UPDATE contenían el UUID 
                # dentro del payload pero no tenían relleno el campo dedicado 'student_id', lo rescatamos al vuelo.
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
        """
        Registra un fallo en el intento de sincronización de una operación específica,
        incrementando el contador de intentos y actualizando el mensaje del último error registrado.

        Args:
            operation_id (int): Identificador de la operación pendiente en la cola.
            error (str): Descripción o traza del error devuelto al intentar sincronizar con MariaDB.

        Returns:
            bool: True si se actualizó correctamente el registro, False en caso contrario.
        """
        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            
            # Actualizamos la fila incrementando en 1 el contador de intentos (attempts = attempts + 1)
            # y guardando el mensaje de error para labores de auditoría, depuración y control de reintentos.
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
            
            # rowcount > 0 comprueba si realmente existía una operación con ese ID y se modificó con éxito
            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def delete_pending_operation(self, operation_id: int) -> bool:
        """
        Elimina una operación de la cola local tras haberse sincronizado exitosamente con la base central MariaDB.

        Args:
            operation_id (int): Identificador de la operación completada.

        Returns:
            bool: True si la operación fue eliminada con éxito de la tabla, False si no se encontró.
        """
        connection = get_sqlite_connection()
        cursor = None

        try:
            cursor = connection.cursor()
            
            # Esta instrucción DELETE solo se ejecuta cuando el cambio remoto en MariaDB 
            # se ha aplicado y confirmado satisfactoriamente, garantizando la consistencia eventual del sistema.
            cursor.execute(
                """
                DELETE FROM pending_operations
                WHERE id = ?
                """,
                (operation_id,),
            )

            connection.commit()
            
            # Verificamos que se haya eliminado al menos una fila en la tabla
            return cursor.rowcount > 0

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()