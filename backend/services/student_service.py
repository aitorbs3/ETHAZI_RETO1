from repositories.student_repository import StudentRepository
from models.student import Student


class StudentService:
    """
    Capa de servicio encargada de gestionar las operaciones relacionadas con los estudiantes.

    El servicio actúa como intermediario entre la API y la capa de acceso a datos (Repository).

    La API recibe la petición HTTP y delega la operación en este servicio. El servicio decide qué operación realizar y delega el acceso a los datos al Repository.
    """

    def __init__(self):
        """
        Inicializa el servicio de estudiantes.

        Se crea una instancia del repositorio que será utilizada para acceder a los datos.
        """

        # Creamos el repositorio que se encargará
        # del acceso a los datos.
        self.repository = StudentRepository()


    def get_all_students(self):
        """
        Obtiene todos los estudiantes almacenados en el sistema central.

        Returns:
            list: Lista de estudiantes.
        """

        # De momento delegamos la operación al repositorio.
        # Más adelante el repositorio realizará la consulta
        # a MariaDB o SQLite.
        return self.repository.get_all_students()


    def get_student(self, id: str):
        """
        Obtiene un estudiante mediante su identificador.

        Args:
            id (str): Identificador del estudiante.

        Returns:
            Student | None: Estudiante encontrado o None
            si no existe.
        """

        # Comprobamos que se haya proporcionado un identificador.
        if not id:
            raise ValueError("El identificador es obligatorio")

        # Delegamos la búsqueda al repositorio.
        return self.repository.get_student(id)


    def create_student(self, student: Student):
        """
        Crea un nuevo estudiante en el sistema central.

        Args:
            student (Student): Datos del estudiante que se quiere crear.

        Returns:
            Student: Estudiante creado.
        """

        # Delegamos la creación al repositorio.
        return self.repository.create_student(student)


    def update_student(self, id: str, student: Student):
        """
        Actualiza los datos de un estudiante existente.

        Args:
            id (str): Identificador del estudiante.
            student (Student): Nuevos datos del estudiante.

        Returns:
            Student: Estudiante actualizado.
        """

        # Comprobamos que se haya proporcionado un identificador.
        if not id:
            raise ValueError("El identificador es obligatorio")

        # Delegamos la modificación al repositorio.
        return self.repository.update_student(id, student)


    def delete_student(self, id: str):
        """
        Elimina un estudiante del sistema central.

        Args:
            id (str): Identificador del estudiante que se quiere eliminar.

        Returns:
            Any: Resultado de la operación de eliminación.
        """

        # Comprobamos que se haya proporcionado un identificador.
        if not id:
            raise ValueError("El identificador es obligatorio")

        # Delegamos la eliminación al repositorio.
        return self.repository.delete_student(id)


    def get_students_from_connector(self, connector: str):
        """
        Obtiene los estudiantes desde una base de datos
        mediante el conector indicado.

        Args:
            connector (str): Nombre del conector que se quiere utilizar.

        Returns:
            list: Lista de estudiantes obtenidos del conector.
        """

        # Comprobamos que se haya indicado un conector.
        if not connector:
            raise ValueError("El conector es obligatorio")

        # Delegamos la operación al repositorio.
        return self.repository.get_students_from_connector(connector)


    def get_student_from_connector(self, connector: str, id: str):
        """
        Obtiene un estudiante concreto desde una base de datos
        mediante el conector indicado.

        Args:
            connector (str): Nombre del conector que se quiere utilizar.
            id (str): Identificador del estudiante.

        Returns:
            Student | None: Estudiante encontrado o None.
        """

        # Comprobamos los datos recibidos.
        if not connector:
            raise ValueError("El conector es obligatorio")

        if not id:
            raise ValueError("El identificador es obligatorio")

        # Delegamos la consulta al repositorio.
        return self.repository.get_student_from_connector(
            connector,
            id
        )