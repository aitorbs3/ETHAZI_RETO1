# Este servicio actúa como la capa intermedia (Capa de Negocio) entre los endpoints de la API
# y los repositorios de datos, aplicando validaciones, reglas de casas históricas y sincronización offline-first.

from datetime import datetime

from models.student import Student, StudentCreate
from repositories.student_repository import StudentRepository
from services.sync_service import SyncService

# Conjunto inmutable que define las casas históricas de solo lectura.
# Las operaciones de escritura (crear, actualizar, borrar) están estrictamente prohibidas en estas casas.
CASAS_HISTORICAS_SOLO_LECTURA = {
    "gryffindor",
    "slytherin",
    "hufflepuff",
    "ravenclaw",
}


class StudentService:
    # Clase principal que coordina la lógica de negocio para la gestión de alumnos.

    def __init__(self):
        # Inicializamos las dependencias necesarias para la persistencia y la sincronización remota.
        # StudentRepository gestiona las bases de datos locales y cacheadas.
        self.repository = StudentRepository()
        # SyncService gestiona la comunicación con la base de datos central MariaDB mediante una cola de eventos.
        self.sync_service = SyncService()
        # Almacena el estado y metadatos de la última sincronización ejecutada.
        self.ultima_sincronizacion = None

    def _intentar_sincronizar(self):
        # Método auxiliar privado para intentar volcar las operaciones pendientes a MariaDB.
        # Se aplica una estrategia resiliente: si MariaDB no está disponible, la app no se cae.
        try:
            # Ejecutamos el servicio de sincronización de la cola pendiente
            resultado = self.sync_service.sincronizar_pendientes()
            # Actualizamos los metadatos de la última sincronización con marca de tiempo ISO
            self.ultima_sincronizacion = {
                "fecha": datetime.now().isoformat(),
                "resultado": resultado,
            }
            return resultado
        except Exception as error:
            # Capturamos cualquier error de red o caída de MariaDB.
            # Como los datos ya están seguros en SQLite (local), informamos por consola
            # pero mantenemos las operaciones encoladas para el siguiente arranque o reintento.
            print(f"No se pudo sincronizar con MariaDB: {error}")
            return {
                "procesadas": 0,
                "fallidas": 0,
                "detalles": [],
                "error": str(error),
            }

    @staticmethod
    def _validar_nombre(nombre: str | None):
        # Valida que el nombre proporcionado no sea nulo ni consista únicamente en espacios en blanco.
        # El método strip() elimina espacios al principio y al final.
        if nombre is None or not nombre.strip():
            raise ValueError("El nombre del alumno es obligatorio.")

    @staticmethod
    def _validar_casa_historica(casa: str | None):
        # Restricción de dominio: impide realizar operaciones de modificación sobre casas históricas.
        # Usamos casefold() para realizar una comparación insensible a mayúsculas/minúsculas de forma robusta.
        if casa and casa.strip().casefold() in CASAS_HISTORICAS_SOLO_LECTURA:
            raise ValueError(
                "No se pueden modificar ni eliminar alumnos "
                "de las casas históricas."
            )

    def get_all_students(self) -> list[Student]:
        # Recupera de forma unificada todos los alumnos locales y los almacenados en caché.
        return self.repository.get_all_students()

    def get_student(self, student_id: str) -> Student:
        # Busca un alumno por su identificador único (UUID).
        student = self.repository.get_student(student_id)

        # Si el repositorio devuelve None, lanzamos un ValueError que el controlador transformará en un código HTTP 404.
        if student is None:
            raise ValueError("No se encontró el alumno.")

        return student

    def search_students_by_name(self, nombre: str) -> list[Student]:
        # Valida la corrección del término de búsqueda y delega la consulta parcial al repositorio.
        self._validar_nombre(nombre)
        return self.repository.search_students_by_name(nombre)

    def create_student(self, student_data: StudentCreate) -> Student:
        # Orquesta la creación de un nuevo alumno aplicando las reglas de negocio y persistencia local.
        # 1. Validamos que el nombre no esté vacío.
        self._validar_nombre(student_data.nombre)
        # 2. Comprobamos que no se intente crear un alumno directamente en una casa histórica restringida.
        self._validar_casa_historica(student_data.casa)

        # Instanciamos el modelo Student dejando el ID vacío para que el repositorio asigne un UUID v4.
        student = Student(
            id="",
            **student_data.model_dump(),
        )

        # 3. Guardamos localmente en SQLite (prioridad alta para garantizar la disponibilidad offline).
        creado = self.repository.create_student(student)
        
        # 4. Intentamos sincronizar de inmediato el cambio con la base central MariaDB.
        self._intentar_sincronizar()

        return creado

    def update_student_by_id(
        self,
        student_id: str,
        student_data: Student,
    ) -> Student:
        # Actualiza los datos de un alumno existente aplicando controles estrictos de dominio.
        # Verificamos que el ID de la ruta no esté vacío.
        if not student_id or not student_id.strip():
            raise ValueError("El identificador del alumno es obligatorio.")

        # Comprobamos que el alumno realmente exista en el sistema local.
        alumno_actual = self.repository.get_student(student_id)

        if alumno_actual is None:
            raise ValueError("No se encontró el alumno seleccionado.")

        # Regla de negocio: las modificaciones de escritura están restringidas exclusivamente 
        # a alumnos nuevos de la casa unificada "Hogwarths".
        if (alumno_actual.casa or "").strip().casefold() != "hogwarths":
            raise ValueError(
                "Solo se pueden modificar alumnos nuevos de Hogwarths."
            )

        # Regla de negocio: no se permite alterar la casa de pertenencia de un alumno ya registrado.
        if (student_data.casa or "").strip().casefold() != "hogwarths":
            raise ValueError(
                "No se puede cambiar la casa de un alumno nuevo."
            )

        # Validamos el nuevo nombre proporcionado.
        self._validar_nombre(student_data.nombre)

        # Comprobamos restricciones sobre las casas históricas por seguridad adicional.
        self._validar_casa_historica(alumno_actual.casa)
        self._validar_casa_historica(student_data.casa)

        # Asignamos el ID de la ruta al objeto de datos recibido.
        student_data.id = student_id

        # Ejecutamos la actualización local en SQLite y encolamos la operación pendiente para MariaDB.
        actualizado = self.repository.update_student_by_id(
            student_id,
            student_data,
        )

        # Intentamos sincronizar los cambios pendientes con la base central.
        self._intentar_sincronizar()

        return actualizado

    def delete_student_by_id(self, student_id: str) -> dict:
        # Elimina un alumno del sistema aplicando el mismo principio de protección de las casas históricas.
        # Validamos que el identificador sea una cadena válida.
        if not student_id or not student_id.strip():
            raise ValueError("El identificador del alumno es obligatorio.")

        student_id = student_id.strip()

        # Localizamos al alumno en la base de datos.
        alumno = self.repository.get_student(student_id)

        if alumno is None:
            raise ValueError("No se encontró el alumno seleccionado.")

        # Restricción: solo se permite eliminar registros de la casa "Hogwarths".
        if (alumno.casa or "").strip().casefold() != "hogwarths":
            raise ValueError(
                "Solo se pueden eliminar alumnos nuevos de Hogwarths."
            )

        # Ejecutamos el borrado local (esto elimina el registro en SQLite y registra el evento DELETE en la cola).
        eliminado = self.repository.delete_student_by_id(student_id)

        if not eliminado:
            raise RuntimeError("No se pudo eliminar el alumno.")

        # Intentamos propagar el borrado hacia MariaDB de manera síncrona/asíncrona.
        resultado_sync = self._intentar_sincronizar()

        # Retornamos un diccionario con el informe de la operación local y de sincronización.
        return {
            "mensaje": "Alumno eliminado localmente.",
            "student_id": student_id,
            "sincronizacion": resultado_sync,
        }

    def get_students_from_connector(
        self,
        connector_name: str,
    ) -> list[Student]:
        # Consulta y recupera todos los alumnos directamente de un conector histórico específico (ej. derby, h2).
        return self.repository.get_students_from_connector(connector_name)

    def get_student_from_connector(
        self,
        connector_name: str,
        nombre: str,
    ) -> list[Student]:
        # Realiza una búsqueda filtrada por nombre en una base de datos histórica de solo lectura.
        # Validamos primero el término de búsqueda antes de abrir la conexión JDBC/nativa.
        self._validar_nombre(nombre)
        return self.repository.get_student_from_connector(
            connector_name,
            nombre,
        )