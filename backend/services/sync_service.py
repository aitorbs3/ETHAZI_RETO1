"""
Descripción: Orquesta la sincronización ordenada y resiliente de la cola de cambios locales
pendientes en SQLite hacia la base de datos central MariaDB (Consistencia Eventual / Patrón Offline-First).
"""

from connectors.mariadb_connector import MariaDBConnector, init_mariadb_db
from repositories.pending_operations_repository import (
    PendingOperationsRepository,
)
from models.student import Student


class SyncService:
    """
    Clase encargada de gestionar el ciclo de sincronización de la cola local 
    con el servidor remoto centralizado de MariaDB.
    """

    def __init__(self):
        """
        Construye las instancias del repositorio de la cola local y del conector MariaDB.
        """
        # Encapsulamos el acceso a la tabla local de SQLite de operaciones pendientes
        self.pending_repository = PendingOperationsRepository()
        # Encapsulamos el conector y las operaciones CRUD contra la base de datos central MariaDB
        self.mariadb = MariaDBConnector()

    def sincronizar_pendientes(self) -> dict:
        """
        Procesa secuencialmente la cola de operaciones pendientes y aplica los cambios en MariaDB.

        Returns:
            dict: Diccionario con estadísticas del resultado (procesadas, fallidas y detalles por operación).
        """
        # Recuperamos todas las operaciones pendientes almacenadas localmente en SQLite ordenadas por ID (FIFO)
        operaciones = self.pending_repository.get_pending_operations()

        # Si existen operaciones pendientes en la cola, inicializamos la conexión y esquema con MariaDB
        if operaciones:
            init_mariadb_db()

        # Estructura de control para almacenar métricas y el estado detallado de cada intento de sincronización
        resultado = {
            "procesadas": 0,
            "fallidas": 0,
            "detalles": [],
        }

        # Iteramos ordenadamente sobre cada operación de la cola para mantener la secuencia lógica de cambios
        for operacion in operaciones:
            operation_id = operacion["id"]

            try:
                # Cada operación se procesa de forma aislada en un bloque try-except independiente.
                # Esto garantiza que si una operación falla (ej. caída puntual de red), 
                # el error no interrumpa ni bloquee el procesamiento del resto de la cola.
                self._ejecutar_operacion(
                    tipo=operacion["operation"],
                    student_id=operacion.get("student_id"),
                    payload=operacion.get("payload"),
                )

                # Si la operación remota en MariaDB se aplica con éxito, eliminamos el registro de la cola local en SQLite
                self.pending_repository.delete_pending_operation(
                    operation_id
                )

                # Actualizamos las métricas de éxito y registramos el detalle
                resultado["procesadas"] += 1
                resultado["detalles"].append(
                    {
                        "id_operacion": operation_id,
                        "resultado": "Sincronizada",
                    }
                )

            except Exception as error:
                # Si ocurre un fallo o excepción con MariaDB, dejamos la operación en la cola local 
                # incrementando los intentos e informando el error para permitir un reintento futuro (resiliencia).
                self.pending_repository.mark_attempt_failed(
                    operation_id,
                    str(error),
                )

                # Actualizamos las métricas de error y guardamos el detalle con el motivo del fallo
                resultado["fallidas"] += 1
                resultado["detalles"].append(
                    {
                        "id_operacion": operation_id,
                        "resultado": "Pendiente",
                        "error": str(error),
                    }
                )

        return resultado

    def _ejecutar_operacion(
        self,
        tipo: str,
        student_id: str | None,
        payload,
    ):
        """
        Aplica una operación de tipo CREATE, UPDATE o DELETE directamente en la base de datos MariaDB.

        Args:
            tipo (str): Tipo de operación ('CREATE', 'UPDATE', 'DELETE').
            student_id (str | None): Identificador único universal (UUID) del alumno afectado.
            payload: Datos adicionales del alumno en formato diccionario (requerido para altas y modificaciones).
        """
        # Normalizamos el tipo de operación convirtiéndolo a mayúsculas
        tipo = tipo.upper()

        # Validación defensiva: toda operación en la cola debe apuntar obligatoriamente a un alumno mediante su UUID
        if not student_id:
            raise ValueError(
                "La operación pendiente no tiene un student_id válido asignado."
            )

        # Las operaciones CREATE y UPDATE exigen obligatoriamente que se proporcione el paquete de datos (payload)
        if tipo in {"CREATE", "UPDATE"} and not payload:
            raise ValueError(
                f"La operación de tipo {tipo} no contiene los datos del alumno (payload)."
            )

        # Enrutamiento según el tipo de acción requerida:
        if tipo == "CREATE":
            # Convertimos el payload a diccionario y aseguramos que contenga el identificador correcto
            datos = dict(payload)
            datos["id"] = student_id

            # Validamos y construimos el modelo Pydantic Student y lo persistimos en MariaDB
            estudiante = Student(**datos)
            self.mariadb.create_student(estudiante)

        elif tipo == "UPDATE":
            # Preparamos los datos actualizados asociando el UUID correspondiente
            datos = dict(payload)
            datos["id"] = student_id

            estudiante = Student(**datos)
            # Ejecutamos la actualización en la base central
            self.mariadb.update_student(
                student_id,
                estudiante,
            )

        elif tipo == "DELETE":
            # Solicitamos el borrado del alumno en MariaDB mediante su identificador
            eliminado = self.mariadb.delete_student(student_id)

            if not eliminado:
                # Tolerancia a fallos idempotente: si el registro ya había sido eliminado previamente en MariaDB 
                # (por ejemplo, en una sincronización anterior incompleta antes de borrar la cola), 
                # consideramos el objetivo cumplido y retornamos sin lanzar error.
                return

        else:
            # Si el tipo de comando no es reconocido, lanzamos una excepción descriptiva
            raise ValueError(
                f"Tipo de operación desconocido en la lógica de sincronización: {tipo}"
            )