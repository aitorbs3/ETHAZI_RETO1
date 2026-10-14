from fastapi import APIRouter, HTTPException

from models.student import Student, StudentCreate, StudentUpdate
from services.student_service import StudentService


router = APIRouter(
    prefix="/students",
    tags=["Students"],
)

service = StudentService()


@router.get("")
def get_students(nombre: str | None = None):
    try:
        if nombre is not None:
            return service.search_students_by_name(nombre)

        return service.get_all_students()

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.get("/{student_id}")
def get_student(student_id: str):
    try:
        return service.get_student(student_id)

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )


@router.post("")
def create_student(student: StudentCreate):
    try:
        return service.create_student(student)

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )


@router.put("/{student_id}")
def update_student(student_id: str, student: StudentUpdate):
    try:
        datos = Student(
            id=student_id,
            **student.model_dump(),
        )

        return service.update_student_by_id(
            student_id,
            datos,
        )

    except ValueError as error:
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
    try:
        return service.delete_student_by_id(student_id)

    except ValueError as error:
        status_code = (
            404
            if "No se encontró" in str(error)
            else 400
        )

        raise HTTPException(
            status_code=status_code,
            detail=str(error),
        )