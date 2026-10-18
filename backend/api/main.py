"""Configura la aplicación FastAPI y sus tareas de inicialización."""

# Importamos la clase principal FastAPI para instanciar y configurar el servidor web del backend.
from fastapi import FastAPI

# Importamos los diferentes enrutadores (routers) modulares de la API según su dominio de negocio.
from api.health import router as health_router
from api.connectors import router as connectors_router
from api.students import router as students_router

# Importamos las funciones de inicialización para las bases de datos SQLite local y MariaDB central.
from connectors.sqlite_connector import init_sqlite_db
from connectors.mariadb_connector import init_mariadb_db

# Importamos los servicios de negocio encargados de la sincronización de transacciones y el bootstrap histórico.
from services.sync_service import SyncService
from services.bootstrap_service import inicializar_bases_historicas

# Instanciamos la aplicación FastAPI configurando sus metadatos principales para la documentación automática (Swagger/OpenAPI).
app = FastAPI(
    title="R01 - Sistema de Interconexión de Datos",
    description="API para la integración de bases de datos heterogéneas.",
    version="1.0.0"
)

# Asociamos cada router modular a la aplicación principal para mantener las rutas agrupadas por responsabilidad.
app.include_router(health_router)
app.include_router(connectors_router)
app.include_router(students_router)


@app.on_event("startup")
def startup_event():
    """Prepara SQLite y las fuentes históricas e intenta sincronizar MariaDB."""

    # 1. Inicializamos SQLite local. Actúa como la red de seguridad del sistema:
    # la API puede arrancar y seguir aceptando operaciones locales aunque MariaDB esté temporalmente caída.
    init_sqlite_db()

    # 2. Inicializamos las fuentes históricas (Derby, H2, HSQLDB, Oracle).
    # Importa los datos de las cuatro casas solo si las tablas están vacías o no existen previamente.
    # Cada base se inicializa de forma independiente para evitar fallos en cascada.
    inicializar_bases_historicas()

    # 3. Intentamos conectar con MariaDB y procesar la cola de operaciones pendientes.
    # La cola local de SQLite garantiza la persistencia si MariaDB no está disponible,
    # permitiendo reintentar las transacciones de manera transparente en un arranque posterior.
    try:
        init_mariadb_db()

        resultado = SyncService().sincronizar_pendientes()

        print("Sincronización inicial completada con éxito:", resultado)

    except Exception as error:
        # Tolerancia a fallos: si MariaDB no está accesible, la API no se cae en el arranque.
        # Las escrituras o cambios offline quedan retenidos en la cola local a la espera de conectividad.
        print(
            "MariaDB no disponible temporalmente. "
            "Las operaciones de escritura seguirán pendientes en la cola local:",
            error
        )