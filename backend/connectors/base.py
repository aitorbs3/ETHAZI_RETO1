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
        """
        Convierte una fila de la base de datos en un objeto Student.

        Orden de las columnas:

            0 -> id
            1 -> nombre
            2 -> casa
            3 -> especie
            4 -> genero
            5 -> nacimiento
            6 -> nacionalidad
            7 -> patronus
            8 -> imagen
        """

        nacimiento = row[5]

        if nacimiento is not None and not isinstance(nacimiento, date):
            nacimiento = date.fromisoformat(str(nacimiento))

        return Student(
            id=str(row[0]),
            nombre=row[1],
            casa=row[2],
            especie=row[3],
            genero=row[4],
            nacimiento=nacimiento,
            nacionalidad=row[6],
            patronus=row[7],
            imagen=row[8],
        )