from connectors.mariadb_connector import MariaDBConnector, init_mariadb_db
from repositories.pending_operations_repository import (
    PendingOperationsRepository,
)
from models.student import Student


class SyncService:
    def __init__(self):
        self.pending_repository = PendingOperationsRepository()
        self.mariadb = MariaDBConnector()

    def sincronizar_pendientes(self) -> dict:
        operaciones = self.pending_repository.get_pending_operations()

        if operaciones:
            init_mariadb_db()

        resultado = {
            "procesadas": 0,
            "fallidas": 0,
            "detalles": [],
        }

        for operacion in operaciones:
            operation_id = operacion["id"]

            try:
                self._ejecutar_operacion(
                    tipo=operacion["operation"],
                    student_id=operacion.get("student_id"),
                    payload=operacion.get("payload"),
                )

                self.pending_repository.delete_pending_operation(
                    operation_id
                )

                resultado["procesadas"] += 1
                resultado["detalles"].append(
                    {
                        "id_operacion": operation_id,
                        "resultado": "Sincronizada",
                    }
                )

            except Exception as error:
                self.pending_repository.mark_attempt_failed(
                    operation_id,
                    str(error),
                )

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
        tipo = tipo.upper()

        if not student_id:
            raise ValueError(
                "La operación pendiente no tiene student_id."
            )

        if tipo in {"CREATE", "UPDATE"} and not payload:
            raise ValueError(
                f"La operación {tipo} no contiene los datos del alumno."
            )

        if tipo == "CREATE":
            datos = dict(payload)
            datos["id"] = student_id

            estudiante = Student(**datos)
            self.mariadb.create_student(estudiante)

        elif tipo == "UPDATE":
            datos = dict(payload)
            datos["id"] = student_id

            estudiante = Student(**datos)

            self.mariadb.update_student(
                student_id,
                estudiante,
            )

        elif tipo == "DELETE":
            eliminado = self.mariadb.delete_student(student_id)

            if not eliminado:
                # El registro puede haberse borrado en MariaDB antes
                # de que se pudiera retirar la operación de la cola.
                # En ese caso, el objetivo ya está cumplido.
                return

        else:
            raise ValueError(
                f"Tipo de operación desconocido: {tipo}"
            )