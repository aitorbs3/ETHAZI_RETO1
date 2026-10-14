from models.student import Student, StudentCreate
from repositories.student_repository import StudentRepository


CASAS_HISTORICAS_SOLO_LECTURA = {
    "gryffindor",
    "slytherin",
    "hufflepuff",
    "ravenclaw",
}


class StudentService:
    def __init__(self):
        self.repository = StudentRepository()

    def get_all_students(self):
        return self.repository.get_all_students()

    def get_student(self, student_id: str):
        if not student_id:
            raise ValueError("El identificador es obligatorio")

        return self.repository.get_student(student_id)

    def create_student(self, student: StudentCreate) -> Student:
        casa = student.casa.strip().lower() if student.casa else ""

        if casa in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"No se pueden registrar nuevos alumnos en la casa "
                f"histórica '{student.casa}'. Los nuevos alumnos "
                "deben pertenecer a 'Hogwarts'."
            )

        new_student = Student(id="", **student.model_dump())
        return self.repository.create_student(new_student)

    def update_student(self, nombre: str, student: Student) -> Student:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del alumno es obligatorio")

        existente = self.repository.get_student_by_name(nombre)

        if existente is None:
            raise ValueError("El alumno que intenta modificar no existe")

        casa = existente.casa.strip().lower() if existente.casa else ""

        if casa in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"Acceso denegado: los registros de {existente.casa} "
                "son de solo lectura."
            )

        casa_nueva = student.casa.strip().lower() if student.casa else ""

        if casa_nueva in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                "No se puede asignar un alumno editable a una casa histórica."
            )

        return self.repository.update_student(nombre, student)

    def delete_student(self, nombre: str) -> bool:
        if not nombre or not nombre.strip():
            raise ValueError("El nombre del alumno es obligatorio")

        existente = self.repository.get_student_by_name(nombre)

        if existente is None:
            raise ValueError("El alumno que intenta eliminar no existe")

        casa = existente.casa.strip().lower() if existente.casa else ""

        if casa in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"Acceso denegado: no se pueden eliminar registros "
                f"históricos de {existente.casa}."
            )

        return self.repository.delete_student(nombre)

    def get_students_from_connector(self, connector: str):
        if not connector:
            raise ValueError("El conector es obligatorio")

        return self.repository.get_students_from_connector(connector)

    def get_student_from_connector(self, connector: str, name: str):
        if not connector:
            raise ValueError("El conector es obligatorio")

        if not name or not name.strip():
            raise ValueError("El nombre es obligatorio")

        return self.repository.get_student_from_connector(
            connector,
            name.strip(),
        )

    def search_students_by_name(self, name: str) -> list[Student]:
        if not name or not name.strip():
            raise ValueError("El nombre es obligatorio")

        return self.repository.search_students_by_name(name.strip())