from pydantic import BaseModel

from backend.models.student import Student


class StudentResponse(BaseModel):
    """
    Respuesta de la API para un único estudiante.
    """

    success: bool
    student: Student | None = None


class StudentsResponse(BaseModel):
    """
    Respuesta de la API para una lista de estudiantes.
    """

    success: bool
    students: list[Student]


class MessageResponse(BaseModel):
    """
    Respuesta de la API para operaciones que no necesitan
    devolver un estudiante.
    """

    success: bool
    message: str