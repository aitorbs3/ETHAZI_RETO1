
"""Inicia la API local en Windows y redirige su salida a un archivo de log."""

import os
import sys
import traceback
from pathlib import Path

# Las rutas parten de este lanzador para no depender del directorio actual
# desde el que Windows abra el acceso directo.
ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"

# Crear carpeta de registros
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

# El buffer por línea mantiene el registro actualizado mientras Uvicorn corre
# en segundo plano y el archivo se abre sin mostrar una ventana de consola.
registro = open(
    LOGS / "api.log",
    "a",
    encoding="utf-8",
    buffering=1
)

sys.stdout = registro
sys.stderr = registro

# Uvicorn importa api.main desde backend; se prepara la ruta antes del arranque.
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
    # Guardar el traceback completo para diagnosticar fallos de inicio.
    traceback.print_exc()

finally:
    registro.close()
