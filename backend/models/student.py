from datetime import date

from pydantic import BaseModel


class Student(BaseModel):
    """
    Modelo que representa un registro de estudiante/personaje.

    Este modelo define la estructura común de los datos
    que manejará la API independientemente de la base de
    datos de origen.

    Attributes:
        id (str): Identificador único del registro.
        nombre (str): Nombre del personaje.
        casa (str): Casa a la que pertenece.
        especie (str): Especie del personaje.
        genero (str): Género del personaje.
        nacimiento (date | None): Fecha de nacimiento, si existe.
        nacionalidad (str): Nacionalidad del personaje.
        patronus (str | None): Patronus del personaje, si existe.
        imagen (str | None): URL de la imagen, si existe.
    """

    id: str
    nombre: str
    casa: str
    especie: str
    genero: str
    nacimiento: date | None = None
    nacionalidad: str
    patronus: str | None = None
    imagen: str | None = None


class StudentCreate(BaseModel):
    """
    Modelo utilizado para crear un nuevo estudiante.

    El identificador no se recibe desde el cliente,
    ya que será generado automáticamente por el backend.
    """

    nombre: str
    casa: str
    especie: str
    genero: str
    nacimiento: date | None = None
    nacionalidad: str
    patronus: str | None = None
    imagen: str | None = None

class StudentUpdate(BaseModel):
    """
    Modelo utilizado para actualizar un estudiante existente.

    El identificador del estudiante no se modifica.
    """

    nombre: str
    casa: str
    especie: str
    genero: str
    nacimiento: date | None = None
    nacionalidad: str
    patronus: str | None = None
    imagen: str | None = None