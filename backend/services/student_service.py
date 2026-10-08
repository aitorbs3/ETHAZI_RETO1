from repositories.student_repository import StudentRepository
from models.student import Student

CASAS_HISTORICAS_SOLO_LECTURA = {"gryffindor", "slytherin", "hufflepuff", "ravenclaw"}

class StudentService:
    def __init__(self):
        self.repository = StudentRepository()

    def get_all_students(self):
        return self.repository.get_all_students()

    def get_student(self, id: str):
        if not id:
            raise ValueError("El identificador es obligatorio")
        return self.repository.get_student(id)

    def create_student(self, student: Student):
        # Regla: Los nuevos alumnos SOLO pueden ir a la casa 'DATABASE' (MariaDB)
        casa_normalizada = student.casa.strip().lower()
        if casa_normalizada in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"No se pueden registrar nuevos alumnos en la casa histórica '{student.casa}'. "
                f"Los nuevos alumnos deben pertenecer a 'Hogwarts'."
            )
        return self.repository.create_student(student)

    def update_student(self, id: str, student: Student):
        if not id:
            raise ValueError("El identificador es obligatorio")

        # 1. Comprobar a qué casa pertenece el alumno antes de editar
        existente = self.get_student(id)
        if not existente:
            raise ValueError("El estudiante que intenta modificar no existe")

        casa_actual = existente.casa.strip().lower()
        if casa_actual in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"Acceso Denegado: Los registros de {existente.casa} son de solo lectura y no se pueden modificar."
            )

        return self.repository.update_student(id, student)

    def delete_student(self, id: str):
        if not id:
            raise ValueError("El identificador es obligatorio")

        # 1. Comprobar si pertenece a una casa histórica antes de borrar
        existente = self.get_student(id)
        if existente:
            casa_actual = existente.casa.strip().lower()
            if casa_actual in CASAS_HISTORICAS_SOLO_LECTURA:
                raise ValueError(
                    f"Acceso Denegado: No se pueden eliminar registros históricos de {existente.casa}."
                )

        return self.repository.delete_student(id)

    def get_students_from_connector(self, connector: str):
        if not connector:
            raise ValueError("El conector es obligatorio")
        return self.repository.get_students_from_connector(connector)

    def get_student_from_connector(self, connector: str, id: str):
        if not connector:
            raise ValueError("El conector es obligatorio")
        if not id:
            raise ValueError("El identificador es obligatorio")
        return self.repository.get_student_from_connector(connector, id)