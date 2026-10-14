
from datetime import date

from models.student import Student
from connectors.connector_factory import get_connector
from connectors.sqlite_connector import get_sqlite_connection


class StudentRepository:
    """
    Acceso a los datos de estudiantes.

    SQLite almacena la caché de los estudiantes consultados
    en las bases de datos de origen.

    Las bases de origen son:
    Derby, H2, HSQLDB y Oracle.

    Las bases de origen son exclusivamente de lectura.
    """

    SOURCE_CONNECTORS = (
        "derby",
        "h2",
        "hsqldb",
        "oracle",
    )

    # ==========================================================
    # SQLITE: CONSULTA DE CACHÉ
    # ==========================================================

    def get_student_from_cache(self, student_id: str) -> Student | None:
        query = """
            SELECT id, nombre, casa, especie, genero,
                   nacimiento, nacionalidad, patronus, imagen
            FROM cache_students
            WHERE id = ?
        """

        with get_sqlite_connection() as conn:
            row = conn.execute(query, (student_id,)).fetchone()

        return self._row_to_student(row) if row else None

    def get_students_from_cache(self) -> list[Student]:
        query = """
            SELECT id, nombre, casa, especie, genero,
                   nacimiento, nacionalidad, patronus, imagen
            FROM cache_students
        """

        with get_sqlite_connection() as conn:
            rows = conn.execute(query).fetchall()

        return [self._row_to_student(row) for row in rows]

    def search_students_in_cache(self, name: str) -> list[Student]:
        query = """
            SELECT id, nombre, casa, especie, genero,
                   nacimiento, nacionalidad, patronus, imagen
            FROM cache_students
            WHERE LOWER(nombre) LIKE LOWER(?)
        """

        with get_sqlite_connection() as conn:
            rows = conn.execute(query, (f"%{name}%",)).fetchall()

        return [self._row_to_student(row) for row in rows]

    def save_student_to_cache(self, student: Student) -> Student:
        query = """
            INSERT INTO cache_students (
                id, nombre, casa, especie, genero,
                nacimiento, nacionalidad, patronus, imagen
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
            if student.nacimiento is not None
            else None
        )

        with get_sqlite_connection() as conn:
            conn.execute(
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
                ),
            )
            conn.commit()

        return student

    def save_students_to_cache(self, students: list[Student]) -> None:
        """
        Guarda varios estudiantes en la caché.
        """
        for student in students:
            self.save_student_to_cache(student)

    def delete_student_from_cache(self, student_id: str) -> bool:
        query = "DELETE FROM cache_students WHERE id = ?"

        with get_sqlite_connection() as conn:
            cursor = conn.execute(query, (student_id,))
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_all_students(self) -> list[Student]:
        """
        Devuelve los estudiantes actualmente guardados en caché.
        """
        return self.get_students_from_cache()

    def get_student(self, student_id: str) -> Student | None:
        """
        Mantiene la consulta existente por ID.
        No consulta todavía las fuentes por este método.
        """
        return self.get_student_from_cache(student_id)

    def search_students_by_name(self, name: str) -> list[Student]:
        """
        Busca por nombre.

        1. Consulta SQLite.
        2. Si encuentra resultados, los devuelve.
        3. Si no encuentra ninguno, consulta las fuentes.
        4. Elimina duplicados por ID.
        5. Guarda los resultados en la caché y los devuelve.
        """

        if not name or not name.strip():
            raise ValueError("El nombre es obligatorio")

        name = name.strip()

        # Primero se consulta SQLite.
        cached_students = self.search_students_in_cache(name)

        if cached_students:
            return cached_students

        # Si SQLite no tiene resultados, se consultan las fuentes.
        found_by_id: dict[str, Student] = {}

        for connector_name in self.SOURCE_CONNECTORS:
            try:
                connector = get_connector(connector_name)
                students = connector.get_student(name)

                for raw_student in students:
                    student = self._ensure_student(raw_student)
                    found_by_id[student.id] = student

            except Exception as exc:
                # Un origen caído no impide consultar los demás.
                print(
                    f"No se pudo consultar {connector_name}: {exc}"
                )

        found_students = list(found_by_id.values())

        # Se guardan los resultados encontrados en SQLite.
        if found_students:
            self.save_students_to_cache(found_students)

        return found_students

    # ==========================================================
    # CRUD LOCAL EXISTENTE
    # ==========================================================

    def create_student(self, student: Student) -> Student:
        """
        Guarda un estudiante en la tabla local alumnos.
        La sincronización con MariaDB se implementará después.
        """
        from connectors.sqlite_connector import SQLiteConnector

        return SQLiteConnector().create_student(student)

    def update_student(
        self,
        student_id: str,
        student: Student,
    ) -> Student:
        from connectors.sqlite_connector import SQLiteConnector

        return SQLiteConnector().update_student(student_id, student)

    def delete_student(self, student_id: str) -> bool:
        from connectors.sqlite_connector import SQLiteConnector

        return SQLiteConnector().delete_student(student_id)

    # ==========================================================
    # CONSULTAS DIRECTAS A FUENTES
    # ==========================================================

    def get_students_from_connector(
        self,
        connector_name: str,
    ) -> list[Student]:
        connector = get_connector(connector_name)
        return [
            self._ensure_student(student)
            for student in connector.get_students()
        ]

    def get_student_from_connector(
        self,
        connector_name: str,
        name: str,
    ) -> list[Student]:
        """
        Busca coincidencias por nombre en una fuente concreta.
        """
        connector = get_connector(connector_name)
        return [
            self._ensure_student(student)
            for student in connector.get_student(name)
        ]

    # ==========================================================
    # CONVERSIÓN
    # ==========================================================

    @staticmethod
    def _row_to_student(row) -> Student:
        nacimiento = row["nacimiento"]

        if nacimiento and isinstance(nacimiento, str):
            nacimiento = date.fromisoformat(nacimiento)

        return Student(
            id=str(row["id"]),
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
        if isinstance(student, Student):
            return student

        if isinstance(student, dict):
            return Student(**student)

        raise TypeError(
            f"Tipo de estudiante no soportado: {type(student)}"
        )