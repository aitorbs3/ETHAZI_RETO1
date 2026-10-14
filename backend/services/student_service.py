
import uuid

from models.student import Student, StudentCreate
from repositories.student_repository import StudentRepository


CASAS_HISTORICAS_SOLO_LECTURA = {
    "gryffindor",
    "slytherin",
    "hufflepuff",
    "ravenclaw"
}


class StudentService:
    """
    Capa de servicio encargada de gestionar las operaciones
    relacionadas con los estudiantes.

    Actúa como intermediario entre la API y el repositorio.
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
        Obtiene todos los estudiantes disponibles
        mediante el repositorio.
        """
        return self.repository.get_all_students()

    def get_student(self, id: str):
        """
        Obtiene un estudiante mediante su ID interno.

        Se mantiene para identificar los registros
        utilizados en las operaciones CRUD.
        """
        if not id:
            raise ValueError("El identificador es obligatorio")

        return self.repository.get_student(id)

    def search_students_by_name(self, nombre: str) -> list[Student]:
        """
        Busca estudiantes por nombre.

        El repositorio consulta primero la caché SQLite.
        Si no encuentra resultados, consulta las bases
        de datos históricas.

        Args:
            nombre (str): Nombre o parte del nombre.

        Returns:
            list[Student]: Estudiantes encontrados.
        """
        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio")

        return self.repository.search_students_by_name(
            nombre.strip()
        )

    def create_student(self, student: StudentCreate) -> Student:
        """
        Crea un nuevo estudiante.

        No permite registrar nuevos estudiantes
        en las casas históricas.

        El ID se genera automáticamente.
        """
        casa_normalizada = student.casa.strip().lower()

        if casa_normalizada in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"No se pueden registrar nuevos alumnos en "
                f"la casa histórica '{student.casa}'. "
                f"Los nuevos alumnos deben pertenecer a Hogwarts."
            )

        student_id = self.generate_student_id()

        new_student = Student(
            id=student_id,
            **student.model_dump()
        )

        return self.repository.create_student(new_student)

    def update_student(self, id: str, student: Student):
        """
        Actualiza un estudiante existente.

        No permite modificar registros históricos.
        """
        if not id:
            raise ValueError("El identificador es obligatorio")

        existente = self.get_student(id)

        if not existente:
            raise ValueError(
                "El estudiante que intenta modificar no existe"
            )

        casa_actual = existente.casa.strip().lower()

        if casa_actual in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                f"Acceso denegado: Los registros de "
                f"{existente.casa} son de solo lectura "
                f"y no se pueden modificar."
            )

        return self.repository.update_student(id, student)

    def delete_student(self, id: str):
        """
        Elimina un estudiante del sistema central.

        No permite eliminar estudiantes históricos.
        """
        if not id:
            raise ValueError("El identificador es obligatorio")

        existente = self.get_student(id)

        if existente:
            casa_actual = existente.casa.strip().lower()

            if casa_actual in CASAS_HISTORICAS_SOLO_LECTURA:
                raise ValueError(
                    f"Acceso denegado: No se pueden eliminar "
                    f"registros históricos de {existente.casa}."
                )

        return self.repository.delete_student(id)

    def get_students_from_connector(self, connector: str):
        """
        Obtiene todos los estudiantes de una base
        de datos específica.

        Args:
            connector (str): Nombre del conector.

        Returns:
            list[Student]: Estudiantes encontrados.
        """
        if not connector or not connector.strip():
            raise ValueError("El conector es obligatorio")

        return self.repository.get_students_from_connector(
            connector.strip()
        )

    def get_student_from_connector(
        self,
        connector: str,
        nombre: str
    ) -> list[Student]:
        """
        Busca estudiantes por nombre en un conector.

        Permite coincidencias parciales.

        Args:
            connector (str): Nombre del conector.
            nombre (str): Nombre o parte del nombre.

        Returns:
            list[Student]: Estudiantes encontrados.
        """
        if not connector or not connector.strip():
            raise ValueError("El conector es obligatorio")

        if not nombre or not nombre.strip():
            raise ValueError("El nombre es obligatorio")

        return self.repository.get_student_from_connector(
            connector.strip(),
            nombre.strip()
        )
