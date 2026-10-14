from abc import abstractmethod

from connectors.base import BaseConnector
from models.student import Student


class BaseCRUDConnector(BaseConnector):
    """
    Clase base para los conectores que permiten leer y modificar
    estudiantes.

    Hereda de BaseConnector las funciones de lectura y añade
    las operaciones de crear, actualizar y eliminar estudiantes.
    """

    TABLE_NAME = "alumnos"

    @property
    @abstractmethod
    def placeholder(self) -> str:
        """
        Devuelve el marcador SQL utilizado por cada base de datos.

        Ejemplos:
        - JDBC: ?
        - MariaDB: %s
        """
        pass

    def create_student(self, student: Student) -> Student:
        """
        Añade un estudiante a la base de datos.
        """

        p = self.placeholder

        query = f"""
            INSERT INTO {self.TABLE_NAME} (
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
            VALUES ({', '.join([p] * 9)})
        """

        values = (
            student.id,
            student.nombre,
            student.casa,
            student.especie,
            student.genero,
            student.nacimiento,
            student.nacionalidad,
            student.patronus,
            student.imagen,
        )

        connection = self._connect()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(query, values)
            connection.commit()
            return student

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def update_student(self, student_id: str, student: Student) -> Student:
        """
        Actualiza los datos de un estudiante identificado por su ID.
        """

        p = self.placeholder

        query = f"""
            UPDATE {self.TABLE_NAME}
            SET nombre = {p},
                casa = {p},
                especie = {p},
                genero = {p},
                nacimiento = {p},
                nacionalidad = {p},
                patronus = {p},
                imagen = {p}
            WHERE id = {p}
        """

        values = (
            student.nombre,
            student.casa,
            student.especie,
            student.genero,
            student.nacimiento,
            student.nacionalidad,
            student.patronus,
            student.imagen,
            student_id,
        )

        connection = self._connect()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(query, values)

            # Comprobamos si el estudiante existe.
            # Puede haber 0 filas modificadas si los datos ya eran iguales.
            if cursor.rowcount == 0:
                cursor.execute(
                    f"SELECT id FROM {self.TABLE_NAME} WHERE id = {p}",
                    (student_id,),
                )

                if cursor.fetchone() is None:
                    raise ValueError(
                        f"No existe ningún estudiante con ID {student_id}"
                    )

            connection.commit()
            student.id = student_id
            return student

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def delete_student(self, student_id: str) -> bool:
        """
        Elimina un estudiante por su ID.

        Devuelve True si se ha eliminado y False si no existía.
        """

        p = self.placeholder
        query = f"DELETE FROM {self.TABLE_NAME} WHERE id = {p}"

        connection = self._connect()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(query, (student_id,))

            deleted = cursor.rowcount > 0

            connection.commit()
            return deleted

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()

    def delete_student_by_name(self, name: str) -> int:
        """
        Elimina los estudiantes cuyo nombre coincide exactamente,
        ignorando mayúsculas y minúsculas.

        Devuelve el número de estudiantes eliminados.
        """

        if not name or not name.strip():
            raise ValueError("El nombre del estudiante es obligatorio")

        p = self.placeholder

        query = f"""
            DELETE FROM {self.TABLE_NAME}
            WHERE LOWER(nombre) = LOWER({p})
        """

        connection = self._connect()
        cursor = None

        try:
            cursor = connection.cursor()
            cursor.execute(query, (name.strip(),))

            deleted = cursor.rowcount

            connection.commit()
            return deleted

        except Exception:
            connection.rollback()
            raise

        finally:
            if cursor is not None:
                cursor.close()
            connection.close()