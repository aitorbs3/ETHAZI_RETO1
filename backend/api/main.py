from fastapi import FastAPI

from api.health import router as health_router
from api.connectors import router as connectors_router
from api.students import router as students_router


# Creamos la aplicación principal de FastAPI.
#
# FastAPI se encargará de:
#   - Recibir las peticiones HTTP.
#   - Dirigir cada petición al endpoint correspondiente.
#   - Generar automáticamente la documentación de la API.
app = FastAPI(
    title="R01 - Sistema de Interconexión de Datos",
    description="API para la integración de bases de datos heterogéneas.",
    version="1.0.0"
)


# Registramos los diferentes routers de la aplicación.
#
# Cada router contiene un grupo de endpoints relacionado
# con una determinada funcionalidad.
#
# health_router:
#   Contiene los endpoints relacionados con el estado
#   y diagnóstico de la API.
#
# connectors_router:
#   Contiene los endpoints utilizados para consultar
#   los diferentes conectores de bases de datos.
#
# students_router:
#   Contiene los endpoints relacionados con los estudiantes
#   y sus operaciones CRUD.
app.include_router(health_router)
app.include_router(connectors_router)
app.include_router(students_router)