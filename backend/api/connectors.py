
from fastapi import APIRouter, HTTPException

from services.student_service import StudentService


# Router que agrupa los endpoints relacionados
# con los conectores de bases de datos.
router = APIRouter(
    prefix="/connectors",
    tags=["Connectors"]
)


# Instancia del servicio que gestiona la lógica
# de acceso a los diferentes conectores.
service = StudentService()


@router.get("/{connector}/students")
def get_students_from_connector(connector: str):
    """
    Obtiene todos los estudiantes de una base de datos.

    Args:
        connector (str): Nombre del conector.

    Returns:
        list: Lista de estudiantes encontrados.

    Raises:
        HTTPException: Error 400 si el conector no es válido.
    """

    try:
        return service.get_students_from_connector(connector)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/{connector}/students/{nombre}")
def get_student_from_connector(
    connector: str,
    nombre: str
):
    """
    Busca estudiantes por nombre en una base de datos.

    Permite búsquedas parciales. Por ejemplo:
    - Harry
    - Hermione
    - Potter

    Args:
        connector (str): Nombre del conector.
        nombre (str): Nombre o parte del nombre del alumno.

    Returns:
        list: Lista de estudiantes que coinciden
              con el nombre indicado.

    Raises:
        HTTPException: Error 400 si los datos
                       proporcionados no son válidos.
    """

    try:
        return service.get_student_from_connector(
            connector,
            nombre
        )

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )
