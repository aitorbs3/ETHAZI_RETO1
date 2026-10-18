Aquí tienes el manual de instalación, configuración y verificación completamente optimizado, limpio y ordenado, estructurado de forma profesional y **enfocado específicamente en el conector de Apache Derby** para el módulo de **Acceso a Datos (DAM 2º)** del proyecto **ETHAZI_RETO1**.

---

# Manual Técnico de Instalación y Configuración: Subsistema Apache Derby — ETHAZI_RETO1

## 1. Objetivo del Manual

Este documento detalla el procedimiento paso a paso para desplegar y configurar el backend del proyecto **Reto 01**, centrándose en el funcionamiento, integración y pruebas del conector de **Apache Derby** (que simula la fuente histórica de la casa _Gryffindor_).

Gracias al diseño modular del proyecto, **los drivers JDBC de Apache Derby se distribuyen embebidos dentro del propio repositorio**, por lo que no es necesario realizar ninguna instalación pesada del motor de base de datos en el sistema operativo del equipo.

---

## 2. Requisitos Previos del Sistema

Para garantizar la compatibilidad con los puentes de interoperabilidad JDBC entre Python y Java, el equipo de desarrollo debe contar con:

| Componente Software   | Versión Requerida         | Propósito Técnico                                                           |
| --------------------- | ------------------------- | --------------------------------------------------------------------------- |
| **Sistema Operativo** | Windows 10 / 11 (64 bits) | Entorno base de ejecución y pruebas.                                        |
| **Python**            | `3.14.x`                  | Lenguaje del backend y la API REST (FastAPI).                               |
| **Java JDK**          | `21 LTS`                  | Imprescindible para ejecutar la máquina virtual de Java y los drivers JDBC. |
| **Git**               | Última versión            | Para la obtención y clonación del repositorio del proyecto.                 |

---

## 3. Estructura de Ficheros y Drivers Embebidos de Derby

La jerarquía de directorios relevante para este subsistema se organiza de la siguiente manera:

```text
ETHAZI_RETO1/
│
├── backend/
│   ├── connectors/
│   │   └── derby_connector.py      # Lógica de conexión y consultas JDBC para Derby
│   │
│   ├── drivers/
│   │   └── derby/                  # Drivers JDBC embebidos (NO MODIFICAR)
│   │       ├── derby.jar
│   │       ├── derbyshared.jar
│   │       └── derbytools.jar
│   │
│   ├── tests/
│   │   └── test_derby.py           # Script de prueba manual/unitaria de Derby
│   │
│   ├── utils/
│   │   └── config.py               # Lector centralizado de variables de entorno
│   │
│   └── requirements.txt            # Dependencias de Python (FastAPI, JayDeBeApi, etc.)
│
├── .env.example                    # Plantilla de variables de entorno
└── .env                            # Configuración local privada (ignorada por Git)

```

> ⚠️ **Importante:** El conector (`derby_connector.py`) localiza los archivos `.jar` de forma estática en `backend/drivers/derby/`. **Nunca debes moverlos ni descargarlos externamente**. Por este motivo, la antigua variable de entorno `DERBY_HOME` queda totalmente obsoleta y deja de utilizarse.

---

## 4. Configuración de Java JDK 21

El motor JDBC de Derby requiere estrictamente Java 21 LTS.

1. Instala Java 21 y abre una terminal de **PowerShell** para comprobar su correcta instalación:

```powershell
java -version
javac -version

```

_(Ambos comandos deben retornar referencias a la versión 21)._ 2. **Configuración obligatoria de `JAVA_HOME`:**
Si la terminal no detecta la versión correcta de manera predeterminada, configura las variables de entorno de tu sesión actual de PowerShell:

```powershell
$env:JAVA_HOME="C:\Program Files\Java\jdk-21.0.12.1"
$env:Path="$env:JAVA_HOME\bin;$env:Path"

```

---

## 5. Configuración del Entorno Virtual de Python (`.venv`)

Para aislar las dependencias del proyecto y evitar conflictos globales en el equipo:

1. Sitúate en la carpeta raíz del proyecto (`ETHAZI_RETO1`) y crea el entorno virtual:

```powershell
python -m venv .venv

```

2. Activa el entorno virtual en PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1

```

- _Nota de permisos:_ Si PowerShell bloquea la ejecución de scripts, habilita temporalmente la política para la sesión actual ejecutando:\*

```powershell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

```

_Al activarse correctamente, aparecerá el prefijo `(.venv)` en la línea de comandos._

---

## 6. Instalación de Dependencias del Backend

Con el entorno virtual activo, instala de forma automatizada todas las librerías necesarias ejecutando:

```powershell
python -m pip install -r backend\requirements.txt

```

_Este fichero instala el framework FastAPI, el servidor Uvicorn y las librerías de enlace Python-Java (`JPype` / `JayDeBeApi`) indispensables para manejar los drivers `.jar` de Derby mediante JDBC._

---

## 7. Configuración de las Variables de Entorno para Derby (`.env`)

El sistema necesita conocer la ubicación exacta en tu disco duro del fichero de la base de datos histórica de Derby.

1. Genera tu archivo de configuración local a partir de la plantilla oficial:

```powershell
Copy-Item .env.example .env

```

2. Abre el archivo `.env` recién creado y define la ruta absoluta o relativa de la base de datos Derby mediante la variable `DERBY_DATABASE`:

```env
DERBY_DATABASE=C:\Bases\datos_derby

```

_(Sustituye la ruta por la ubicación real de la base de datos proporcionada en tu equipo)._

> 🔒 **Seguridad:** El archivo `.env` contiene rutas locales privadas y está excluido en el `.gitignore`. **Nunca debe subirse a Git**.

---

## 8. Verificación y Prueba del Conector Apache Derby

Una vez completada la configuración, el proyecto incluye un script de test específico para validar la comunicación con la base de datos Derby (`backend/tests/test_derby.py`).

### Flujo de Conexión Interno:

```text
.env
 └── DERBY_DATABASE (Ruta de los datos)
       ▼
   config.py (Carga segura)
       ▼
   derby_connector.py
       ├── derby.jar
       ├── derbyshared.jar
       └── derbytools.jar
             ▼
   JPype / JayDeBeApi (Puente Python ⇄ Java)
             ▼
   JDBC Driver Manager
             ▼
   Base de datos Apache Derby (Gryffindor)

```

### Ejecución de la prueba:

Desde la raíz del proyecto y con el entorno virtual activo (`.venv`), ejecuta el script de test:

```powershell
python -m backend.tests.test_derby

```

Si la configuración es correcta, el script se conectará mediante JDBC a Apache Derby, realizará una consulta de agregación y volcará por consola el número total de alumnos junto a una muestra de los registros de Gryffindor.

---

## 9. Resumen Exprés para Nuevas Instalaciones (Derby)

Copia y ejecuta estos comandos secuenciales en PowerShell si clonas el proyecto en un equipo limpio:

```powershell
# 1. Situarse en la raíz del proyecto
cd ETHAZI_RETO1

# 2. Crear y activar el entorno virtual de Python
python -m venv .venv
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass
.\.venv\Scripts\Activate.ps1

# 3. Instalar las dependencias del backend
python -m pip install -r backend\requirements.txt

# 4. Crear el fichero de configuración local
Copy-Item .env.example .env

# 5. Editar el archivo .env y configurar tu ruta de Derby:
# DERBY_DATABASE=C:\ruta\a\tu\base_derby

# 6. Comprobar que el conector Derby funciona correctamente
python -m backend.tests.test_derby

```
