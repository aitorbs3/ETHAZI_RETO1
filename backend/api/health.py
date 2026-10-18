"""Endpoint de diagnóstico para comprobar la disponibilidad de la API."""

# Importamos APIRouter desde FastAPI para estructurar y agrupar las rutas 
# del backend de manera modular e independiente.
from fastapi import APIRouter


# Creamos una instancia de APIRouter para agrupar todos los endpoints relacionados
# con el estado, salud y diagnóstico de la API (también conocido como Health Check).
router = APIRouter()


@router.get("/health")
def health():
    """
    Comprueba si la API está funcionando correctamente.

    Returns:
        dict: Información sobre el estado del backend.
              Incluye el identificador del reto y el estado
              actual de la API.
    """

    # La respuesta es un diccionario JSON deliberadamente ligero y rápido.
    # No realiza consultas a bases de datos (ni SQLite ni MariaDB ni históricas) 
    # para que los sistemas de monitorización, Docker healthchecks o balanceadores 
    # de carga puedan comprobar la disponibilidad del proceso de forma instantánea.
    return {
        "reto": "R01",
        "status": "ok"
    }