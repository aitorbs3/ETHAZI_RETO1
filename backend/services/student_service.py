import uuid

from models.student import Student, StudentCreate
from repositories.student_repository import StudentRepository

CASAS_HISTORICAS_SOLO_LECTURA = {"gryffindor", "slytherin", "hufflepuff", "ravenclaw"}


class StudentService:
    """
    Capa de servicio encargada de gestionar las operaciones
    relacionadas con los estudiantes.
    """

    def __init__(self):
        """
        Inicializa el servicio de estudiantes.
        """
        self.repository = StudentRepository()

    @staticmethod
    def generate_student_id() -> str:
        """
        Genera un identificador único para un nuevo estudiante.

        Returns:
            str: Identificador UUID generado.
        """
        return str(uuid.uuid4())

    def get_all_students(self):
        """
        Obtiene todos los estudiantes almacenados en el sistema central.
        """
        return self.repository.get_all_students()

    def get_student(self, id: str):
        """
        Obtiene un estudiante mediante su identificador.
        """
        if not id:
            raise ValueError("El identificador es obligatorio")
        return self.repository.get_student(id)

    def create_student(self, student: StudentCreate) -> Student:
        """
        Crea un nuevo estudiante validando las casas permitidas.
        El identificador se genera automáticamente en el backend.

        Args:
            student (StudentCreate): Datos del nuevo estudiante.

        Returns:
            Student: Estudiante creado con su identificador.
        """
        # 1. Regla de negocio: Los nuevos alumnos no pueden registrarse en casas históricas
        casa_normalizada = student.casa.strip().lower()
        if casa_normalizada in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"No se pueden registrar nuevos alumnos en la casa histórica '{student.casa}'. "
                f"Los nuevos alumnos deben pertenecer a 'Hogwarts'."
            )

        # 2. Generar ID automático e instanciar el modelo Student completo
        student_id = self.generate_student_id()
        new_student = Student(
            id=student_id,
            **student.model_dump()
        )

        return self.repository.create_student(new_student)

    def update_student(self, id: str, student: Student):
        """
        Actualiza los datos de un estudiante existente verificando permisos de lectura.
        """
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
        """
        Elimina un estudiante del sistema central verificando permisos de lectura.
        """
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
        """
        Obtiene estudiantes desde un conector concreto.
        """
        if not connector:
            raise ValueError("El conector es obligatorio")
        return self.repository.get_students_from_connector(connector)

    def get_student_from_connector(self, connector: str, id: str):
        """
        Obtiene un estudiante concreto desde un conector.
        """
        if not connector:
            raise ValueError("El conector es obligatorio")
        if not id:
            raise ValueError("El identificador es obligatorio")
        return self.repository.get_student_from_connector(connector, id)