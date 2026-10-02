from fastapi import FastAPI

"""
Módulo principal de la API del Reto 01.

Este módulo inicializa la aplicación FastAPI y define los
endpoints básicos de comprobación del funcionamiento del backend.
"""

app = FastAPI(
    title="API Reto 01",
    description="API de interconexión de datos del Reto 01",
    version="1.0.0"
)


@app.get("/")
def root():
    """
    Endpoint principal de la API.
    Returns:
        dict: Mensaje indicando que la API del Reto 01 está funcionando.
    """
    return {"mensaje": "API R01 funcionando"}


@app.get("/estado")
def estado():
    """
    Comprueba el estado actual del backend.

    Este endpoint permite verificar que la API está operativa
    e identifica el reto al que pertenece.
    Returns:
        dict: Identificador del reto y estado del backend.
    """
    return {
        "reto": "R01",
        "estado": "operativo"
    }