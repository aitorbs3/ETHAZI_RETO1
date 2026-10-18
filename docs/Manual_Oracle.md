# Manual de Instalación, Configuración y Uso de Oracle Database (Docker)

---

## 1. Objetivo

Este documento detalla el procedimiento completo para instalar, levantar, configurar y comprobar la base de datos **Oracle** utilizada como fuente histórica de lectura (casa _Ravenclaw_) en el proyecto **ETHAZI_RETO1**.

Gracias al uso de **Docker**, no es necesario realizar una instalación pesada de Oracle Database directamente en el sistema operativo del equipo. El backend se comunica con este motor a través de la librería oficial de Python **`oracledb`** (`backend/connectors/oracle_connector.py`).

---

## 2. Requisitos Previos

| Componente                   | Propósito Técnico                                                       |
| ---------------------------- | ----------------------------------------------------------------------- |
| **Docker Desktop**           | Ejecutar la imagen oficial de Oracle Database en un contenedor aislado. |
| **Python (Entorno Virtual)** | Ejecutar la lógica de negocio y los conectores del backend.             |
| **`oracledb`**               | Driver de conexión optimizado para enlazar Python con Oracle.           |
| **Archivo `.env**`           | Centralizar credenciales y parámetros de conexión de forma segura.      |

> 💡 **Nota:** Para este conector **no** se requiere instalar manualmente Oracle Instant Client ni dependencias binarias adicionales en la máquina local.

---

## 3. Instalación y Verificación de Docker Desktop

1. Asegúrate de tener instalado **Docker Desktop** en tu equipo.
2. Abre la aplicación y espera a que el icono de la barra de estado indique que el motor está totalmente iniciado.
3. Abre una terminal de **PowerShell** y verifica que las herramientas CLI estén operativas ejecutando:

```powershell
docker --version
docker compose version
docker info

```

_Si aparece el error `failed to connect to the docker API`, asegúrate de que Docker Desktop siga abierto y en ejecución._

---

## 4. Configuración de Oracle en el Entorno Docker (`docker-compose.yml`)

En la raíz del proyecto se encuentra el archivo `docker-compose.yml`, donde se define el servicio de Oracle utilizando la imagen oficial de Oracle Free:

```yaml
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
```

- **Puerto `1521`:** Es el puerto estándar de escucha de Oracle, utilizado por el backend de Python para establecer la conexión JDBC/nativa.

---

## 5. Persistencia de los Datos (`Volumes`)

Los datos almacenados en Oracle (tablas, registros de alumnos, esquemas) no se pierden al apagar el contenedor gracias al volumen gestionado de Docker llamado **`oracle_data`**.

- **Detener contenedores sin perder datos:**

```powershell
docker compose down

```

- **Volver a iniciar el servicio conservando la información:**

```powershell
docker compose up -d oracle

```

- ⚠️ **Precaución:** **Nunca** ejecutes `docker compose down -v` si deseas conservar los datos almacenados, ya que el modificador `-v` destruye también los volúmenes persistentes de Docker.

---

## 6. Configuración de Variables de Entorno (`.env`)

El archivo `.env` en la raíz del proyecto almacena la configuración y credenciales confidenciales de acceso.

### Plantilla de referencia (`.env.example`)

El repositorio incluye una plantilla para nuevas instalaciones:

```env
# Configuración de Oracle Database
ORACLE_ADMIN_PASSWORD=TuPasswordAdminSegura
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE_NAME=FREEPDB1
ORACLE_USER=sys
ORACLE_PASSWORD=TuPasswordAdminSegura

```

Para configurarlo en tu entorno local:

```powershell
Copy-Item .env.example .env

```

_(Abre el archivo `.env` generado y completa los valores con tus credenciales personales)._

> 🔒 **Seguridad:** El archivo `.env` contiene credenciales sensibles y está incluido en el archivo `.gitignore` para evitar que se suba accidentalmente a repositorios públicos de Git.

---

