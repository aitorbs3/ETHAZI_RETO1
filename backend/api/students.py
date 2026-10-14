
from fastapi import APIRouter, HTTPException

from models.student import Student, StudentCreate
from services.student_service import StudentService


# Router para las operaciones de estudiantes.
router = APIRouter(
    prefix="/students",
    tags=["Students"]
)

# Servicio que gestiona la lógica de negocio.
service = StudentService()


@router.get("")
def get_students(nombre: str | None = None):
    """
    Consulta estudiantes.

    Si se proporciona un nombre, realiza una búsqueda
    mediante el servicio y el repositorio.

    Si no se proporciona, devuelve los alumnos
    actualmente almacenados en la caché.
    """
    try:
        if nombre is not None:
            return service.search_students_by_name(nombre)

        return service.get_all_students()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.post("")
def create_student(student: StudentCreate):
    """
    Crea un nuevo estudiante.

    El ID se genera automáticamente en el servicio.
    """
    try:
        return service.create_student(student)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.put("/{id}")
def update_student(id: str, student: Student):
    """
    Modifica un estudiante mediante su ID interno.

    El servicio impide modificar alumnos históricos.
    """
    try:
        return service.update_student(id, student)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.delete("/{id}")
def delete_student(id: str):
    """
    Elimina un estudiante mediante su ID interno.

    El servicio impide eliminar alumnos históricos.
    """
    try:
        return service.delete_student(id)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
