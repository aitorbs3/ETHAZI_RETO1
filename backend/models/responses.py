"""Esquemas Pydantic para las respuestas estructuradas de la API."""

# Importamos BaseModel de Pydantic para definir los modelos de validación y estructuración de datos.
from pydantic import BaseModel

# Importamos el modelo base Student que representa los datos de un alumno en el sistema.
from models.student import Student


class StudentResponse(BaseModel):
    """
    Respuesta de la API para un único estudiante.
    """

    # Indicador booleano de éxito de la operación.
    success: bool
    
    # Objeto Student devuelto, o None si el registro puede faltar o la operación no devuelve un alumno.
    student: Student | None = None


class StudentsResponse(BaseModel):
    """
    Respuesta de la API para una lista de estudiantes.
    """

    # Indicador booleano de éxito de la operación.
    success: bool
    
    # Lista con los estudiantes encontrados (puede ser una lista vacía si la consulta no devuelve coincidencias).
    students: list[Student]


class MessageResponse(BaseModel):
    """
    Respuesta de la API para operaciones que no necesitan
    devolver un estudiante (por ejemplo, confirmaciones de borrado o mensajes de éxito).
    """

    # Indicador booleano de éxito de la operación.
    success: bool
    
    # Mensaje descriptivo con el resultado de la ejecución.
    message: str