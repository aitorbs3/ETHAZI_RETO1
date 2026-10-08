import os
from pathlib import Path
import jaydebeapi
import jpype
from backend.utils.config import obtener_variable
from backend.models.student import Student


BASE_DIR = Path(__file__).resolve().parents[2]
H2_JAR = BASE_DIR / "backend" / "drivers" / "h2" / "h2.jar"
DRIVER_CLASS = "org.h2.Driver"


def obtener_conexion_h2():
    # Lee H2_DATABASE; si no existe en el .env, obtener_variable
    # lanzará el RuntimeError automáticamente
    h2_db_path = obtener_variable("H2_DATABASE", obligatoria=True)

    # Construcción de la URL JDBC
    h2_url = f"jdbc:h2:{h2_db_path};AUTO_SERVER=TRUE;DB_CLOSE_DELAY=-1"

    usuario = obtener_variable(
        "H2_USER",
        obligatoria=False
    ) or "sa"

    password = obtener_variable(
        "H2_PASSWORD",
        obligatoria=False
    ) or ""

    if not H2_JAR.exists():
        raise FileNotFoundError(
            f"No se encontró el driver JDBC en: {H2_JAR}"
        )

    try:
        if not jpype.isJVMStarted():
            jpype.startJVM(
                jpype.getDefaultJVMPath(),
                f"-Djava.class.path={H2_JAR}"
            )

        return jaydebeapi.connect(
            DRIVER_CLASS,
            h2_url,
            [usuario, password],
            str(H2_JAR)
        )

    except Exception as e:
        print(f"Error al conectar con H2: {e}")
        raise e


class H2Connector:
    """
    Conector de solo lectura para H2.

    H2 actúa como una de las bases de datos de origen
    de los estudiantes.
    """

    def get_students(self) -> list[Student]:
        """
        Obtiene todos los alumnos de la tabla alumnos.
        """

        connection = obtener_conexion_h2()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
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
                """
            )

            rows = cursor.fetchall()

            return [
                self._row_to_student(row)
                for row in rows
            ]

        finally:
            connection.close()

    def get_student(self, student_id: str) -> Student | None:
        """
        Obtiene un alumno mediante su identificador.
        """

        connection = obtener_conexion_h2()

        try:
            cursor = connection.cursor()

            cursor.execute(
                """
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
                WHERE id = ?
                """,
                (student_id,)
            )

            row = cursor.fetchone()

            if row is None:
                return None

            return self._row_to_student(row)

        finally:
            connection.close()

    @staticmethod
    def _row_to_student(row) -> Student:
        """
        Convierte una fila obtenida de H2 en un objeto Student.
        """

        return Student(
            id=str(row[0]),
            nombre=row[1],
            casa=row[2],
            especie=row[3],
            genero=row[4],
            nacimiento=row[5],
            nacionalidad=row[6],
            patronus=row[7],
            imagen=row[8]
        )