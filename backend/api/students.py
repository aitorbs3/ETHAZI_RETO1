from fastapi import APIRouter, HTTPException

from models.student import Student
from services.student_service import StudentService


# Creamos un router para agrupar todos los endpoints
# relacionados con los estudiantes.
#
# prefix="/students":
#   Hace que todas las rutas de este router empiecen
#   por /students.
#
# tags=["Students"]:
#   Agrupa estos endpoints bajo "Students" en la
#   documentación automática de FastAPI (/docs).
router = APIRouter(
    prefix="/students",
    tags=["Students"]
)


# Creamos una instancia del servicio que contiene
# la lógica de las operaciones de estudiantes.
#
# La API NO realiza directamente consultas a las bases de datos.
# La API recibe la petición y delega el trabajo al servicio.
service = StudentService()


@router.get("")
def get_students():
    """
    Obtiene todos los estudiantes almacenados en el sistema central.

    Returns:
        list: Lista de estudiantes.
    """

    # La API delega la operación al servicio.
    return service.get_all_students()


@router.get("/{id}")
def get_student(id: str):
    """
    Obtiene un estudiante mediante su identificador.

    Args:
        id (str): Identificador del estudiante que se quiere consultar.

    Returns:
        Student: Datos del estudiante encontrado.

    Raises:
        HTTPException: Error 404 si el estudiante no existe.
    """

    # Pedimos al servicio que busque el estudiante.
    student = service.get_student(id)

    # Si el servicio no encuentra ningún estudiante,
    # devolvemos un error HTTP 404 (Not Found).
    if student is None:
        raise HTTPException(
            status_code=404,
            detail="Estudiante no encontrado"
        )

    # Si existe, FastAPI convierte el resultado
    # en una respuesta JSON.
    return student


@router.post("")
def create_student(student: Student):
    """
    Crea un nuevo estudiante en el sistema central.
    Args:
        student (Student): Datos del estudiante que se quiere crear.
    Returns:
        Student: Estudiante creado.
    """

    # FastAPI valida previamente que los datos recibidos
    # cumplen el modelo Student.
    #
    # Después delegamos la creación al servicio.
    return service.create_student(student)


@router.put("/{id}")
def update_student(id: str, student: Student):
    """
    Actualiza los datos de un estudiante existente.

    Args:
        id (str): Identificador del estudiante que se quiere modificar.
        student (Student): Nuevos datos del estudiante.

    Returns:
        Student: Estudiante actualizado.
    """

    # Delegamos la modificación al servicio.
    return service.update_student(id, student)


@router.delete("/{id}")
def delete_student(id: str):
    """
    Elimina un estudiante del sistema central.

    Args:
        id (str): Identificador del estudiante que se quiere eliminar.

    Returns:
        Any: Resultado de la operación de eliminación.
    """

    # Delegamos la eliminación al servicio.
    return service.delete_student(id)