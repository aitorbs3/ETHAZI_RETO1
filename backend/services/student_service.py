from datetime import datetime

from models.student import Student, StudentCreate
from repositories.student_repository import StudentRepository
from services.sync_service import SyncService


CASAS_HISTORICAS_SOLO_LECTURA = {
    "gryffindor",
    "slytherin",
    "hufflepuff",
    "ravenclaw",
}


class StudentService:
    def __init__(self):
        self.repository = StudentRepository()
        self.sync_service = SyncService()
        self.ultima_sincronizacion = None

    def _intentar_sincronizar(self):
        """Intenta sincronizar con MariaDB sin perder los cambios locales."""
        try:
            resultado = self.sync_service.sincronizar_pendientes()
            self.ultima_sincronizacion = {
                "fecha": datetime.now().isoformat(),
                "resultado": resultado,
            }
            return resultado
        except Exception as error:
            print(f"No se pudo sincronizar con MariaDB: {error}")
            return {
                "procesadas": 0,
                "fallidas": 0,
                "detalles": [],
                "error": str(error),
            }

    @staticmethod
    def _validar_nombre(nombre: str | None):
        if nombre is None or not nombre.strip():
            raise ValueError("El nombre del alumno es obligatorio.")

    @staticmethod
    def _validar_casa_historica(casa: str | None):
        if casa and casa.strip().casefold() in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                "No se pueden modificar ni eliminar alumnos "
                "de las casas históricas."
            )

    def get_all_students(self) -> list[Student]:
        return self.repository.get_all_students()

    def get_student(self, student_id: str) -> Student:
        student = self.repository.get_student(student_id)

        if student is None:
            raise ValueError("No se encontró el alumno.")

        return student

    def search_students_by_name(self, nombre: str) -> list[Student]:
        self._validar_nombre(nombre)
        return self.repository.search_students_by_name(nombre)

    def create_student(self, student_data: StudentCreate) -> Student:
        self._validar_nombre(student_data.nombre)

        self._validar_casa_historica(student_data.casa)

        student = Student(
            id="",
            **student_data.model_dump(),
        )

        creado = self.repository.create_student(student)
        self._intentar_sincronizar()

        return creado

    def update_student_by_id(
        self,
        student_id: str,
        student_data: Student,
    ) -> Student:
        if not student_id or not student_id.strip():
            raise ValueError("El identificador del alumno es obligatorio.")

        alumno_actual = self.repository.get_student(student_id)

        if alumno_actual is None:
            raise ValueError("No se encontró el alumno seleccionado.")

        # Solo se pueden modificar alumnos nuevos de Hogwarths
        if (alumno_actual.casa or "").strip().casefold() != "hogwarths":
            raise ValueError(
                "Solo se pueden modificar alumnos nuevos de Hogwarths."
            )

        # No se permite cambiar la casa del alumno
        if (student_data.casa or "").strip().casefold() != "hogwarths":
            raise ValueError(
                "No se puede cambiar la casa de un alumno nuevo."
            )

        self._validar_nombre(student_data.nombre)

        self._validar_casa_historica(alumno_actual.casa)
        self._validar_casa_historica(student_data.casa)

        student_data.id = student_id

        # Actualizar alumno en SQLite
        actualizado = self.repository.update_student_by_id(
            student_id,
            student_data,
        )

        # Intentar sincronizar con MariaDB
        self._intentar_sincronizar()

        return actualizado


    def delete_student_by_id(self, student_id: str) -> dict:
        """Elimina únicamente alumnos nuevos de Hogwarths."""

        if not student_id or not student_id.strip():
            raise ValueError("El identificador del alumno es obligatorio.")

        student_id = student_id.strip()

        # Obtener el alumno seleccionado por su ID
        alumno = self.repository.get_student(student_id)

        if alumno is None:
            raise ValueError("No se encontró el alumno seleccionado.")

        # Solo se permiten alumnos nuevos de Hogwarths
        if (alumno.casa or "").strip().casefold() != "hogwarths":
            raise ValueError(
                "Solo se pueden eliminar alumnos nuevos de Hogwarths."
            )

        # Eliminar de SQLite y registrar DELETE pendiente
        eliminado = self.repository.delete_student_by_id(student_id)

        if not eliminado:
            raise RuntimeError("No se pudo eliminar el alumno.")

        # Intentar sincronizar el borrado con MariaDB
        resultado_sync = self._intentar_sincronizar()

        return {
            "mensaje": "Alumno eliminado localmente.",
            "student_id": student_id,
            "sincronizacion": resultado_sync,
        }


    def get_students_from_connector(
        self,
        connector_name: str,
    ) -> list[Student]:
        return self.repository.get_students_from_connector(connector_name)

    def get_student_from_connector(
        self,
        connector_name: str,
        nombre: str,
    ) -> list[Student]:
        self._validar_nombre(nombre)
        return self.repository.get_student_from_connector(
            connector_name,
            nombre,
        )