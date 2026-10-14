from models.student import Student, StudentCreate
from repositories.student_repository import StudentRepository


CASAS_HISTORICAS_SOLO_LECTURA = {
    "gryffindor",
    "slytherin",
    "hufflepuff",
    "ravenclaw",
}


class StudentService:
    """
    Servicio encargado de gestionar las operaciones
    relacionadas con los estudiantes.
    """

    def __init__(self):
        self.repository = StudentRepository()

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_all_students(self):
        """Obtiene los estudiantes almacenados localmente."""
        return self.repository.get_all_students()

    def get_student(self, student_id: str):
        """
        Consulta un estudiante por su identificador interno.
        Se conserva para compatibilidad con consultas existentes.
        """
        if not student_id:
            raise ValueError("El identificador es obligatorio")

        return self.repository.get_student(student_id)

    def search_students_by_name(self, nombre: str) -> list[Student]:
        """Busca estudiantes por nombre."""
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio")

        return self.repository.search_students_by_name(
            nombre.strip()
        )

    # ==========================================================
    # CREATE
    # ==========================================================

    def create_student(self, student: StudentCreate) -> Student:
        """
        Crea un alumno nuevo en SQLite y registra la operación
        pendiente para sincronizarla con MariaDB.

        El UUID se genera en el repositorio.
        """
        casa = student.casa.strip().lower() if student.casa else ""

        if casa in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"No se pueden registrar nuevos alumnos en la casa "
                f"histórica '{student.casa}'. Los nuevos alumnos "
                "deben pertenecer a 'Hogwarts'."
            )

        nuevo = Student(
            id="",
            **student.model_dump(),
        )

        return self.repository.create_student(nuevo)

    # ==========================================================
    # UPDATE
    # ==========================================================

    def update_student(self, nombre: str, student: Student) -> Student:
        """
        Actualiza un alumno identificado por su nombre exacto.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del alumno es obligatorio")

        existente = self.repository.get_student_by_name(nombre)

        if existente is None:
            raise ValueError(
                "El alumno que intenta modificar no existe"
            )

        casa_actual = (
            existente.casa.strip().lower()
            if existente.casa
            else ""
        )

        if casa_actual in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"Acceso denegado: los registros de "
                f"{existente.casa} son de solo lectura."
            )

        casa_nueva = (
            student.casa.strip().lower()
            if student.casa
            else ""
        )

        if casa_nueva in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                "No se puede asignar un alumno editable "
                "a una casa histórica."
            )

        return self.repository.update_student(nombre, student)

    # ==========================================================
    # DELETE
    # ==========================================================

    def delete_student(self, nombre: str) -> bool:
        """
        Elimina un alumno por nombre y registra el borrado
        pendiente de sincronizar con MariaDB.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del alumno es obligatorio")

        existente = self.repository.get_student_by_name(nombre)

        if existente is None:
            raise ValueError(
                "El alumno que intenta eliminar no existe"
            )

        casa = (
            existente.casa.strip().lower()
            if existente.casa
            else ""
        )

        if casa in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"Acceso denegado: no se pueden eliminar "
                f"registros históricos de {existente.casa}."
            )

        return self.repository.delete_student(nombre)

    # ==========================================================
    # CONSULTAS A CONECTORES
    # ==========================================================

    def get_students_from_connector(self, connector: str):
        """Obtiene estudiantes de un conector específico."""
        if not connector or not connector.strip():
            raise ValueError("El conector es obligatorio")

        return self.repository.get_students_from_connector(
            connector.strip()
        )

    def get_student_from_connector(
        self,
        connector: str,
        nombre: str,
    ):
        """Busca coincidencias por nombre en un conector."""
        if not connector or not connector.strip():
            raise ValueError("El conector es obligatorio")

        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio")

        return self.repository.get_student_from_connector(
            connector.strip(),
            nombre.strip(),
        )