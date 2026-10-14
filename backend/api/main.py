from fastapi import FastAPI
from api.health import router as health_router
from api.connectors import router as connectors_router
from api.students import router as students_router
from connectors.sqlite_connector import init_sqlite_db

app = FastAPI(
    title="R01 - Sistema de Interconexión de Datos",
    description="API para la integración de bases de datos heterogéneas.",
    version="1.0.0"
)

@app.on_event("startup")
def startup_event():
    """Se ejecuta automáticamente al iniciar FastAPI."""
    init_sqlite_db()

app.include_router(health_router)
app.include_router(connectors_router)
app.include_router(students_router)