import json
import uuid
from datetime import date

from models.student import Student
from connectors.connector_factory import get_connector
from connectors.sqlite_connector import get_sqlite_connection


class StudentRepository:
    SOURCE_CONNECTORS = ("derby", "h2", "hsqldb", "oracle")

    # ==========================================================
    # CACHÉ
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
                id, nombre, casa, especie, genero, nacimiento,
                nacionalidad, patronus, imagen
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
        for student in students:
            self.save_student_to_cache(student)

    def delete_student_from_cache(self, student_id: str) -> bool:
        with get_sqlite_connection() as conn:
            cursor = conn.execute(
                "DELETE FROM cache_students WHERE id = ?",
                (student_id,),
            )
            conn.commit()
            return cursor.rowcount > 0

    # ==========================================================
    # CONSULTAS
    # ==========================================================

    def get_all_students(self) -> list[Student]:
        """Devuelve los alumnos locales y los de la caché sin duplicarlos."""
        query = """
            SELECT id, nombre, casa, especie, genero,
                   nacimiento, nacionalidad, patronus, imagen
            FROM alumnos
        """
        with get_sqlite_connection() as conn:
            rows = conn.execute(query).fetchall()

        locales = [self._row_to_student(row) for row in rows]
        cache = self.get_students_from_cache()

        resultado = {student.id: student for student in cache}
        resultado.update({student.id: student for student in locales})

        return list(resultado.values())

    def get_student(self, student_id: str) -> Student | None:
        """Consulta primero los alumnos locales y después la caché."""
        with get_sqlite_connection() as conn:
            row = conn.execute(
                """
                SELECT id, nombre, casa, especie, genero,
                       nacimiento, nacionalidad, patronus, imagen
                FROM alumnos
                WHERE id = ?
                """,
                (student_id,),
            ).fetchone()

        if row:
            return self._row_to_student(row)

        return self.get_student_from_cache(student_id)

    def get_student_by_name(self, name: str) -> Student | None:
        """Busca un nombre exacto, ignorando mayúsculas y minúsculas."""
        if not name or not name.strip():
            raise ValueError("El nombre es obligatorio")

        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, nombre, casa, especie, genero,
                       nacimiento, nacionalidad, patronus, imagen
                FROM alumnos
                WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(?))
                """,
                (name.strip(),),
            ).fetchall()

        if len(rows) > 1:
            raise ValueError(
                "Hay varios alumnos locales con ese nombre. "
                "No se puede realizar la operación de forma segura."
            )

        if rows:
            return self._row_to_student(rows[0])

        coincidencias = [
            student
            for student in self.get_students_from_cache()
            if student.nombre
            and student.nombre.strip().casefold() == name.strip().casefold()
        ]

        if len(coincidencias) > 1:
            raise ValueError("Hay varios alumnos con ese nombre.")

        return coincidencias[0] if coincidencias else None

    def search_students_by_name(self, name: str) -> list[Student]:
        """Busca coincidencias por nombre en alumnos, caché y fuentes."""
        if not name or not name.strip():
            raise ValueError("El nombre es obligatorio")

        name = name.strip()
        encontrados: dict[str, Student] = {}

        with get_sqlite_connection() as conn:
            rows = conn.execute(
                """
                SELECT id, nombre, casa, especie, genero,
                       nacimiento, nacionalidad, patronus, imagen
                FROM alumnos
                WHERE LOWER(nombre) LIKE LOWER(?)
                """,
                (f"%{name}%",),
            ).fetchall()

        for row in rows:
            student = self._row_to_student(row)
            encontrados[student.id] = student

        for student in self.search_students_in_cache(name):
            encontrados[student.id] = student

        if encontrados:
            return list(encontrados.values())

        encontrados_fuentes: dict[str, Student] = {}

        for connector_name in self.SOURCE_CONNECTORS:
            try:
                connector = get_connector(connector_name)

                for raw_student in connector.get_student(name):
                    student = self._ensure_student(raw_student)
                    encontrados_fuentes[student.id] = student

            except Exception as exc:
                print(f"No se pudo consultar {connector_name}: {exc}")

        estudiantes = list(encontrados_fuentes.values())

        if estudiantes:
            self.save_students_to_cache(estudiantes)

        return estudiantes

    # ==========================================================
    # CRUD Y COLA DE SINCRONIZACIÓN
    # ==========================================================

    @staticmethod
    def _student_payload(student: Student) -> dict:
        datos = student.model_dump(mode="json")
        datos["id"] = student.id
        return datos

    def create_student(self, student: Student) -> Student:
        """Guarda el alumno y su operación CREATE en una transacción."""
        if not student.id:
            student.id = str(uuid.uuid4())

        nacimiento = (
            student.nacimiento.isoformat()
            if student.nacimiento is not None
            else None
        )
        payload = json.dumps(
            self._student_payload(student),
            ensure_ascii=False,
        )

        with get_sqlite_connection() as conn:
            conn.execute("BEGIN")

            conn.execute(
                """
                INSERT INTO alumnos (
                    id, nombre, casa, especie, genero,
                    nacimiento, nacionalidad, patronus, imagen
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """,
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

            conn.execute(
                """
                INSERT INTO pending_operations (
                    operation, student_id, nombre, nombre_editado, payload
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                ("CREATE", student.id, student.nombre, None, payload),
            )

            conn.commit()

        return student

    def update_student(self, name: str, student: Student) -> Student:
        """
        Actualiza por nombre exacto y registra el cambio en la misma
        transacción SQLite.
        """
        if not name or not name.strip():
            raise ValueError("El nombre del alumno es obligatorio")

        nombre_anterior = name.strip()
        nacimiento = (
            student.nacimiento.isoformat()
            if student.nacimiento is not None
            else None
        )

        with get_sqlite_connection() as conn:
            conn.execute("BEGIN")

            rows = conn.execute(
                """
                SELECT id, nombre
                FROM alumnos
                WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(?))
                """,
                (nombre_anterior,),
            ).fetchall()

            if len(rows) != 1:
                raise ValueError(
                    "No se encontró un único alumno local con ese nombre."
                )

            student.id = str(rows[0]["id"])

            payload = json.dumps(
                self._student_payload(student),
                ensure_ascii=False,
            )

            cursor = conn.execute(
                """
                UPDATE alumnos
                SET nombre = ?, casa = ?, especie = ?, genero = ?,
                    nacimiento = ?, nacionalidad = ?, patronus = ?,
                    imagen = ?
                WHERE id = ?
                """,
                (
                    student.nombre,
                    student.casa,
                    student.especie,
                    student.genero,
                    nacimiento,
                    student.nacionalidad,
                    student.patronus,
                    student.imagen,
                    student.id,
                ),
            )

            if cursor.rowcount != 1:
                raise RuntimeError("No se pudo actualizar el alumno.")

            conn.execute(
                """
                INSERT INTO pending_operations (
                    operation, student_id, nombre, nombre_editado, payload
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                (
                    "UPDATE",
                    student.id,
                    nombre_anterior,
                    student.nombre,
                    payload,
                ),
            )

            conn.commit()

        return student

    def delete_student(self, name: str) -> bool:
        """Elimina por nombre exacto y registra DELETE atómicamente."""
        if not name or not name.strip():
            raise ValueError("El nombre del alumno es obligatorio")

        nombre = name.strip()

        with get_sqlite_connection() as conn:
            conn.execute("BEGIN")

            rows = conn.execute(
                """
                SELECT id, nombre
                FROM alumnos
                WHERE LOWER(TRIM(nombre)) = LOWER(TRIM(?))
                """,
                (nombre,),
            ).fetchall()

            if len(rows) != 1:
                raise ValueError(
                    "No se encontró un único alumno local con ese nombre."
                )

            student_id = str(rows[0]["id"])
            nombre_real = rows[0]["nombre"]

            cursor = conn.execute(
                "DELETE FROM alumnos WHERE id = ?",
                (student_id,),
            )

            if cursor.rowcount != 1:
                raise RuntimeError("No se pudo eliminar el alumno.")

            conn.execute(
                """
                INSERT INTO pending_operations (
                    operation, student_id, nombre, nombre_editado, payload
                )
                VALUES (?, ?, ?, ?, ?)
                """,
                ("DELETE", student_id, nombre_real, None, None),
            )

            conn.commit()

        return True

    # ==========================================================
    # CONECTORES DE ORIGEN: SOLO LECTURA
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