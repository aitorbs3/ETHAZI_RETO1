from connectors.mariadb_connector import MariaDBConnector
from backend.repositories.pending_operations_repository import (
    PendingOperationsRepository,
)
from backend.models.student import Student


class SyncService:
    """
    Sincroniza con MariaDB las operaciones pendientes de SQLite.
    Las operaciones de actualización y eliminación se realizan
    por nombre, no por ID.
    """

    def __init__(self):
        self.pending_repository = PendingOperationsRepository()
        self.mariadb = MariaDBConnector()

    def sincronizar_pendientes(self) -> dict:
        operaciones = self.pending_repository.get_pending_operations()

        resultado = {
            "procesadas": 0,
            "fallidas": 0,
            "detalles": [],
        }

        for operacion in operaciones:
            operation_id = operacion["id"]
            tipo = operacion["operation"]
            nombre = operacion["nombre"]
            nombre_editado = operacion["nombre_editado"]
            payload = operacion["payload"]

            try:
                self._ejecutar_operacion(
                    tipo=tipo,
                    nombre=nombre,
                    nombre_editado=nombre_editado,
                    payload=payload,
                )

                self.pending_repository.delete_pending_operation(
                    operation_id
                )

                resultado["procesadas"] += 1
                resultado["detalles"].append({
                    "id_operacion": operation_id,
                    "operacion": tipo,
                    "resultado": "Sincronizada",
                })

            except Exception as error:
                self.pending_repository.mark_attempt_failed(
                    operation_id,
                    str(error),
                )

                resultado["fallidas"] += 1
                resultado["detalles"].append({
                    "id_operacion": operation_id,
                    "operacion": tipo,
                    "resultado": "Pendiente",
                    "error": str(error),
                })

        return resultado

    def _ejecutar_operacion(
        self,
        tipo: str,
        nombre: str,
        nombre_editado: str | None,
        payload: dict | None,
    ) -> None:
        """
        Ejecuta una operación pendiente en MariaDB.
        """

        tipo = tipo.upper()

        if tipo in {"CREATE", "UPDATE"} and payload is None:
            raise ValueError(
                f"{tipo} necesita los datos del estudiante"
            )

        if tipo in {"UPDATE", "DELETE"}:
            if not nombre or not nombre.strip():
                raise ValueError(
                    f"{tipo} necesita el nombre original del estudiante"
                )

        if tipo == "CREATE":
            datos = dict(payload)
            estudiante = Student(**datos)
            self.mariadb.create_student(estudiante)

        elif tipo == "UPDATE":
            datos = dict(payload)

            # Si el nombre cambió, se aplica el nombre nuevo.
            if nombre_editado is not None:
                datos["nombre"] = nombre_editado

            estudiante = Student(**datos)

            self.mariadb.update_student_by_name(
                nombre.strip(),
                estudiante,
            )

        elif tipo == "DELETE":
            eliminados = self.mariadb.delete_student_by_name(
                nombre.strip()
            )

            if eliminados == 0:
                raise ValueError(
                    f"No existe el estudiante '{nombre}' en MariaDB"
                )

        else:
            raise ValueError(
                f"Operación no soportada: {tipo}"
            )