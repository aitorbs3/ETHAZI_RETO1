# Manual de Instalación, Configuración y Verificación del Conector HSQLDB — ETHAZI_RETO1 (DAM 2º)

---

## 1. Objetivo del Módulo

Este documento detalla de forma estructurada el procedimiento técnico para desplegar, configurar y verificar la base de datos relacional **HSQLDB**, la cual simula una de las fuentes históricas de solo lectura (correspondiente a la casa _Slytherin_) dentro del proyecto **ETHAZI_RETO1** de **2º de Desarrollo de Aplicaciones Multiplataforma (DAM)**. Al igual que con otros motores del sistema, los drivers necesarios se distribuyen embebidos en el repositorio para garantizar la reproducibilidad.

---

## 2. Preparación del Entorno y Dependencias

Antes de configurar el motor HSQLDB, es necesario preparar el entorno de ejecución de Python en el equipo:

- **Crear el entorno virtual:** Ejecuta el siguiente comando en la raíz del proyecto para aislar las librerías:

```powershell
python -m venv .venv

```

- **Desbloquear la ejecución de scripts en PowerShell:** Si tu directiva de seguridad bloquea la activación, ajusta la política temporalmente para la sesión actual:

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

```

- **Activar el entorno virtual:** Inicia el entorno ejecutando:

```powershell
.\.venv\Scripts\Activate.ps1

```

- **Instalar las dependencias:** Con el entorno activo, instala los paquetes necesarios para el backend (incluyendo los puentes JDBC):

```powershell
python -m pip install -r backend\requirements.txt

```

---

## 3. Verificación de Drivers Embebidos para HSQLDB

El proyecto incluye el driver JDBC necesario para conectar con HSQLDB sin necesidad de descargas externas.

- Comprueba que el driver se encuentra ubicado correctamente en el repositorio ejecutando:

```powershell
dir backend\drivers\hsqldb

```

- Debe aparecer listado el archivo principal del driver:

```text
hsqldb.jar

```

---

## 4. Creación del Directorio de Pruebas Local

Para simular el almacenamiento y persistencia de HSQLDB en un entorno de desarrollo local, crearemos una carpeta dedicada para la base de datos de prueba:

- Ejecuta el siguiente comando en PowerShell para crear el directorio de forma automatizada y forzada:

```powershell
New-Item -ItemType Directory -Path .\prueba_hsqldb -Force

```

---

## 5. Configuración de Variables de Entorno (`.env`)

La conexión con HSQLDB requiere que el archivo de configuración local apunte a la ruta de los datos:

- Crea el archivo `.env` a partir de la plantilla oficial incluida en el repositorio:

```powershell
Copy-Item .env.example .env

```

- Abre el archivo `.env` y configura la variable `HSQLDB_DATABASE` asignando la ruta absoluta o relativa de la carpeta de prueba que acabamos de crear:

```env
HSQLDB_DATABASE=C:\Ruta\De\Tu\Equipo\ETHAZI_RETO1\prueba_hsqldb

```

_(Nota: La ruta debe adaptarse rigurosamente a la ubicación real donde hayas clonado o guardado el proyecto en tu equipo)._

---

## 6. Verificación de la Conexión con HSQLDB

Una vez configurados el entorno virtual, las rutas y el archivo de variables de entorno, el proyecto cuenta con un script automatizado para comprobar que el conector funciona correctamente.

- Con el entorno virtual activo y situado en la raíz del proyecto, ejecuta la prueba unitaria de HSQLDB:

```powershell
python -m backend.tests.test_hsqldb

```

Si todos los pasos anteriores se han completado con éxito, el conector cargará el driver `hsqldb.jar`, establecerá la sesión JDBC contra la base de datos de prueba y validará la lectura de registros sin arrojar errores de dependencias o rutas.
