from abc import ABC, abstractmethod
from datetime import date

from models.student import Student


class BaseConnector(ABC):
    """
    Clase base común para los conectores de lectura.

    Contiene las operaciones de consulta que son comunes
    a las diferentes bases de datos.
    """

    @abstractmethod
    def _connect(self):
        """
        Establece una conexión con la base de datos.

        Cada conector implementará este método utilizando
        su propia función de conexión.
        """
        pass

    def get_students(self) -> list[Student]:
        """
        Obtiene todos los estudiantes de la base de datos.
        """

        connection = self._connect()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    id,
                    nombre,
                    casa,
                    especie,
                    genero,
                    nacimiento,
                    nacionalidad,
                    patronus,
                    imagen
                FROM alumnos
            """)

            rows = cursor.fetchall()

            return [
                self.row_to_student(row)
                for row in rows
            ]

        finally:
            connection.close()

    def get_student(self, name: str) -> list[Student]:
        """
        Busca estudiantes por nombre.

        Se permiten coincidencias parciales.
        """

        connection = self._connect()

        try:
            cursor = connection.cursor()

            cursor.execute("""
                SELECT
                    id,
                    nombre,
                    casa,
                    especie,
                    genero,
                    nacimiento,
                    nacionalidad,
                    patronus,
                    imagen
                FROM alumnos
                WHERE LOWER(nombre) LIKE LOWER(?)
            """, (f"%{name}%",))

            rows = cursor.fetchall()

            return [
                self.row_to_student(row)
                for row in rows
            ]

        finally:
            connection.close()

    @staticmethod
    def row_to_student(row) -> Student:
        nacimiento = row[5]

        if nacimiento is not None and not isinstance(nacimiento, date):
            nacimiento = date.fromisoformat(str(nacimiento))

        return Student(
            id=str(row[0]),
            nombre=str(row[1]) if row[1] is not None else None,
            casa=str(row[2]) if row[2] is not None else None,
            especie=str(row[3]) if row[3] is not None else None,
            genero=str(row[4]) if row[4] is not None else None,
            nacimiento=nacimiento,
            nacionalidad=str(row[6]) if row[6] is not None else None,
            patronus=str(row[7]) if row[7] is not None else None,
            imagen=str(row[8]) if row[8] is not None else None,
        )