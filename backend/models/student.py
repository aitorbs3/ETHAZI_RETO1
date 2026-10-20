"""
Descripción: Define los esquemas de transferencia de datos (DTO) y validación utilizando Pydantic.
Actúa como contrato unificado entre las bases de datos heterogéneas (MariaDB, SQLite, Derby, H2, HSQLDB, Oracle)
y la interfaz REST de la API FastAPI.
"""

from datetime import date
from pydantic import BaseModel


class Student(BaseModel):
    """
    ========================================================================
    CLASE: Student (Modelo de Dominio / Respuesta Completa)
    ========================================================================
    Representa un registro unificado de estudiante o personaje en el sistema.
    
    ¿Por qué se utiliza Pydantic aquí?
        Pydantic valida automáticamente los tipos de datos en tiempo de ejecución.
        Si la base de datos devuelve un formato incorrecto (ej. un texto en lugar
        de un número o fecha), Pydantic intercepta el error antes de que corrompa la API.

    Atributos:
        id (str): Identificador único y estable (UUID o clave primaria).
        nombre (str | None): Nombre completo del personaje.
        casa (str | None): Casa a la que pertenece (Gryffindor, Slytherin, etc.).
        especie (str | None): Especie biológica (humano, fantasma, gigante...).
        genero (str | None): Género del personaje.
        nacimiento (date | None): Fecha exacta de nacimiento (convertida a objeto date).
        nacionalidad (str | None): País o procedencia de origen.
        patronus (str | None): Forma corpórea o incorpórea de su hechizo Patronus.
        imagen (str | None): Enlace URL o ruta a la fotografía del personaje.
    """

    # 1. Identificador único obligatorio: es la clave primaria que no puede faltar 
    # para correlacionar al alumno entre la caché local y la base central.
    id: str
    
    # 2. Atributos opcionales (unión de tipos: tipo o None).
    # Se inicializan por defecto a None porque las fuentes de datos históricas 
    # (como Derby u Oracle) suelen tener campos incompletos o nulos en sus tablas antiguas.
    nombre: str | None = None
    casa: str | None = None
    especie: str | None = None
    genero: str | None = None
    nacimiento: date | None = None
    nacionalidad: str | None = None
    patronus: str | None = None
    imagen: str | None = None


class StudentCreate(BaseModel):
    """
    ========================================================================
    CLASE: StudentCreate (Modelo de Entrada para Inserciones / POST)
    ========================================================================
    Define la estructura exacta que el cliente (frontend o script externo) 
    debe enviar al realizar una petición HTTP POST para registrar un nuevo alumno.

    Regla de negocio clave:
        El cliente NO envía el identificador (id). El backend es el único 
        responsable de generarlo automáticamente (por ejemplo, mediante UUID v4)
        para garantizar la unicidad y evitar colisiones de IDs distribuidos.
    """

    # El campo 'id' se omite intencionadamente.
    nombre: str
    casa: str | None = None
    especie: str | None = None
    genero: str | None = None
    nacimiento: date | None = None
    nacionalidad: str | None = None
    patronus: str | None = None
    imagen: str | None = None


class StudentUpdate(BaseModel):
    """
    ========================================================================
    CLASE: StudentUpdate (Modelo de Entrada para Modificaciones / PUT)
    ========================================================================
    Define los campos que pueden ser modificados al actualizar un registro existente
    mediante una petición HTTP PUT.

    Regla de diseño REST:
        El identificador del estudiante viaja en la propia URL (ej. /students/123-abc),
        por lo que el cuerpo (payload) de la petición HTTP solo debe contener 
        los atributos editables del recurso.
    """

    # El cuerpo de la petición contiene únicamente los campos actualizables.
    nombre: str
    casa: str | None = None
    especie: str | None = None
    genero: str | None = None
    nacimiento: date | None = None
    nacionalidad: str | None = None
    patronus: str | None = None
    imagen: str | None = None