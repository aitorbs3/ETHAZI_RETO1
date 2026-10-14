
from abc import ABC, abstractmethod
from datetime import date

from models.student import Student


class DatabaseConnector(ABC):
    """
    Define el contrato común de los conectores.

    Las bases de datos históricas son de solo lectura.
    Las búsquedas se realizan por nombre.
    """

    @abstractmethod
    def get_students(self) -> list[Student]:
        """
        Obtiene todos los estudiantes.
        """
        pass

    @abstractmethod
    def get_student(self, name: str) -> list[Student]:
        """
        Busca estudiantes por nombre.

        Devuelve una lista porque puede haber
        varias coincidencias.
        """
        pass


class BaseConnector(DatabaseConnector):
    """
    Implementación reutilizable de las consultas SQL
    para los conectores de bases de datos históricas.

    Cada conector concreto implementa su conexión.
    """

    @abstractmethod
    def _connect(self):
        """
        Establece la conexión con la base de datos.
        """
        pass

    @property
    def placeholder(self) -> str:
        """
        Marcador utilizado en las consultas SQL.
        """
        return "?"

    def get_students(self) -> list[Student]:
        """
        Obtiene todos los estudiantes de la base de datos.
        """

        connection = self._connect()
        cursor = None

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
            if cursor is not None:
                cursor.close()

            connection.close()

    def get_student(self, name: str) -> list[Student]:
        """
        Busca estudiantes por nombre.

        Permite coincidencias parciales
        sin distinguir mayúsculas y minúsculas.
        """

        connection = self._connect()
        cursor = None

        try:
            cursor = connection.cursor()

            cursor.execute(
                f"""
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
                WHERE LOWER(nombre) LIKE LOWER({self.placeholder})
                """,
                (f"%{name}%",)
            )

            rows = cursor.fetchall()

            return [
                self.row_to_student(row)
                for row in rows
            ]

        finally:
            if cursor is not None:
                cursor.close()

            connection.close()

    @staticmethod
    def row_to_student(row) -> Student:
        """
        Convierte el resultado de una consulta
        en un objeto Student.

        Admite filas de tipo tupla y diccionario.
        """

        if isinstance(row, dict):

            nacimiento = row.get("nacimiento")

            if nacimiento is not None and not isinstance(
                nacimiento, date
            ):
                nacimiento = date.fromisoformat(
                    str(nacimiento)
                )

            return Student(
                id=str(row.get("id")),
                nombre=row.get("nombre"),
                casa=row.get("casa"),
                especie=row.get("especie"),
                genero=row.get("genero"),
                nacimiento=nacimiento,
                nacionalidad=row.get("nacionalidad"),
                patronus=row.get("patronus"),
                imagen=row.get("imagen")
            )

        nacimiento = row[5]

        if nacimiento is not None and not isinstance(
            nacimiento, date
        ):
            nacimiento = date.fromisoformat(
                str(nacimiento)
            )

        return Student(
            id=str(row[0]),
            nombre=row[1],
            casa=row[2],
            especie=row[3],
            genero=row[4],
            nacimiento=nacimiento,
            nacionalidad=row[6],
            patronus=row[7],
            imagen=row[8]
        )
