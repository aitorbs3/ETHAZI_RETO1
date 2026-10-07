from fastapi import APIRouter, HTTPException

from services.student_service import StudentService


# Creamos un router para agrupar todos los endpoints
# relacionados con los conectores de bases de datos.
#
# prefix="/connectors":
#   Hace que todas las rutas de este router empiecen
#   por /connectors.
#
# tags=["Connectors"]:
#   Agrupa estos endpoints bajo "Connectors" en la
#   documentación automática de FastAPI (/docs).
router = APIRouter(
    prefix="/connectors",
    tags=["Connectors"]
)


# Creamos una instancia del servicio que contiene
# la lógica necesaria para trabajar con los conectores.
#
# La API no realiza directamente las consultas a las
# bases de datos. Recibe la petición y delega el trabajo
# al StudentService.
service = StudentService()


@router.get("/{connector}/students")
def get_students_from_connector(connector: str):
    """
    Obtiene los estudiantes de una base de datos concreta.

    Args:
        connector (str): Nombre del conector que se quiere utilizar.

    Returns:
        list: Lista de estudiantes obtenidos de la base de datos.

    Raises:
        HTTPException: Error 400 si el conector no es válido
                       o se produce un error de validación.
    """

    # Delegamos la operación al servicio.
    #
    # El servicio será el encargado de decidir qué conector
    # utilizar y realizar la operación correspondiente.
    try:
        return service.get_students_from_connector(connector)

    # Si el servicio genera un ValueError, lo convertimos
    # en un error HTTP 400 (Bad Request).
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )


@router.get("/{connector}/students/{dni}")
def get_student_from_connector(
    connector: str,
    dni: str
):
    """
    Obtiene un estudiante concreto de una base de datos.

    Args:
        connector (str): Nombre del conector que se quiere utilizar.
        dni (str): DNI del estudiante que se quiere consultar.

    Returns:
        Student: Datos del estudiante encontrado.

    Raises:
        HTTPException: Error 400 si los datos proporcionados
                       no son válidos.
    """

    # Delegamos la consulta al servicio indicando tanto
    # el conector como el DNI del estudiante.
    try:
        return service.get_student_from_connector(
            connector,
            dni
        )

    # Convertimos los errores de validación del servicio
    # en respuestas HTTP 400.
    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error)
        )