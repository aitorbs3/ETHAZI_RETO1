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
        alias (str | None): Alias del personaje, si existe.
        especie (str): Especie del personaje.
        genero (str): Género del personaje.
        nacimiento (str | None): Fecha o información de nacimiento.
        nacionalidad (str): Nacionalidad del personaje.
        patronus (str | None): Patronus del personaje, si existe.
        patronus_origen (str): Indica el origen o disponibilidad
            del Patronus.
        imagen (str | None): URL de la imagen, si existe.
        wiki (str | None): URL de la página wiki, si existe.
    """

    id: str
    nombre: str
    casa: str
    alias: str | None = None
    especie: str
    genero: str
    nacimiento: str | None = None
    nacionalidad: str
    patronus: str | None = None
    patronus_origen: str
    imagen: str | None = None
    wiki: str | None = None