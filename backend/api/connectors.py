"""Endpoints de solo lectura para consultar las bases históricas."""

# Importamos APIRouter para definir rutas modulares en FastAPI y HTTPException para gestionar códigos de error HTTP.
from fastapi import APIRouter, HTTPException

# Importamos la capa de servicios que concentra la lógica de negocio y la comunicación con los conectores.
from services.student_service import StudentService


# Creamos un enrutador (router) de FastAPI que agrupa todos los endpoints 
# bajo el prefijo "/connectors" y los categoriza en la documentación interactiva con la etiqueta "Connectors".
router = APIRouter(
    prefix="/connectors",
    tags=["Connectors"]
)


# Instanciamos el servicio principal que se encarga de coordinar las peticiones 
# hacia las diferentes bases de datos históricas del sistema.
service = StudentService()


@router.get("/{connector}/students")
def get_students_from_connector(connector: str):
    """
    Obtiene todos los estudiantes de una base de datos específica.

    Args:
        connector (str): Nombre del conector (ej. derby, h2, hsqldb, oracle).

    Returns:
        list: Lista de estudiantes encontrados en la base de datos seleccionada.

    Raises:
        HTTPException: Devuelve un código de error HTTP 400 si el conector indicado no es válido o no existe.
    """

    try:
        # Las consultas a las bases de datos históricas (Derby, H2, HSQLDB y Oracle) se realizan exclusivamente en modo lectura.
        return service.get_students_from_connector(connector)

    except ValueError as error:
        # Capturamos cualquier ValueError lanzado por el servicio o los conectores 
        # y lo transformamos en una respuesta HTTP 400 (Bad Request) con el detalle del error.
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
    Busca estudiantes por nombre en una base de datos concreta.

    Permite realizar búsquedas parciales e insensibles a mayúsculas/minúsculas. Por ejemplo:
    - Harry
    - Hermione
    - Potter

    Args:
        connector (str): Nombre del conector de base de datos.
        nombre (str): Nombre o fragmento del nombre del alumno a buscar.

    Returns:
        list: Lista de estudiantes que coinciden con el patrón de nombre indicado.

    Raises:
        HTTPException: Devuelve un código de error HTTP 400 si los parámetros o el conector no son válidos.
    """

    try:
        # El servicio valida el término de búsqueda y el conector ejecuta una consulta filtrada (LIKE).
        return service.get_student_from_connector(
            connector,
            nombre
        )

    except ValueError as error:
        # Gestionamos las excepciones de negocio devolviendo una respuesta HTTP 400 controlada al cliente.
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )