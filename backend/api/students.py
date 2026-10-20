"""Endpoints REST para consultar y gestionar alumnos desde la API."""

# Importamos APIRouter para modularizar las rutas de la API y HTTPException para gestionar códigos de error HTTP.
from fastapi import APIRouter, HTTPException

# Importamos los esquemas y modelos de Pydantic (Student, StudentCreate, StudentUpdate) y la capa de servicios.
from models.student import Student, StudentCreate, StudentUpdate
from services.student_service import StudentService


# Creamos un enrutador (router) de FastAPI para agrupar todos los endpoints 
# relacionados con los estudiantes bajo el prefijo "/students" y la etiqueta OpenAPI "Students".
router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

# Instanciamos el servicio principal que centraliza la lógica de negocio y las reglas de los alumnos.
service = StudentService()


@router.get("")
def get_students(nombre: str | None = None):
    """Lista los alumnos o filtra por nombre si se proporciona."""
    try:
        # Verificamos si se ha proporcionado el parámetro opcional de consulta por nombre.
        # Si existe, ejecutamos la búsqueda filtrada; en caso contrario, devolvemos el listado completo.
        if nombre is not None:
            return service.search_students_by_name(nombre)

        return service.get_all_students()

    except ValueError as error:
        # Capturamos cualquier error de validación del servicio y lo exponemos 
        # limpiamente como una respuesta HTTP 400 (Bad Request).
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/{student_id}")
def get_student(student_id: str):
    """Devuelve el alumno identificado o responde con HTTP 404."""
    try:
        # Intentamos recuperar un estudiante específico a través de su identificador único (ID).
        return service.get_student(student_id)

    except ValueError as error:
        # En este endpoint, si el servicio lanza un ValueError, indica que el ID solicitado no existe,
        # por lo que devolvemos un código HTTP 404 (Not Found) en lugar de un 400.
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.post("")
def create_student(student: StudentCreate):
    """Crea un alumno nuevo y convierte los errores de validación a HTTP 400."""
    try:
        # Delegamos en el servicio la lógica de creación del nuevo estudiante 
        # validando previamente la estructura de entrada mediante Pydantic.
        return service.create_student(student)

    except ValueError as error:
        # El esquema valida la forma de entrada y el servicio aplica las reglas de negocio.
        # Cualquier fallo de validación se traduce en una respuesta HTTP 400 (Bad Request).
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.put("/{student_id}")
def update_student(student_id: str, student: StudentUpdate):
    """Actualiza los datos del alumno sin permitir cambiar su identificador."""
    try:
        # El ID procede de la ruta URL; combinamos dicho identificador con los campos modificables 
        # recibidos en el cuerpo (payload) de la petición mediante el desempaquetado de Pydantic.
        datos = Student(
            id=student_id,
            **student.model_dump(),
        )

        return service.update_student_by_id(
            student_id,
            datos,
        )

    except ValueError as error:
        # Distinguimos de forma inteligente si el error se debe a la ausencia del alumno (HTTP 404) 
        # frente a otros rechazos o fallos de validación de datos (HTTP 400).
        status_code = (
            404
            if "No se encontró" in str(error)
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(error),
        )


@router.delete("/{student_id}")
def delete_student(student_id: str):
    """Elimina un alumno y traduce los errores del servicio a respuestas HTTP."""
    try:
        # Intentamos eliminar el registro del estudiante a través de su identificador único.
        return service.delete_student_by_id(student_id)

    except ValueError as error:
        # Mantenemos la misma semántica HTTP robusta que en la actualización:
        # devolvemos HTTP 404 si el registro no existe y HTTP 400 para cualquier otra excepción de negocio.
        status_code = (
            404
            if "No se encontró" in str(error)
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(error),
        )