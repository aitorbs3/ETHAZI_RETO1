from fastapi import FastAPI

from api.health import router as health_router
from api.connectors import router as connectors_router
from api.students import router as students_router

from connectors.sqlite_connector import init_sqlite_db
from connectors.mariadb_connector import init_mariadb_db
from services.sync_service import SyncService
from services.bootstrap_service import inicializar_bases_historicas

app = FastAPI(
    title="R01 - Sistema de Interconexión de Datos",
    description="API para la integración de bases de datos heterogéneas.",
    version="1.0.0"
)

app.include_router(health_router)
app.include_router(connectors_router)
app.include_router(students_router)

@app.on_event("startup")
def startup_event():
    """
    Inicializa las bases de datos automáticamente
    cuando arranca FastAPI.
    """

    # SQLite siempre debe estar disponible
    init_sqlite_db()

    # Importa las cuatro casas solo si sus tablas están vacías o no existen.
    # Cada base se inicializa independientemente; los errores quedan en logs.
    inicializar_bases_historicas()

    # MariaDB puede estar temporalmente desconectada
    try:
        init_mariadb_db()

        resultado = SyncService().sincronizar_pendientes()

        print("Sincronización inicial:", resultado)

    except Exception as error:
        print(
            "MariaDB no disponible. "
            "Las operaciones seguirán pendientes:",
            error
        )
