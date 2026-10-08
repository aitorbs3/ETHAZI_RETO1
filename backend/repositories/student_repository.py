from datetime import date

from backend.models.student import Student
from backend.connectors.connector_factory import get_connector
from backend.connectors.sqlite_connector import get_sqlite_connection


class StudentRepository:
    """
    Repository encargado del acceso a los datos de estudiantes.

    SQLite actúa como caché/local store principal.
    Las bases de datos Oracle, H2, HSQLDB y Derby son
    fuentes externas de solo lectura.

    MariaDB se utilizará como persistencia central.
    """

    # ==========================================================
    # SQLITE
    # ==========================================================

    def get_student_from_cache(self, student_id: str) -> Student | None:
        """
        Busca un estudiante en la caché SQLite.

        Args:
            student_id (str): identificador del estudiante.

        Returns:
            Student | None: estudiante encontrado o None.
        """

        query = """
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
            FROM cache_students
            WHERE id = ?
        """

        with get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (student_id,))

            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_student(row)

    def get_students_from_cache(self) -> list[Student]:
        """
        Obtiene todos los estudiantes almacenados en SQLite.

        Returns:
            list[Student]: estudiantes almacenados en caché.
        """

        query = """
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
            FROM cache_students
        """

        with get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)

            rows = cursor.fetchall()

            return [
                self._row_to_student(row)
                for row in rows
            ]

    def search_students_in_cache(
        self,
        name: str
    ) -> list[Student]:
        """
        Busca estudiantes por nombre en SQLite.

        Args:
            name (str): nombre o parte del nombre.

        Returns:
            list[Student]: estudiantes encontrados.
        """

        query = """
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
            FROM cache_students
            WHERE LOWER(nombre) LIKE LOWER(?)
        """

        with get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (f"%{name}%",))

            rows = cursor.fetchall()

            return [
                self._row_to_student(row)
                for row in rows
            ]

    def save_student_to_cache(self, student: Student) -> Student:
        """
        Guarda o actualiza un estudiante en SQLite.

        Se utiliza UPSERT para que si el estudiante ya existe,
        sus datos sean actualizados.

        Args:
            student (Student): estudiante que se quiere guardar.

        Returns:
            Student: estudiante guardado.
        """

        query = """
            INSERT INTO cache_students (
                id,
                nombre,
                casa,
                especie,
                genero,
                nacimiento,
                nacionalidad,
                patronus,
                imagen
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                nombre = excluded.nombre,
                casa = excluded.casa,
                especie = excluded.especie,
                genero = excluded.genero,
                nacimiento = excluded.nacimiento,
                nacionalidad = excluded.nacionalidad,
                patronus = excluded.patronus,
                imagen = excluded.imagen
        """

        nacimiento = (
            student.nacimiento.isoformat()
            if student.nacimiento
            else None
        )

        with get_sqlite_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(
                query,
                (
                    student.id,
                    student.nombre,
                    student.casa,
                    student.especie,
                    student.genero,
                    nacimiento,
                    student.nacionalidad,
                    student.patronus,
                    student.imagen,
                )
            )

            conn.commit()

        return student

    def delete_student_from_cache(self, student_id: str) -> bool:
        """
        Elimina un estudiante de SQLite.

        Args:
            student_id (str): identificador del estudiante.

        Returns:
            bool: True si se eliminó, False si no existía.
        """

        query = """
            DELETE FROM cache_students
            WHERE id = ?
        """

        with get_sqlite_connection() as conn:
            cursor = conn.cursor()

            cursor.execute(query, (student_id,))

            conn.commit()

            return cursor.rowcount > 0

    # ==========================================================
    # CONSULTA DE ESTUDIANTES
    # ==========================================================

    def get_all_students(self) -> list[Student]:
        """
        Obtiene todos los estudiantes disponibles.

        De momento se consulta SQLite.

        La lógica completa de sincronización con las fuentes
        externas se incorporará posteriormente.
        """

        return self.get_students_from_cache()

    def get_student(self, student_id: str) -> Student | None:
        """
        Obtiene un estudiante.

        Primero se consulta SQLite.

        Si no existe en caché, se buscará posteriormente
        en las bases de datos de origen.
        """

        student = self.get_student_from_cache(student_id)

        if student is not None:
            return student

        return None

    def search_students_by_name(
        self,
        name: str
    ) -> list[Student]:
        """
        Busca estudiantes por nombre.

        Primero se consulta SQLite.

        Args:
            name (str): nombre o parte del nombre.

        Returns:
            list[Student]: estudiantes encontrados.
        """

        return self.search_students_in_cache(name)

    # ==========================================================
    # CRUD SQLITE
    # ==========================================================

    def create_student(self, student: Student) -> Student:
        """
        Crea un estudiante en SQLite.

        SQLite es la primera base de datos que se modifica.

        La sincronización posterior con MariaDB se añadirá
        cuando implementemos el conector correspondiente.
        """

        return self.save_student_to_cache(student)

    def update_student(
        self,
        student_id: str,
        student: Student
    ) -> Student:
        """
        Actualiza un estudiante en SQLite.

        Args:
            student_id (str): identificador del estudiante.
            student (Student): nuevos datos.

        Returns:
            Student: estudiante actualizado.
        """

        existing = self.get_student_from_cache(student_id)

        if existing is None:
            raise ValueError(
                f"No existe ningún estudiante con el ID {student_id}"
            )

        student.id = student_id

        return self.save_student_to_cache(student)

    def delete_student(self, student_id: str) -> bool:
        """
        Elimina un estudiante de SQLite.

        Args:
            student_id (str): identificador del estudiante.

        Returns:
            bool: True si se eliminó correctamente.
        """

        existing = self.get_student_from_cache(student_id)

        if existing is None:
            raise ValueError(
                f"No existe ningún estudiante con el ID {student_id}"
            )

        return self.delete_student_from_cache(student_id)

    # ==========================================================
    # CONECTORES DE BBDD DE ORIGEN
    # ==========================================================

    def get_students_from_connector(
        self,
        connector_name: str
    ) -> list[Student]:
        """
        Obtiene estudiantes directamente desde una BBDD de origen.

        Esta función es interna y se utilizará para consultar
        Oracle, H2, HSQLDB o Derby.

        Las BBDD de origen son de solo lectura.
        """

        connector = get_connector(connector_name)

        students = connector.get_students()

        return [
            self._ensure_student(student)
            for student in students
        ]

    def get_student_from_connector(
        self,
        connector_name: str,
        student_id: str
    ) -> Student | None:
        """
        Obtiene un estudiante directamente desde una BBDD de origen.

        Args:
            connector_name (str): nombre del conector.
            student_id (str): identificador del estudiante.

        Returns:
            Student | None: estudiante encontrado o None.
        """

        connector = get_connector(connector_name)

        student = connector.get_student(student_id)

        if student is None:
            return None

        return self._ensure_student(student)

    # ==========================================================
    # CONVERSIÓN DE DATOS
    # ==========================================================

    @staticmethod
    def _row_to_student(row) -> Student:
        """
        Convierte una fila SQLite en un objeto Student.
        """

        nacimiento = row["nacimiento"]

        if nacimiento:
            if isinstance(nacimiento, str):
                nacimiento = date.fromisoformat(nacimiento)

        return Student(
            id=row["id"],
            nombre=row["nombre"],
            casa=row["casa"],
            especie=row["especie"],
            genero=row["genero"],
            nacimiento=nacimiento,
            nacionalidad=row["nacionalidad"],
            patronus=row["patronus"],
            imagen=row["imagen"],
        )

    @staticmethod
    def _ensure_student(student) -> Student:
        """
        Convierte un objeto recibido desde un conector
        en un objeto Student.

        Permite trabajar tanto con objetos Student como
        con diccionarios.
        """

        if isinstance(student, Student):
            return student

        if isinstance(student, dict):
            return Student(**student)

        raise TypeError(
            f"Tipo de estudiante no soportado: {type(student)}"
        )