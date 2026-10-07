Manual de instalación y configuración de Oracle
1. Objetivo
Este documento explica cómo instalar, levantar y comprobar la base de datos Oracle utilizada por el backend del proyecto Reto 01.
Oracle se ejecuta mediante Docker, por lo que no es necesario instalar Oracle Database manualmente en el equipo.
El backend se conecta a Oracle mediante la librería Python:
oracledb==26.0.1

La conexión se realiza desde:
backend/connectors/oracle_connector.py

2. Requisitos
Para utilizar Oracle se necesita:
Componente	Uso
Docker Desktop	Ejecutar Oracle Database
Python	Ejecutar el backend
oracledb	Conectar Python con Oracle
.env	Configurar conexión y credenciales


Para este conector no es necesario instalar Oracle Database ni Oracle Instant Client manualmente.
3. Instalar Docker Desktop
Instalar Docker Desktop en el equipo.
Después de instalarlo, abrir Docker Desktop y esperar hasta que el motor de Docker esté iniciado.
Comprobar desde PowerShell:
docker --version

y:
docker compose version

También se puede comprobar que el motor está funcionando mediante:
docker info

Si aparece un error parecido a:
failed to connect to the docker API

se debe comprobar que Docker Desktop está abierto y en ejecución.
4. Configuración de Oracle con Docker
En la raíz del proyecto existe:
docker-compose.yml

Oracle se define como un servicio dentro de este archivo.
Una configuración básica es:
services:
  oracle:
    image: container-registry.oracle.com/database/free:latest-lite
    container_name: reto01-oracle

    ports:
      - "1521:1521"

    environment:
      ORACLE_PWD: ${ORACLE_ADMIN_PASSWORD}

    volumes:
      - oracle_data:/opt/oracle/oradata

    restart: unless-stopped

volumes:
  oracle_data:

El puerto:
1521

es utilizado por el backend para conectarse a Oracle.
5. Persistencia de los datos
Oracle utiliza un volumen de Docker llamado:
oracle_data

Este volumen almacena físicamente los datos de la base Oracle.
Por tanto, los alumnos y las demás tablas creadas en Oracle no desaparecen al detener el contenedor.
Se puede detener Oracle mediante:
docker compose down

y volver a iniciarlo posteriormente:
docker compose up -d oracle

Los datos seguirán existiendo.
No se debe utilizar:
docker compose down -v

si se desean conservar los datos, ya que -v elimina también el volumen.
6. Configuración del archivo .env
En la raíz del proyecto debe existir:
.env

Este archivo contiene la configuración específica de cada instalación.
Para Oracle se utilizan las siguientes variables:
ORACLE_ADMIN_PASSWORD=
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=FREEPDB1
ORACLE_USER=
ORACLE_PASSWORD=

Por ejemplo, en un entorno de desarrollo:
ORACLE_ADMIN_PASSWORD=contraseña_administrador
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=FREEPDB1
ORACLE_USER=usuario_oracle
ORACLE_PASSWORD=contraseña_usuario

Las contraseñas reales no deben almacenarse en Git.
El archivo:
.env

debe estar incluido en .gitignore.
7. Archivo .env.example
El repositorio incluye:
.env.example

Este archivo sirve como plantilla para nuevas instalaciones y puede contener:
# ORACLE

ORACLE_ADMIN_PASSWORD=
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=FREEPDB1
ORACLE_USER=
ORACLE_PASSWORD=

El cliente deberá copiarlo:
Copy-Item .env.example .env

y completar sus valores.
8. Instalar la dependencia Python
Activar primero el entorno virtual:
.\.venv\Scripts\Activate.ps1

Si PowerShell bloquea la ejecución:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

y posteriormente:
.\.venv\Scripts\Activate.ps1

Instalar las dependencias del backend:
python -m pip install -r backend\requirements.txt

El archivo:
backend/requirements.txt

debe incluir:
oracledb==26.0.1

Se puede comprobar la instalación con:
python -m pip show oracledb

Debe aparecer:
Name: oracledb
Version: 26.0.1

y la ubicación debe pertenecer al entorno virtual:
...\ETHAZI_RETO1\.venv\Lib\site-packages

9. Levantar Oracle
Desde la raíz del proyecto:
docker compose up -d oracle

La primera ejecución puede tardar más tiempo debido a que Docker debe descargar e inicializar Oracle.
Comprobar el estado mediante:
docker compose ps

También pueden consultarse los logs:
docker logs reto01-oracle

Si se desean visualizar continuamente:
docker logs -f reto01-oracle

10. Conector Python
La conexión con Oracle se realiza desde:
backend/connectors/oracle_connector.py

El conector obtiene los datos de configuración mediante:
backend/utils/config.py

El flujo de conexión es:
.env
 │
 ▼
config.py
 │
 ▼
oracle_connector.py
 │
 ▼
python-oracledb
 │
 ▼
localhost:1521
 │
 ▼
Oracle Docker
 │
 ▼
FREEPDB1

El código no contiene usuarios, contraseñas ni direcciones específicas del equipo.
11. Comprobar la conexión
El proyecto incluye:
backend/tests/test_oracle.py

La prueba realiza una consulta básica:
SELECT 1 FROM DUAL

Para ejecutarla:
python -m backend.tests.test_oracle

Si la conexión funciona correctamente aparecerá:
(1,)

Este resultado confirma que:
Python
   ↓
oracle_connector.py
   ↓
python-oracledb
   ↓
Oracle Database

funciona correctamente.
12. Detener Oracle
Para detener Oracle:
docker compose down

Los datos seguirán almacenados en el volumen:
oracle_data

Para volver a arrancarlo:
docker compose up -d oracle

13. Reiniciar Oracle
Si únicamente se desea reiniciar el servicio:
docker compose restart oracle

También puede detenerse:
docker compose stop oracle

y volver a iniciarse:
docker compose start oracle

14. Comandos principales
# Levantar Oracle
docker compose up -d oracle

# Comprobar estado
docker compose ps

# Ver logs
docker logs reto01-oracle

# Probar conexión desde Python
python -m backend.tests.test_oracle

# Detener Oracle
docker compose down

# Reiniciar Oracle
docker compose restart oracle

15. Problemas frecuentes
Docker no está iniciado
Error:
failed to connect to the docker API

Solución: abrir Docker Desktop, esperar a que esté completamente iniciado y ejecutar:
docker info

No se encuentra oracledb
Error:
ModuleNotFoundError: No module named 'oracledb'

Activar .venv:
.\.venv\Scripts\Activate.ps1

e instalar:
python -m pip install -r backend\requirements.txt

No conecta con Oracle
Comprobar primero:
docker compose ps

Después revisar en .env:
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=FREEPDB1
ORACLE_USER=
ORACLE_PASSWORD=

Finalmente volver a ejecutar:
python -m backend.tests.test_oracle

16. Resumen para una instalación nueva
Una vez obtenido el proyecto:
cd ETHAZI_RETO1

Activar o crear el entorno Python e instalar dependencias:
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt

Crear la configuración:
Copy-Item .env.example .env

Completar las variables de Oracle en .env.
Abrir Docker Desktop y ejecutar:
docker compose up -d oracle

Finalmente comprobar la conexión:
python -m backend.tests.test_oracle

Resultado esperado:
(1,)