# Manual de instalación de la API ETHAZI — Windows

**Proyecto:** ETHAZI Reto 01 · Sistema de interconexión de datos de Hogwarths  
**Sistema:** Windows 10/11, 64 bits  
**Objetivo:** instalar FastAPI y hacer que se inicie sin escribir comandos cada vez que se abra JavaFX o Unity. Android se conectará por red al equipo Windows.

> **Alcance:** este manual instala **la API**. Las bases de datos MariaDB y Oracle, sus contenedores y los archivos de Derby, H2 y HSQLDB deben estar disponibles y configurados. La API no sustituye su instalación. Se utiliza la estructura de carpetas del repositorio `ETHAZI_RETO1`; comprueba los nombres concretos de los archivos en tu versión.

## 1. Requisitos previos

| Programa | Recomendación para este proyecto | Comprobar en PowerShell |
|---|---|---|
| Windows | 10/11 de 64 bits | `winver` |
| Python | 3.14.x (versión usada por el equipo; verificar compatibilidad de `requirements.txt`) | `python --version` |
| Java JDK | 21 LTS, necesario para los conectores JDBC/JPype | `java -version` |
| Git | Para descargar o actualizar el proyecto | `git --version` |
| Docker Desktop | Necesario si MariaDB y Oracle se ejecutan mediante contenedores | `docker version` |
| Docker Compose | Si se usa un archivo de composición | `docker compose version` |

Instala Python y Java con las opciones que permitan ejecutarlos desde la terminal. Inicia Docker Desktop antes de levantar los contenedores. Si no se usarán contenedores, configura las conexiones a instancias de bases de datos ya instaladas.

## 2. Obtener el proyecto

Descarga o clona el repositorio proporcionado por el equipo FILOS. Abre PowerShell en la carpeta raíz, **la que contiene `backend` y `data`**.

```powershell
cd "C:\ruta\ETHAZI_RETO1"
Get-ChildItem
```

Deberías encontrar `backend\api\main.py`. No ejecutes el comando de arranque desde dentro de `backend` cuando utilices los comandos de este manual.

## 3. Crear el entorno Python e instalar dependencias

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install --upgrade pip
```

En función de dónde esté el archivo real `requirements.txt`:

```powershell
if (Test-Path .\requirements.txt) {
    $req = ".\requirements.txt"
} elseif (Test-Path .\backend\requirements.txt) {
    $req = ".\backend\requirements.txt"
} else {
    throw "No se ha encontrado requirements.txt. Pídeselo al equipo FILOS."
}

.\.venv\Scripts\python.exe -m pip install -r $req
```

Si una dependencia da error, conserva el mensaje y revisa la compatibilidad de esa biblioteca con tu versión de Python; no cambies las versiones a ciegas.

## 4. Configurar las bases de datos y las credenciales

1. En la raíz del proyecto, copia la plantilla de configuración que acompañe al repositorio. Por ejemplo, si existe `.env.example`:

   ```powershell
   Copy-Item .env.example .env
   ```

2. Edita `.env` y configura las direcciones, puertos, usuarios, contraseñas y rutas según vuestra instalación. **Utiliza los nombres de variables definidos en el `.env.example` real**, no valores inventados. Entre los parámetros que utiliza el proyecto pueden estar `MARIADB_HOST`, `MARIADB_PORT`, `MARIADB_USER`, `MARIADB_PASSWORD`, `MARIADB_DATABASE`, `SQLITE_DATABASE`, `DERBY_DATABASE` y `H2_DATABASE`.
3. Comprueba que `JAVA_HOME` señala al JDK 21 cuando sea requerido por JPype/JDBC, y que están presentes los archivos `.jar` incluidos en la distribución.
4. No subas `.env` ni credenciales a GitHub. Incluye únicamente una plantilla sin contraseñas.

### Bases de datos

- **SQLite:** el backend debe llamar a `init_sqlite_db()` para crear las tablas `alumnos`, `cache_students` y `pending_operations` y asegurar las columnas `attempts` y `last_error`. La carpeta del fichero SQLite debe permitir escritura.
- **MariaDB:** el backend debe llamar a `init_mariadb_db()` para crear la tabla `alumnos` en una **base de datos MariaDB ya existente**. El usuario configurado necesita permisos para crear tablas al instalar.
- **Oracle, Derby, H2 y HSQLDB:** deben encontrarse las instancias/bases, rutas y drivers JDBC esperados por sus conectores. Las cuatro fuentes históricas se consultan en modo lectura.

Si MariaDB y Oracle se ejecutan con Docker Compose, abre la carpeta donde esté el `compose.yaml` o `docker-compose.yml` del proyecto y ejecuta:

```powershell
docker compose up -d
docker compose ps
```

**Importante:** el archivo Compose debe estar preparado con los servicios necesarios. Si `docker compose` no encuentra el archivo, localízalo y usa `docker compose -f "ruta\compose.yaml" up -d`. Para que los contenedores se reinicien automáticamente tras reiniciar Docker, establece `restart: unless-stopped` en sus servicios y configura Docker Desktop para iniciarse con Windows.

## 5. Probar la API manualmente (solo primera instalación)

Desde **la raíz del repositorio**:

```powershell
.\.venv\Scripts\python.exe -m uvicorn api.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

Abre:

- Swagger: <http://127.0.0.1:8000/docs>
- Lista de alumnos: <http://127.0.0.1:8000/students>

Swagger debe mostrar `GET /students`, `POST /students`, `PUT /students/{student_id}` y `DELETE /students/{student_id}`. El resultado de `/students` depende de las bases conectadas. Si alguna fuente falla, revisa el registro de la terminal. Detén esta instancia de prueba con **Ctrl+C** antes de configurar el arranque automático.

