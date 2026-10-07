from abc import ABC, abstractmethod


class DatabaseConnector(ABC):
    """
    Clase base que define el contrato común de todos
    los conectores de bases de datos.

    Todos los conectores concretos, como Derby, HSQLDB,
    H2 y Oracle, deberán implementar los métodos definidos
    en esta clase.
    """

    @abstractmethod
    def get_students(self):
        """
        Obtiene todos los estudiantes de la base de datos.

        Returns:
            list: Lista de estudiantes.
        """
        pass

    @abstractmethod
    def get_student(self, id: str):
        """
        Obtiene un estudiante mediante su identificador.

        Args:
            id (str): Identificador del estudiante.

        Returns:
            Student | None: Estudiante encontrado o None
            si no existe.
        """
        pass