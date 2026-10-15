# Manual de instalación de la API ETHAZI — Ubuntu

**Proyecto:** ETHAZI Reto 01 · Sistema de interconexión de datos de Hogwarths  
**Sistema:** Ubuntu de 64 bits  
**Objetivo:** instalar la API en Ubuntu y configurarla como servicio `systemd`, de forma **independiente de Windows**. JavaFX en Ubuntu podrá conectarse a la API local; Android podrá hacerlo por red si se habilita y protege ese acceso.

> **Alcance:** este manual configura **la API**. Las bases MariaDB/Oracle, los drivers JDBC y los archivos de Derby/H2/HSQLDB deberán configurarse por separado. No se asume que el repositorio contenga un `compose.yaml` en su raíz.

## 1. Requisitos previos

- Ubuntu 64 bits con usuario autorizado para instalar software y crear un servicio.
- Python compatible con las dependencias de vuestro `requirements.txt` (**el proyecto se ha trabajado con Python 3.14.x**; verifica esa compatibilidad en Ubuntu antes de desplegar).
- Java **JDK 21 LTS** para JPype/JDBC.
- Git para descargar el código.
- Docker Engine y complemento Docker Compose, **si MariaDB y Oracle funcionan en contenedores**.

Instala los paquetes básicos:

```bash
sudo apt update
sudo apt install -y git python3 python3-venv python3-pip openjdk-21-jdk
python3 --version
java -version
```

Si Ubuntu no ofrece Java 21 o Python con la versión requerida, instálalos desde un proveedor compatible con vuestra distribución. **No presupongas que `python3` es Python 3.14**: revisa la versión y las dependencias de `requirements.txt`.

Comprueba Docker, si procede:

```bash
docker --version
docker compose version
```

Si no está instalado, sigue el procedimiento oficial de Docker para tu versión de Ubuntu e instala Docker Engine y el complemento Compose. Comprueba que el daemon funciona antes de continuar.

## 2. Copiar el repositorio

Clona o copia el repositorio proporcionado por Equipo FILOS. Estos ejemplos usan `/opt/ethazi/ETHAZI_RETO1`; puedes utilizar otra carpeta, pero **sustituye la ruta en todos los comandos y en el servicio**.

```bash
sudo mkdir -p /opt/ethazi
sudo chown "$USER":"$USER" /opt/ethazi
cd /opt/ethazi
# Sustituir por la URL del repositorio que os facilite el equipo:
# git clone <URL_DEL_REPOSITORIO> ETHAZI_RETO1
cd ETHAZI_RETO1
ls
```

La última orden requiere que el proyecto ya esté copiado. Verifica que existe `backend/api/main.py`.

## 3. Instalar dependencias en entorno virtual

Usa la versión de Python compatible instalada en ese equipo. Si el comando `python3` corresponde a dicha versión:

```bash
python3 -m venv .venv
.venv/bin/python -m pip install --upgrade pip
```

Localiza y usa el fichero `requirements.txt` real:

```bash
if [ -f requirements.txt ]; then
    REQ=requirements.txt
elif [ -f backend/requirements.txt ]; then
    REQ=backend/requirements.txt
else
    echo "No se ha encontrado requirements.txt. Detén la instalación." >&2
    REQ=""
fi

if [ -n "$REQ" ]; then
    .venv/bin/python -m pip install -r "$REQ"
fi
```

Si estás siguiendo las instrucciones en una terminal interactiva y no existe el archivo, detén la instalación y solicita el `requirements.txt` al equipo FILOS. No inventes paquetes o versiones.

## 4. Variables de entorno y acceso a las bases de datos

1. En la raíz del proyecto, copia `.env.example` a `.env` si se suministra:

   ```bash
   cp .env.example .env
   ```

2. Edita `.env` y configura **los nombres y valores que figuren en vuestra plantilla real**: conexión MariaDB, Oracle, rutas de Derby, H2, HSQLDB y SQLite. No publiques el archivo.
3. Comprueba la localización del JDK:

   ```bash
   readlink -f "$(command -v java)"
   ```

4. Si JPype necesita `JAVA_HOME`, define la ruta al JDK 21 en el servicio `systemd` (apartado 6). En Ubuntu suele tener una ruta parecida a `/usr/lib/jvm/java-21-openjdk-amd64`, **compruébala antes de usarla**.
5. Asegúrate de que el usuario que ejecutará la API pueda leer los drivers `.jar` y escribir en la carpeta SQLite y en los registros.

### Dependencias de base de datos

- **SQLite:** `init_sqlite_db()` debe crear `alumnos`, `cache_students`, `pending_operations` y las columnas `attempts`, `last_error` que faltaban en las instalaciones antiguas.
- **MariaDB:** la base de datos debe existir y estar accesible; `init_mariadb_db()` crea `alumnos` si no existe y el usuario tiene permisos.
- **Derby, H2, HSQLDB y Oracle:** configura rutas, drivers y datos de conexión. Estas fuentes son históricas y de lectura.

Si dispones de un archivo Compose con MariaDB y Oracle, desde la carpeta que lo contiene:

```bash
docker compose up -d
docker compose ps
```

Para que Docker y los contenedores se recuperen tras reiniciar, habilita el servicio Docker y configura en el Compose de cada contenedor `restart: unless-stopped`:

```bash
sudo systemctl enable --now docker
```

*Nota:* el arranque del servicio API no garantiza que MariaDB u Oracle hayan terminado de inicializarse; comprueba su estado antes de la primera prueba de sincronización.

