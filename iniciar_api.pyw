
import os
import sys
import traceback
from pathlib import Path

# Localizar automáticamente el proyecto
ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"

# Crear carpeta de registros
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

# Guardar los mensajes sin abrir una consola
registro = open(
    LOGS / "api.log",
    "a",
    encoding="utf-8",
    buffering=1
)

sys.stdout = registro
sys.stderr = registro

# Preparar directorio e importaciones
os.chdir(ROOT)
sys.path.insert(0, str(BACKEND))

try:
    import uvicorn

    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False
    )

except Exception:
    traceback.print_exc()

finally:
    registro.close()
