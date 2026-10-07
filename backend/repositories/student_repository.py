from models.student import Student
from backend.connectors.connector_factory import get_connector


class StudentRepository:
    """
    Capa de acceso a datos de los estudiantes.

    El Repository se encarga de comunicarse con los conectores
    y, más adelante, con el sistema de persistencia central.

    El Service no realiza directamente las consultas a las bases
    de datos, sino que delega estas operaciones en este Repository.
    """

    def __init__(self):
        """
        Inicializa el repositorio de estudiantes.
        """

        # De momento no necesitamos inicializar ninguna conexión.
        #
        # Las conexiones a las bases de datos se gestionarán
        # posteriormente mediante los conectores correspondientes.
        pass


    def get_all_students(self):
        """
        Obtiene todos los estudiantes almacenados en el sistema central.

        Returns:
            list: Lista de estudiantes.
        """

        # Más adelante aquí realizaremos la consulta
        # a MariaDB o SQLite.
        #
        # De momento devolvemos una lista vacía para que
        # la estructura de la aplicación esté preparada.
        return []


    def get_student(self, id: str):
        """
        Obtiene un estudiante del sistema central mediante su ID.

        Args:
            id (str): Identificador del estudiante.

        Returns:
            Student | None: Estudiante encontrado o None
            si no existe.
        """

        # Más adelante aquí realizaremos la consulta
        # a MariaDB o SQLite.
        #
        # De momento no tenemos implementada la persistencia
        # central, por lo que devolvemos None.
        return None


    def create_student(self, student: Student):
        """
        Crea un nuevo estudiante en el sistema central.

        Args:
            student (Student): Datos del estudiante que se quiere crear.

        Returns:
            Student: Estudiante creado.
        """

        # Más adelante aquí insertaremos el estudiante
        # en MariaDB y/o SQLite.
        return student


    def update_student(self, id: str, student: Student):
        """
        Actualiza los datos de un estudiante existente.

        Args:
            id (str): Identificador del estudiante.
            student (Student): Nuevos datos del estudiante.

        Returns:
            Student: Estudiante actualizado.
        """

        # Más adelante aquí realizaremos la actualización
        # en la base de datos central.
        return student


    def delete_student(self, id: str):
        """
        Elimina un estudiante del sistema central.

        Args:
            id (str): Identificador del estudiante que se quiere eliminar.

        Returns:
            dict: Resultado de la operación.
        """

        # Más adelante aquí realizaremos la eliminación
        # en la base de datos central.
        return {
            "id": id,
            "deleted": True
        }


    def get_students_from_connector(self, connector_name: str):
        """
        Obtiene todos los estudiantes desde una base de datos
        mediante el conector indicado.

        Args:
            connector_name (str): Nombre del conector que se quiere utilizar.

        Returns:
            list: Lista de estudiantes obtenidos desde el conector.
        """

        # Obtenemos el conector correspondiente al nombre recibido.
        #
        # Por ejemplo:
        #   "derby"  -> DerbyConnector
        #   "hsqldb" -> HSQLDBConnector
        #   "h2"     -> H2Connector
        #   "oracle" -> OracleConnector
        connector = get_connector(connector_name)

        # Delegamos la consulta al conector específico.
        return connector.get_students()


    def get_student_from_connector(
        self,
        connector_name: str,
        id: str
    ):
        """
        Obtiene un estudiante concreto desde una base de datos
        mediante el conector indicado.

        Args:
            connector_name (str): Nombre del conector que se quiere utilizar.
            id (str): Identificador del estudiante.

        Returns:
            Student | None: Estudiante encontrado o None.
        """

        # Obtenemos el conector correspondiente.
        connector = get_connector(connector_name)

        # Delegamos la búsqueda del estudiante al conector.
        return connector.get_student(id)