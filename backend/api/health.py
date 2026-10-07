from fastapi import APIRouter


# Creamos un router para agrupar los endpoints relacionados
# con el estado y diagnóstico de la API.
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

    # Devolvemos una respuesta sencilla para indicar que
    # el backend está operativo.
    #
    # FastAPI convierte automáticamente este diccionario
    # en una respuesta JSON.
    return {
        "reto": "R01",
        "status": "ok"
    }