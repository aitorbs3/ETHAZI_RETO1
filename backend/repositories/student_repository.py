import sqlite3
from models.student import Student
from connectors.connector_factory import get_connector
from connectors.sqlite_connector import get_sqlite_connection

class StudentRepository:
    def __init__(self):
        pass

    # ==========================================
    # MÉTODOS AUXILIARES DE CACHÉ SQLITE
    # ==========================================
    def get_student_from_cache(self, id: str) -> Student | None:
        """Busca un estudiante en la caché SQLite."""
        query = "SELECT * FROM cache_students WHERE id = ?"
        with get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id,))
            row = cursor.fetchone()
            if row:
                row_dict = dict(row)
                row_dict.pop("fecha_actualizacion", None)
                return Student(**row_dict)
        return None

    def save_student_to_cache(self, student: Student):
        """Guarda o actualiza un estudiante en la caché SQLite (UPSERT)."""
        query = """
        INSERT INTO cache_students (
            id, nombre, casa, alias, especie, genero, nacimiento,
            nacionalidad, patronus, patronus_origen, imagen, wiki, fecha_actualizacion
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ON CONFLICT(id) DO UPDATE SET
            nombre = excluded.nombre,
            casa = excluded.casa,
            alias = excluded.alias,
            especie = excluded.especie,
            genero = excluded.genero,
            nacimiento = excluded.nacimiento,
            nacionalidad = excluded.nacionalidad,
            patronus = excluded.patronus,
            patronus_origen = excluded.patronus_origen,
            imagen = excluded.imagen,
            wiki = excluded.wiki,
            fecha_actualizacion = CURRENT_TIMESTAMP;
        """
        with get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (
                student.id, student.nombre, student.casa, student.alias,
                student.especie, student.genero, student.nacimiento,
                student.nacionalidad, student.patronus, student.patronus_origen,
                student.imagen, student.wiki
            ))
            conn.commit()

    def delete_student_from_cache(self, id: str):
        """Elimina un estudiante de la caché SQLite."""
        query = "DELETE FROM cache_students WHERE id = ?"
        with get_sqlite_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query, (id,))
            conn.commit()

    # ==========================================
    # OPERACIONES CENTRALES Y DE FALLBACK
    # ==========================================
    def get_all_students(self):
        return []

    def get_student(self, id: str) -> Student | None:
        # 1. Intentar consultar en la caché SQLite primero
        try:
            student_cache = self.get_student_from_cache(id)
            if student_cache:
                return student_cache
        except Exception:
            pass # Si falla SQLite, continua hacia las BBDD principales

        # 2. Si no está en caché, consultar en MariaDB o BBDD de origen
        # (Sustituir por la consulta real a MariaDB cuando la tengáis)
        student = None 
        
        # 3. Si se encuentra el alumno en origen, actualizar en la caché
        if student:
            try:
                self.save_student_to_cache(student)
            except Exception:
                pass

        return student

    def create_student(self, student: Student) -> Student:
        # 1. Guardar en MariaDB (Sistema Central)
        # mariadb_conn.insert(student)

        # 2. Guardar en la caché SQLite
        try:
            self.save_student_to_cache(student)
        except Exception:
            pass
        return student

    def update_student(self, id: str, student: Student) -> Student:
        # 1. Actualizar en MariaDB
        # mariadb_conn.update(id, student)

        # 2. Actualizar en la caché SQLite
        try:
            self.save_student_to_cache(student)
        except Exception:
            pass
        return student

    def delete_student(self, id: str):
        # 1. Eliminar de MariaDB
        # mariadb_conn.delete(id)

        # 2. Eliminar de la caché SQLite
        try:
            self.delete_student_from_cache(id)
        except Exception:
            pass

        return {"id": id, "deleted": True}

    def get_students_from_connector(self, connector_name: str):
        connector = get_connector(connector_name)
        students = connector.get_students()
        
        # Opcional: Guardar en caché todos los consultados por conector
        for student in students:
            try:
                if isinstance(student, Student):
                    self.save_student_to_cache(student)
            except Exception:
                pass
        return students

    def get_student_from_connector(self, connector_name: str, id: str) -> Student | None:
        # 1. Buscar en caché
        try:
            student_cache = self.get_student_from_cache(id)
            if student_cache:
                return student_cache
        except Exception:
            pass

        # 2. Buscar mediante conector de la casa de origen
        connector = get_connector(connector_name)
        student = connector.get_student(id)

        # 3. Guardar en caché si existía en la casa de origen
        if student:
            try:
                if isinstance(student, dict):
                    student = Student(**student)
                self.save_student_to_cache(student)
            except Exception:
                pass

        return student