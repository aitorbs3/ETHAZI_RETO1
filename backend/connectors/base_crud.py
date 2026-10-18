
"""Operaciones CRUD compartidas por los conectores con capacidad de escritura."""

# Permite definir métodos abstractos, que las clases hijas deberán implementar.
from abc import abstractmethod

# Importamos la clase base que contiene las operaciones comunes de conexión y lectura.
from connectors.base import BaseConnector

# Importamos el modelo Student, que representa los datos de un estudiante.
from models.student import Student


class BaseCRUDConnector(BaseConnector):
    """
    Clase base para los conectores que permiten leer y modificar estudiantes.

    Hereda de BaseConnector las funciones de lectura y añade las operaciones
    de crear, actualizar y eliminar estudiantes.
    """

    # Nombre de la tabla de la base de datos sobre la que se realizan las operaciones.
    # Se centraliza aquí para no repetir el nombre en cada consulta SQL.
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

        # Cada conector concreto debe implementar esta propiedad.
        # Así se utiliza el marcador que admite el controlador de la base de datos.
        pass

    def create_student(self, student: Student) -> Student:
        """
        Añade un estudiante a la base de datos.
        """

        # Obtenemos el marcador SQL específico del conector.
        p = self.placeholder

        # Construimos una consulta INSERT para insertar un nuevo estudiante.
        # Hay nueve columnas y, por tanto, nueve marcadores de parámetros.
        # join() une los marcadores mediante comas.
        # Por ejemplo, si p es '?', genera '?, ?, ?, ?, ?, ?, ?, ?, ?'.
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

        # Preparamos los valores que se insertarán en la consulta.
        # El orden debe coincidir con el de las columnas del INSERT.
        # Los valores se pasan por separado para evitar concatenarlos al SQL.
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

        # Abrimos una conexión con la base de datos.
        connection = self._connect()

        # Inicializamos el cursor a None por si falla su creación.
        # Así podemos comprobar después si hay que cerrarlo.
        cursor = None

        try:
            # Creamos un cursor, que permite ejecutar consultas SQL.
            cursor = connection.cursor()

            # Ejecutamos el INSERT pasando los parámetros por separado.
            cursor.execute(query, values)

            # Confirmamos la transacción para guardar los cambios.
            connection.commit()

            # Devolvemos el objeto Student insertado.
            return student

        except Exception:
            # Si se produce un error, deshacemos los cambios de la transacción.
            connection.rollback()

            # Volvemos a lanzar la excepción para que el código que llamó
            # al método pueda gestionar el error.
            raise

        finally:
            # Este bloque se ejecuta tanto si la operación funciona como si falla.

            # Cerramos el cursor solo si llegó a crearse.
            if cursor is not None:
                cursor.close()

            # Cerramos siempre la conexión que se ha abierto.
            connection.close()

    def update_student(self, student_id: str, student: Student) -> Student:
        """
        Actualiza los datos de un estudiante identificado por su ID.
        """

        # Obtenemos el marcador de parámetros compatible con el conector.
        p = self.placeholder

        # Construimos una consulta UPDATE para modificar los datos del estudiante.
        # El ID se utiliza en WHERE para seleccionar el registro que se actualizará.
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

        # Preparamos los nuevos valores en el mismo orden que aparecen
        # en SET. El último valor corresponde al ID utilizado en WHERE.
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

        # Abrimos la conexión y preparamos la variable del cursor.
        connection = self._connect()
        cursor = None

        try:
            # Creamos el cursor y ejecutamos la actualización.
            cursor = connection.cursor()
            cursor.execute(query, values)

            # Comprobamos si el controlador informa de cero filas modificadas.
            # Esto puede significar que el ID no existe o que los datos ya eran
            # iguales a los almacenados, dependiendo del controlador.
            if cursor.rowcount == 0:

                # Consultamos si existe un estudiante con ese ID.
                # Usamos el mismo marcador SQL y pasamos el ID como parámetro.
                cursor.execute(
                    f"SELECT id FROM {self.TABLE_NAME} WHERE id = {p}",
                    (student_id,),
                )

                # fetchone() devuelve una fila si existe; si no, devuelve None.
                if cursor.fetchone() is None:

                    # Si no existe, informamos del problema mediante una excepción.
                    raise ValueError(
                        f"No existe ningún estudiante con ID {student_id}"
                    )

            # Confirmamos los cambios realizados en la base de datos.
            connection.commit()

            # Actualizamos el ID del objeto recibido para que coincida
            # con el ID que se ha utilizado para identificar el registro.
            student.id = student_id

            # Devolvemos el objeto actualizado.
            return student

        except Exception:
            # Deshacemos la transacción si falla la actualización
            # o la comprobación de existencia.
            connection.rollback()

            # Propagamos el error al código que llamó al método.
            raise

        finally:
            # Cerramos los recursos independientemente del resultado.
            if cursor is not None:
                cursor.close()

            connection.close()

    def delete_student(self, student_id: str) -> bool:
        """
        Elimina un estudiante por su ID.

        Devuelve True si se ha eliminado y False si no existía.
        """

        # Obtenemos el marcador SQL correspondiente al controlador.
        p = self.placeholder

        # Creamos la consulta para eliminar el registro cuyo ID coincida.
        query = f"DELETE FROM {self.TABLE_NAME} WHERE id = {p}"

        # Abrimos la conexión e inicializamos el cursor.
        connection = self._connect()
        cursor = None

        try:
            # Creamos el cursor y ejecutamos el DELETE.
            # La tupla de un único elemento debe llevar una coma final.
            cursor = connection.cursor()
            cursor.execute(query, (student_id,))

            # rowcount indica cuántas filas informa el controlador que se han
            # visto afectadas por la operación.
            # Si es mayor que cero, consideramos que se ha eliminado un registro.
            deleted = cursor.rowcount > 0

            # Confirmamos la eliminación.
            connection.commit()

            # Devolvemos un booleano: True o False.
            return deleted

        except Exception:
            # Si ocurre un error, revertimos la transacción.
            connection.rollback()

            # Propagamos el error.
            raise

        finally:
            # Liberamos el cursor y la conexión.
            if cursor is not None:
                cursor.close()

            connection.close()

    def update_student_by_name(
        self,
        name: str,
        student: Student,
    ) -> Student:
        """
        Actualiza un estudiante por su nombre exacto,
        ignorando mayúsculas y minúsculas.

        Exige que exista exactamente un estudiante con ese nombre.
        """

        # Rechazamos nombres vacíos o que solo contengan espacios.
        # strip() elimina los espacios del principio y del final.
        if not name or not name.strip():
            raise ValueError("El nombre del estudiante es obligatorio")

        # Obtenemos el marcador SQL del conector.
        p = self.placeholder

        # Abrimos la conexión y preparamos el cursor.
        connection = self._connect()
        cursor = None

        try:
            # Creamos el cursor para ejecutar las consultas.
            cursor = connection.cursor()

            # Contamos cuántos estudiantes tienen ese nombre.
            # LOWER() convierte ambos textos a minúsculas para comparar
            # sin distinguir entre mayúsculas y minúsculas.
            cursor.execute(
                f"""
                SELECT COUNT(*)
                FROM {self.TABLE_NAME}
                WHERE LOWER(nombre) = LOWER({p})
                """,
                (name.strip(),),
            )

            # fetchone() devuelve la fila del COUNT(*).
            # El índice [0] obtiene el primer valor de esa fila: el recuento.
            cantidad = cursor.fetchone()[0]

            # Si no hay coincidencias, no se puede actualizar el estudiante.
            if cantidad == 0:
                raise ValueError(
                    f"No existe ningún estudiante con el nombre '{name}'"
                )

            # Si hay varias coincidencias, el nombre no identifica
            # un registro de forma inequívoca y sería peligroso actualizar.
            if cantidad > 1:
                raise ValueError(
                    f"Hay varios estudiantes con el nombre '{name}'. "
                    "No se puede actualizar de forma segura."
                )

            # Solo llegamos aquí si hay exactamente un estudiante con ese nombre.
            # Ejecutamos el UPDATE con los nuevos datos.
            cursor.execute(
                f"""
                UPDATE {self.TABLE_NAME}
                SET nombre = {p},
                    casa = {p},
                    especie = {p},
                    genero = {p},
                    nacimiento = {p},
                    nacionalidad = {p},
                    patronus = {p},
                    imagen = {p}
                WHERE LOWER(nombre) = LOWER({p})
                """,
                (
                    student.nombre,
                    student.casa,
                    student.especie,
                    student.genero,
                    student.nacimiento,
                    student.nacionalidad,
                    student.patronus,
                    student.imagen,
                    name.strip(),
                ),
            )

            # Confirmamos la actualización.
            connection.commit()

            # Devolvemos el objeto Student con los datos proporcionados.
            return student

        except Exception:
            # Deshacemos los cambios si falla alguna operación.
            connection.rollback()

            # Propagamos la excepción para que el llamador pueda gestionarla.
            raise

        finally:
            # Cerramos los recursos utilizados.
            if cursor is not None:
                cursor.close()

            connection.close()

    def delete_student_by_name(self, name: str) -> int:
        """
        Elimina los estudiantes cuyo nombre coincide exactamente,
        ignorando mayúsculas y minúsculas.

        Devuelve el número de estudiantes eliminados.
        """

        # Comprobamos que se ha proporcionado un nombre válido.
        if not name or not name.strip():
            raise ValueError("El nombre del estudiante es obligatorio")

        # Obtenemos el marcador SQL del conector.
        p = self.placeholder

        # Preparamos la consulta DELETE.
        # LOWER() permite comparar los nombres sin distinguir mayúsculas
        # y minúsculas. Se eliminarán todas las coincidencias.
        query = f"""
            DELETE FROM {self.TABLE_NAME}
            WHERE LOWER(nombre) = LOWER({p})
        """

        # Abrimos la conexión e inicializamos el cursor.
        connection = self._connect()
        cursor = None

        try:
            # Creamos el cursor y ejecutamos el borrado.
            cursor = connection.cursor()
            cursor.execute(query, (name.strip(),))

            # Obtenemos el número de filas que el controlador informa
            # como afectadas por la operación.
            deleted = cursor.rowcount

            # Confirmamos la eliminación.
            connection.commit()

            # Devolvemos el número de estudiantes eliminados.
            return deleted

        except Exception:
            # Deshacemos la transacción si se produce un error.
            connection.rollback()

            # Propagamos el error.
            raise

        finally:
            # Cerramos el cursor y la conexión.
            if cursor is not None:
                cursor.close()

            connection.close()