## 7. Instalación de Dependencias de Python

1. Activa el entorno virtual del proyecto en PowerShell:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

```

2. Instala o actualiza las dependencias del backend:

```powershell
python -m pip install -r backend\requirements.txt

```

3. Verifica que la librería de Oracle esté correctamente instalada:

```powershell
python -m pip show oracledb

```

_La versión debe coincidir exactamente con la requerida por el proyecto (`oracledb==26.0.1`), apuntando al directorio del entorno virtual (`...\ETHAZI_RETO1\.venv\Lib\site-packages`)._

---

## 8. Puesta en Marcha del Contenedor

Desde la raíz del proyecto, ejecuta el comando de Docker Compose para levantar el servicio en segundo plano:

```powershell
docker compose up -d oracle

```

> ⏳ **¡Atención (Tiempo de Inicialización):** La **primera vez** que se levanta la imagen de Oracle Free, el contenedor realiza un proceso interno de instalación y configuración de la base de datos que puede tardar entre **5 y 10 minutos**. Durante este tiempo, los intentos de conexión fallarán temporalmente.

Puedes supervisar el progreso de arranque consultando los registros en tiempo real:

```powershell
docker logs -f reto01-oracle

```

Debes esperar hasta ver el mensaje clave que confirma que el sistema está listo:

```text
DATABASE IS READY TO USE!

```

---

## 9. Arquitectura del Conector Python

El flujo mediante el cual el backend establece comunicación con Oracle sigue una arquitectura desacoplada:

```text
.env (Credenciales)
  │
  ▼
backend/utils/config.py (Carga segura)
  │
  ▼
backend/connectors/oracle_connector.py (Lógica de conexión)
  │
  ▼
Librería python-oracledb
  │
  ▼
localhost:1521 (Pluggable Database: FREEPDB1)

```

---

## 10. Comprobación y Test de Conexión

El proyecto incluye un script dedicado a verificar la conectividad con la base de datos Oracle (`backend/tests/test_oracle.py`).

Para ejecutar la prueba de diagnóstico:

```powershell
python -m backend.tests.test_oracle

```

Si la conexión es exitosa, la consola devolverá:

```text
(1,)

```

Este resultado confirma que el circuito completo (`Python` ➔ `oracle_connector` ➔ `python-oracledb` ➔ `Oracle Database`) responde correctamente a la consulta de prueba `SELECT 1 FROM DUAL`.

---

## 11. Gestión y Comandos Principales

| Acción                     | Comando PowerShell                    |
| -------------------------- | ------------------------------------- |
| **Arrancar Oracle**        | `docker compose up -d oracle`         |
| **Comprobar estado**       | `docker compose ps`                   |
| **Ver registros (Logs)**   | `docker logs reto01-oracle`           |
| **Probar conexión Python** | `python -m backend.tests.test_oracle` |
| **Reiniciar servicio**     | `docker compose restart oracle`       |
| **Detener contenedor**     | `docker compose down`                 |

---

## 12. Resolución de Problemas Frecuentes (Troubleshooting)

- **Error: `failed to connect to the docker API**`
- _Causa:_ Docker Desktop está cerrado o el servicio de Windows no ha arrancado.
- _Solución:_ Abre la aplicación Docker Desktop, espera a que aparezca el icono verde y ejecuta `docker info`.

- **Error: `ModuleNotFoundError: No module named 'oracledb'**`
- _Causa:_ El entorno virtual de Python no está activado o falta instalar los requerimientos.
- _Solución:_ Activa tu `.venv` y ejecuta `python -m pip install -r backend\requirements.txt`.

- **Error de conexión denegada o tiempo de espera agotado (`ORA-12514` / Conexión rechazada)**
- _Causa:_ Estás intentando conectarte antes de que Oracle termine de inicializarse por primera vez.
- _Solución:_ Revisa los logs con `docker logs reto01-oracle` y espera pacientemente a que aparezca el mensaje `DATABASE IS READY TO USE!`.
