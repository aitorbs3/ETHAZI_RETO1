"""Acceso a alumnos locales, caché y bases históricas de solo lectura."""

import json
import uuid
from datetime import date

from models.student import Student
from connectors.connector_factory import get_connector
from connectors.sqlite_connector import get_sqlite_connection


class StudentRepository:
    """Centraliza consultas, escrituras locales y cola de sincronización."""

    SOURCE_CONNECTORS = ("derby", "h2", "hsqldb", "oracle")

    # ==========================================================
    # CACHÉ
    # ==========================================================

    def get_student_from_cache(self, student_id: str) -> Student | None:
        """Busca en caché un alumno por su identificador."""
        # La clave primaria hace que la lectura devuelva como máximo una fila.
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
        """Devuelve todos los alumnos almacenados en la caché SQLite."""
        # El modelo común oculta las diferencias entre sqlite3.Row y otros drivers.
        query = """
            SELECT id, nombre, casa, especie, genero,
                   nacimiento, nacionalidad, patronus, imagen
            FROM cache_students
        """
        with get_sqlite_connection() as conn:
            rows = conn.execute(query).fetchall()

        return [self._row_to_student(row) for row in rows]

    def search_students_in_cache(self, name: str) -> list[Student]:
        """Busca coincidencias parciales por nombre en la caché."""
        # LIKE permite reutilizar el mismo comportamiento de búsqueda parcial.
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
        """Inserta o actualiza en caché el alumno recibido."""
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

        # La caché persiste las fechas de Python como texto ISO en SQLite.
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
        """Guarda en caché cada alumno de la colección."""
        # Se reutiliza el upsert individual para mantener una sola regla de escritura.
        for student in students:
            self.save_student_to_cache(student)

    def delete_student_from_cache(self, student_id: str) -> bool:
        """Elimina un alumno de la caché e indica si existía."""
        # rowcount indica si se encontró una fila con ese ID.
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

        # El ID unifica ambas colecciones; lo local prevalece sobre una copia
        # cacheada del mismo registro.
        resultado = {student.id: student for student in cache}
        resultado.update({student.id: student for student in locales})

        return list(resultado.values())

    def get_student(self, student_id: str) -> Student | None:
        """Busca por UUID primero en los alumnos locales y después en caché."""
        # La tabla alumnos tiene prioridad porque contiene las escrituras locales.
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
        """Busca un nombre exacto. No permite resolver nombres duplicados."""
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
                "Selecciona el alumno que quieres modificar."
            )

        if rows:
            return self._row_to_student(rows[0])

        # Para no abrir conexiones a los orígenes, esta resolución por nombre
        # se limita a los datos locales y a los que ya están cacheados.
        coincidencias = [
            student
            for student in self.get_students_from_cache()
            if student.nombre
            and student.nombre.strip().casefold() == name.strip().casefold()
        ]

        if len(coincidencias) > 1:
            raise ValueError(
                "Hay varios alumnos con ese nombre. "
                "Selecciona el alumno que quieres modificar."
            )

        return coincidencias[0] if coincidencias else None

    def search_students_by_name(self, name: str) -> list[Student]:
        """Busca coincidencias parciales por nombre en SQLite y fuentes."""
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

        # Combinar por ID evita duplicados entre datos locales y cacheados.
        for row in rows:
            student = self._row_to_student(row)
            encontrados[student.id] = student

        for student in self.search_students_in_cache(name):
            encontrados[student.id] = student

        # Si SQLite ya tiene resultados, no consultamos las fuentes externas:
        # la copia local es más rápida y evita consultas remotas innecesarias.
        if encontrados:
            return list(encontrados.values())

        # Sin coincidencias locales, se consultan las casas históricas y se
        # combinan sus resultados usando el ID como clave.
        encontrados_fuentes: dict[str, Student] = {}

        for connector_name in self.SOURCE_CONNECTORS:
            try:
                connector = get_connector(connector_name)

                for raw_student in connector.get_student(name):
                    student = self._ensure_student(raw_student)
                    encontrados_fuentes[student.id] = student

            except Exception as exc:
                # Un origen no disponible no impide consultar los restantes.
                print(f"No se pudo consultar {connector_name}: {exc}")

        # Guardar el resultado permite responder desde SQLite en búsquedas futuras.
        estudiantes = list(encontrados_fuentes.values())

        if estudiantes:
            self.save_students_to_cache(estudiantes)

        return estudiantes

    # ==========================================================
    # CRUD Y COLA DE SINCRONIZACIÓN
    # ==========================================================

    @staticmethod
    def _student_payload(student: Student) -> dict:
        """Serializa un alumno a un diccionario compatible con JSON."""
        # mode="json" convierte date y demás tipos especiales a valores serializables.
        datos = student.model_dump(mode="json")
        datos["id"] = student.id
        return datos

    def create_student(self, student: Student) -> Student:
        """Crea el alumno y encola CREATE dentro de una transacción SQLite."""
        # El UUID se genera en el backend para que todos los sistemas usen el
        # mismo identificador durante la sincronizacion.
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

        # Alta y cola comparten transacción: el cambio local no puede quedar
        # confirmado si no se registró también para sincronizarse.
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

    def update_student_by_id(
        self,
        student_id: str,
        student: Student,
    ) -> Student:
        """Actualiza exclusivamente el alumno identificado por UUID."""
        if not student_id:
            raise ValueError("El identificador del alumno es obligatorio")

        student.id = student_id

        nacimiento = (
            student.nacimiento.isoformat()
            if student.nacimiento is not None
            else None
        )

        # El estado actualizado y el evento de sincronización se confirman juntos.
        with get_sqlite_connection() as conn:
            conn.execute("BEGIN")

            row = conn.execute(
                "SELECT nombre, casa FROM alumnos WHERE id = ?",
                (student_id,),
            ).fetchone()

            if row is None:
                raise ValueError("No se encontró el alumno seleccionado.")

            if (row["casa"] or "").strip().casefold() != "hogwarths":
                raise ValueError(
                    "Solo se pueden modificar alumnos nuevos de Hogwarths."
                )

            if row is None:
                raise ValueError("No se encontró el alumno seleccionado.")

            nombre_anterior = row["nombre"]

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
                    student_id,
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
                    student_id,
                    nombre_anterior,
                    student.nombre,
                    payload,
                ),
            )

            conn.commit()

        return student


    def delete_student_by_id(self, student_id: str) -> bool:
        """
        Elimina por ID únicamente alumnos nuevos de Hogwarths.
        Registra la operación pendiente de sincronización con MariaDB.
        """

        if not student_id:
            raise ValueError("El identificador del alumno es obligatorio")

        # Borrar y encolar DELETE en una sola transacción permite propagarlo
        # a MariaDB aunque la conexión remota falle durante esta solicitud.
        with get_sqlite_connection() as conn:
            conn.execute("BEGIN")

            row = conn.execute(
                """
                SELECT nombre, casa
                FROM alumnos
                WHERE id = ?
                """,
                (student_id,),
            ).fetchone()

            if row is None:
                raise ValueError("No se encontró el alumno seleccionado.")

            # Impedir el borrado de alumnos históricos
            if (row["casa"] or "").strip().casefold() != "hogwarths":
                raise ValueError(
                    "Solo se pueden eliminar alumnos nuevos de Hogwarths."
                )

            nombre_real = row["nombre"]

            cursor = conn.execute(
                "DELETE FROM alumnos WHERE id = ?",
                (student_id,),
            )

            if cursor.rowcount != 1:
                raise RuntimeError("No se pudo eliminar el alumno.")

            # Registrar operación para sincronizar con MariaDB
            conn.execute(
                """
                INSERT INTO pending_operations (
                    operation, student_id, nombre,
                    nombre_editado, payload
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
        """Obtiene y normaliza todos los alumnos de una fuente histórica."""
        # La fábrica valida el nombre y devuelve la implementación correspondiente.
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
        """Busca y normaliza alumnos por nombre en una fuente histórica."""
        # Se mantiene la búsqueda en la fuente indicada, sin consultar otras casas.
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
        """Convierte una fila de SQLite en el modelo común Student."""
        # SQLite devuelve la fecha como texto; el modelo común espera date.
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
        """Normaliza una instancia o diccionario al modelo Student."""
        # Se aceptan las dos representaciones emitidas por los conectores.
        if isinstance(student, Student):
            return student

        if isinstance(student, dict):
            return Student(**student)

        raise TypeError(
            f"Tipo de estudiante no soportado: {type(student)}"
        )
