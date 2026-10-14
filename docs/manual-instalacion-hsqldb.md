Crear el entorno virtual:
python -m venv .venv

Desbloquear la ejecución de scripts en la sesión actual de PowerShell:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Activar el entorno virtual:
.\.venv\Scripts\Activate.ps1

Instalar las Dependencias
Con el entorno virtual activado, instalar las dependencias del proyecto:
python -m pip install -r backend\requirements.txt

Configurar HSQLDB
El proyecto incluye el driver JDBC necesario para utilizar HSQLDB.
Comprobar que el driver se encuentra en el proyecto:
dir backend\drivers\hsqldb

Debe aparecer:
hsqldb.jar

Crear la carpeta local para la base de datos de prueba:
New-Item -ItemType Directory -Path .\prueba_hsqldb -Force

Configurar el Archivo .env
Crear el archivo .env a partir de la plantilla:
Copy-Item .env.example .env

Abrir el archivo .env y configurar la variable HSQLDB_DATABASE con la ruta de la carpeta prueba_hsqldb:
HSQLDB_DATABASE=C:\Ruta\De\Tu\Equipo\ETHAZI_RETO1\prueba_hsqldb

La ruta debe adaptarse a la ubicación donde se haya clonado el proyecto.
Verificar la Conexión con HSQLDB
Con el entorno virtual activado y situado en la raíz del proyecto, ejecutar:
python -m backend.tests.test_hsqldb