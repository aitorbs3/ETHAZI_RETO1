
from abc import ABC, abstractmethod
from datetime import date

from models.student import Student


class DatabaseConnector(ABC):
    """
    Define el contrato común de los conectores
    de bases de datos.

    Las bases históricas permiten únicamente
    operaciones de lectura.
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

        Permite obtener varias coincidencias.
        """
        pass


class BaseConnector(DatabaseConnector):
    """
    Clase base que implementa las consultas SQL
    comunes a los conectores.

    Cada conector debe implementar su propia
    conexión mediante el método _connect().
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
        Devuelve el marcador utilizado en SQL.

        JDBC y SQLite: ?
        MariaDB: %s
        """
        return "?"

    def get_students(self) -> list[Student]:
        """
        Obtiene todos los estudiantes de la base.
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

        Permite coincidencias parciales sin
        distinguir mayúsculas y minúsculas.
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
        Convierte una fila de la base de datos
        en un objeto Student.

        Admite filas de tipo tupla y diccionario.
        """

        if isinstance(row, dict):
            get = row.get

            nacimiento = get("nacimiento")

            if nacimiento is not None and not isinstance(
                nacimiento, date
            ):
                nacimiento = date.fromisoformat(
                    str(nacimiento)
                )

            return Student(
                id=str(get("id")),
                nombre=get("nombre"),
                casa=get("casa"),
                especie=get("especie"),
                genero=get("genero"),
                nacimiento=nacimiento,
                nacionalidad=get("nacionalidad"),
                patronus=get("patronus"),
                imagen=get("imagen"),
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
            imagen=row[8],
        )