## 5. Primera prueba manual

Desde la raíz del repositorio:

```bash
.venv/bin/python -m uvicorn api.main:app --app-dir backend --host 127.0.0.1 --port 8000
```

En el navegador local abre:

- Swagger: <http://127.0.0.1:8000/docs>
- Alumnos: <http://127.0.0.1:8000/students>

Verifica que `/docs` incluye `GET`, `POST`, `PUT` y `DELETE` sobre estudiantes. Si algún conector da error, revisa el mensaje en terminal. **Detén Uvicorn con Ctrl+C** antes de instalar el servicio, para que no queden dos procesos en el puerto 8000.

## 6. Arranque automático mediante `systemd`

### 6.1. Anotar usuario y ruta real

```bash
whoami
pwd
```

En el ejemplo siguiente se emplea:

- Usuario de Linux: `usuario_ethazi` (sustituir por el valor de `whoami`).
- Carpeta del proyecto: `/opt/ethazi/ETHAZI_RETO1` (sustituir si es distinta).
- Entorno virtual: `/opt/ethazi/ETHAZI_RETO1/.venv`.

### 6.2. Crear el servicio

```bash
sudo nano /etc/systemd/system/ethazi-api.service
```

Pega este contenido y **sustituye `usuario_ethazi` y las rutas indicadas**:

```ini
[Unit]
Description=ETHAZI FastAPI
Wants=network-online.target
After=network-online.target

[Service]
Type=simple
User=usuario_ethazi
WorkingDirectory=/opt/ethazi/ETHAZI_RETO1
Environment=PYTHONUNBUFFERED=1
# Descomenta SOLO si corresponde al JDK 21 real de este equipo:
# Environment=JAVA_HOME=/usr/lib/jvm/java-21-openjdk-amd64
ExecStart=/opt/ethazi/ETHAZI_RETO1/.venv/bin/python -m uvicorn api.main:app --app-dir backend --host 127.0.0.1 --port 8000
Restart=on-failure
RestartSec=5

[Install]
WantedBy=multi-user.target
```

`127.0.0.1` permite que JavaFX funcione en este mismo Ubuntu. Para Android u otro equipo, consulta el apartado 8.

### 6.3. Activar y comprobar

```bash
sudo systemctl daemon-reload
sudo systemctl enable --now ethazi-api.service
sudo systemctl status ethazi-api.service
```

Ver el registro:

```bash
sudo journalctl -u ethazi-api.service -n 80 --no-pager
```

Volver a arrancar el servicio tras un cambio:

```bash
sudo systemctl restart ethazi-api.service
```

Para comprobarlo después de reiniciar Ubuntu:

```bash
sudo reboot
```

Cuando vuelva a arrancar:

```bash
systemctl is-active ethazi-api.service
curl http://127.0.0.1:8000/openapi.json
```

`is-active` debería mostrar `active`. El resultado de `curl` será el esquema OpenAPI en JSON.

## 7. Uso desde JavaFX en Ubuntu

Si JavaFX y FastAPI están instalados **en el mismo equipo Ubuntu**, JavaFX se conectará a:

```text
http://127.0.0.1:8000
```

La API funcionará **sin necesitar un equipo Windows encendido**. Se inicia automáticamente como servicio del propio Ubuntu.

## 8. Acceso desde Android o desde otros dispositivos

1. Modifica el servicio `ethazi-api.service`: en `ExecStart`, sustituye `--host 127.0.0.1` por `--host 0.0.0.0`.
2. Reinicia el servicio:

   ```bash
   sudo systemctl daemon-reload
   sudo systemctl restart ethazi-api.service
   ```

3. Averigua la IP del equipo Ubuntu:

   ```bash
   hostname -I
   ```

4. Configura Android para usar `http://IP_DE_UBUNTU:8000`.
5. Si se utiliza UFW, permite solo las IP o la subred **de confianza**. Ejemplo de sintaxis (sustituye `192.168.1.0/24` por la red real):

   ```bash
   sudo ufw allow from 192.168.1.0/24 to any port 8000 proto tcp
   ```

**Seguridad:** no publiques el puerto 8000 directamente en Internet ni habilites escritura anónima. Para uso fuera de una red local controlada, implanta autenticación y HTTPS mediante un proxy inverso.

## 9. Diagnóstico

| Problema | Comprobación |
|---|---|
| El servicio no arranca | `sudo journalctl -u ethazi-api.service -n 80 --no-pager` |
| `ModuleNotFoundError` | Revisar `WorkingDirectory`, `--app-dir backend` y `.venv` |
| Error de Java/JPype | `java -version`, `JAVA_HOME`, archivos `.jar` y permisos |
| SQLite no puede escribir | Permisos del usuario de `systemd` sobre `data/` y la ruta de SQLite |
| MariaDB/Oracle no disponibles | `docker compose ps`, host/puerto, credenciales y estado de contenedores |
| `/students` devuelve 404 | Revisar `app.include_router(students_router)` en `backend/api/main.py` |
| Android no puede conectar | IP real, firewall, misma red y `--host 0.0.0.0` |

Después de instalar nuevas dependencias, **reinicia el servicio**. Haz copias de seguridad de SQLite/MariaDB antes de actualizaciones que cambien los esquemas de datos.

---

**Resultado esperado:** Ubuntu arranca automáticamente FastAPI como servicio `systemd`; JavaFX local funciona sin Windows; Android puede acceder mientras Ubuntu permanezca encendido y se haya habilitado una conexión de red segura.