## 6. Preparar un lanzador sin ventana de PowerShell

Crea el archivo **`iniciar_api.pyw` en la raíz del proyecto** si todavía no existe, o revisa el ya utilizado por el equipo. Debe contener:

```python
import os
import sys
import traceback
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BACKEND = ROOT / "backend"
LOGS = ROOT / "logs"
LOGS.mkdir(exist_ok=True)

registro = open(LOGS / "api.log", "a", encoding="utf-8", buffering=1)
sys.stdout = registro
sys.stderr = registro
os.chdir(ROOT)
sys.path.insert(0, str(BACKEND))

try:
    import uvicorn
    uvicorn.run(
        "api.main:app",
        host="127.0.0.1",
        port=8000,
        reload=False,
    )
except Exception:
    traceback.print_exc()
finally:
    registro.close()
```

`127.0.0.1` permite conexiones **solo desde ese PC**. Para Android o dispositivos en la red local será necesaria la configuración del apartado 9.

Haz una prueba del lanzador:

```powershell
Start-Process -FilePath ".\.venv\Scripts\pythonw.exe" -ArgumentList "iniciar_api.pyw" -WorkingDirectory (Get-Location).Path
```

Comprueba Swagger. Si no abre, revisa `logs\api.log`. Asegúrate de que **no haya otra instancia ocupando el puerto 8000**. Detén el proceso de prueba antes de pasar al siguiente apartado.

## 7. Iniciar automáticamente al iniciar sesión en Windows

1. Pulsa **Win+R**, escribe `taskschd.msc` y acepta.
2. Pulsa **Crear tarea** (no «Crear tarea básica»).
3. Pestaña **General**: nombre `ETHAZI API`. Usa la cuenta que tiene permisos sobre los archivos del proyecto.
4. Pestaña **Desencadenadores**: nuevo desencadenador **Al iniciar sesión**.
5. Pestaña **Acciones** → **Iniciar un programa**:
   - **Programa:** `C:\ruta\ETHAZI_RETO1\.venv\Scripts\pythonw.exe`
   - **Argumentos:** `iniciar_api.pyw`
   - **Iniciar en:** `C:\ruta\ETHAZI_RETO1` (sin comillas en este campo)
6. Pestaña **Configuración**: selecciona **No iniciar una nueva instancia** cuando la tarea ya esté ejecutándose. Puedes activar el reinicio tras un fallo.
7. Guarda y usa **Ejecutar** sobre la tarea para probarla. Después inicia sesión de nuevo y comprueba <http://127.0.0.1:8000/docs>.

**Limitación:** «Al iniciar sesión» ejecuta la API cuando inicia sesión ese usuario. No es un servicio Windows permanente anterior al inicio de sesión. Para un servidor que atienda Android incluso sin sesiones abiertas, instalad un servicio Windows real y configurad las dependencias de Docker; no dejéis que cada cliente levante otra API distinta.

## 8. Cómo usarla desde JavaFX y Unity

En el mismo ordenador Windows, JavaFX y Unity pueden conectarse a:

```text
http://127.0.0.1:8000
```

Los dos programas comparten **la misma** API. Si abres JavaFX y Unity simultáneamente no debes arrancar dos servidores distintos.

## 9. Acceso desde Android o desde otro ordenador

1. En el lanzador modifica `host="127.0.0.1"` por `host="0.0.0.0"` y reinicia **la tarea** o el proceso; esto solo tiene sentido para redes privadas controladas.
2. Obtén la dirección IPv4 del PC servidor con `ipconfig`.
3. Configura Android o el cliente remoto para acceder a `http://IP_DEL_PC:8000` (la IP será distinta en cada instalación).
4. Permite el puerto 8000 en el firewall **solo desde la red privada o desde los dispositivos autorizados**.
5. Comprueba que el equipo servidor sigue encendido y que el móvil está en una red que puede alcanzarlo.

**Seguridad:** no publiques esta API directamente en Internet ni abras `8000` a cualquiera. Antes de permitir accesos externos y operaciones de alta/modificación/borrado, añade autenticación, control de acceso y HTTPS (por ejemplo, mediante un proxy inverso).

## 10. Diagnóstico y mantenimiento

| Problema | Qué comprobar |
|---|---|
| `/docs` no abre | `logs\api.log`, Programador de tareas, Python instalado, puerto 8000 ocupado |
| `/students` devuelve 404 | Comprueba que `backend/api/main.py` registra `students_router` con `app.include_router(...)` |
| Error de SQLite (`attempts`, `last_error`) | Comprobar que `init_sqlite_db()` contiene las columnas y migración de instalaciones antiguas |
| MariaDB no sincroniza | Que Docker esté activo, que la base exista, credenciales y cola `pending_operations` |
| Error JDBC/JPype | Java 21, `JAVA_HOME`, archivos `.jar` y rutas de bases |
| Android no conecta | Dirección IP real (nunca `127.0.0.1` del móvil), firewall, red y enlace `0.0.0.0` |

Tras instalar actualizaciones:

```powershell
.\.venv\Scripts\python.exe -m pip install -r $req
```

Ejecuta el comando anterior solo después de volver a definir `$req` según el apartado 3. Reinicia la tarea/proceso después de actualizar. **Haz copias de seguridad de SQLite y MariaDB** antes de cambios importantes.

---

**Resultado esperado:** Windows inicia automáticamente una instancia de FastAPI cuando el usuario inicia sesión. JavaFX y Unity funcionan sin escribir comandos; Android accede a ese equipo cuando la configuración de red y seguridad está terminada.
