from abc import ABC, abstractmethod
from datetime import date

from models.student import Student


class BaseConnector(ABC):
    """
    Clase base común para los conectores de lectura.

    Contiene las operaciones de consulta compartidas por
    las diferentes bases de datos.
    """

    @abstractmethod
    def _connect(self):
        """
        Establece una conexión con la base de datos.
        Cada conector implementa su propia conexión.
        """
        pass

    @property
    def placeholder(self) -> str:
        """
        Marcador SQL predeterminado para los conectores JDBC.
        MariaDB puede sobrescribirlo para utilizar %s.
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
        Se permiten coincidencias parciales.
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
        Convierte una fila de la base de datos en un objeto Student.

        Admite filas tipo tupla (JDBC) y tipo diccionario (MariaDB).
        El orden esperado de las columnas es:
        id, nombre, casa, especie, genero, nacimiento,
        nacionalidad, patronus, imagen.
        """

        if isinstance(row, dict):
            get = row.get

            nacimiento = get("nacimiento")

            if nacimiento is not None and not isinstance(nacimiento, date):
                nacimiento = date.fromisoformat(str(nacimiento))

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