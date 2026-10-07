Manual de instalación — Reto 01
1. Objetivo
Este documento explica cómo preparar y ejecutar el backend del proyecto Reto 01 en un nuevo equipo.
El backend está desarrollado en Python y utiliza distintos conectores para acceder a las bases de datos del sistema.
Los drivers necesarios para Apache Derby se distribuyen junto con el proyecto, por lo que el usuario no necesita descargar ni instalar Apache Derby manualmente.
El proyecto se ha diseñado de forma modular y configurable, de acuerdo con los requisitos de instalación y reproducibilidad establecidos para el reto. Pliego Reto 01 (Conjunto)
2. Requisitos previos
El equipo deberá disponer de:
Software	Versión
Windows	Windows 10/11 64 bits
Python	3.14.x
Java JDK	21 LTS
Git	Solo necesario si se obtiene el proyecto mediante repositorio


Apache Derby no necesita instalarse, ya que sus drivers están incluidos dentro del proyecto.
3. Estructura básica del proyecto
La estructura relevante para el backend es:
ETHAZI_RETO1/
│
├── backend/
│   ├── api/
│   ├── connectors/
│   │   └── derby_connector.py
│   │
│   ├── drivers/
│   │   └── derby/
│   │       ├── derby.jar
│   │       ├── derbyshared.jar
│   │       └── derbytools.jar
│   │
│   ├── models/
│   ├── repositories/
│   ├── services/
│   ├── tests/
│   ├── utils/
│   │   └── config.py
│   │
│   └── requirements.txt
│
├── docs/
├── .env.example
├── .gitignore
└── README.md

Los drivers de Apache Derby ya se encuentran en:
backend/drivers/derby/

Por tanto, no se debe modificar su ubicación ni descargarlos nuevamente.
4. Instalación de Java 21
El proyecto utiliza Java JDK 21 LTS.
Una vez instalado Java, abrir PowerShell y comprobar:
java -version

Debe aparecer una versión 21, por ejemplo:
java version "21..."

También puede comprobarse:
javac -version

Debe mostrar:
javac 21...

Configurar JAVA_HOME
Si Java 21 no aparece como versión predeterminada, configurar la variable de entorno:
JAVA_HOME

para que apunte al directorio donde está instalado el JDK 21.
Ejemplo:
C:\Program Files\Java\jdk-21

En la variable Path debe existir:
%JAVA_HOME%\bin

Después de modificar las variables de entorno, cerrar y volver a abrir la terminal.
5. Instalación de Python
Instalar Python 3.
La versión utilizada durante el desarrollo es:
Python 3.14.x

Comprobar:
python --version

Debe aparecer algo similar a:
Python 3.14.7

6. Crear el entorno virtual
Desde la carpeta raíz del proyecto:
python -m venv .venv

Esto creará:
ETHAZI_RETO1/
└── .venv/

El entorno virtual permite instalar las dependencias del proyecto sin modificar las librerías globales del equipo.
7. Activar el entorno virtual
En PowerShell:
.\.venv\Scripts\Activate.ps1

Si PowerShell muestra un error indicando que la ejecución de scripts está deshabilitada, ejecutar:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

y posteriormente:
.\.venv\Scripts\Activate.ps1

Si funciona correctamente, aparecerá:
(.venv)

al principio de la terminal.
Ejemplo:
(.venv) PS C:\ETHAZI_RETO1>

La modificación de la política de ejecución realizada con -Scope Process solo afecta a esa sesión de PowerShell.
8. Instalar las dependencias
Con .venv activo y situado en la raíz del proyecto:
python -m pip install -r backend\requirements.txt

El archivo:
backend/requirements.txt

contiene las dependencias necesarias para el backend.
Actualmente incluye las librerías utilizadas para:
- FastAPI.
- Uvicorn.
- Validación de datos.
- Lectura del archivo .env.
- Comunicación entre Python y Java.
- Acceso a bases de datos mediante JDBC.
No es necesario instalar estas librerías manualmente una por una.
9. Drivers de Apache Derby
El cliente no tiene que descargar Apache Derby.
Los archivos necesarios están incluidos en:
backend/drivers/derby/

y son:
derby.jar
derbyshared.jar
derbytools.jar

El conector:
backend/connectors/derby_connector.py

localiza automáticamente estos archivos dentro del proyecto.
Por este motivo ya no se utiliza una variable:
DERBY_HOME

ni es necesario indicar dónde está instalado Apache Derby.
10. Configurar las variables de entorno
En la raíz del proyecto se proporciona:
.env.example

Este archivo contiene las variables que deben configurarse.
Se debe crear una copia y llamarla:
.env

En PowerShell se puede hacer:
Copy-Item .env.example .env

El archivo .env será específico de cada instalación.
11. Configuración de Apache Derby
Actualmente la configuración necesaria es:
DERBY_DATABASE=

DERBY_DATABASE indica dónde se encuentra la base de datos Derby que debe utilizar el sistema.
Por ejemplo:
DERBY_DATABASE=C:\Bases\datos_derby

El cliente deberá sustituir esa ruta por la ubicación real de la base proporcionada.
Importante
No es necesario indicar la ubicación de los drivers:
DERBY_HOME=

ya no existe ni es necesario, porque los drivers están incluidos dentro del proyecto.
12. Seguridad del archivo .env
El archivo:
.env

puede contener rutas, usuarios, contraseñas u otros parámetros específicos de cada instalación.
Por ello está excluido del repositorio mediante .gitignore.
No debe subirse a Git.
El archivo que sí permanece en el repositorio es:
.env.example

porque únicamente sirve como plantilla y no contiene información privada.
13. Comprobar la configuración
Desde la raíz del proyecto y con .venv activo:
python -c "from backend.utils.config import obtener_variable; print(obtener_variable('DERBY_DATABASE'))"

Debe aparecer la ruta configurada en .env.
Por ejemplo:
C:\Bases\datos_derby

Si aparece un mensaje indicando que:
DERBY_DATABASE

no está configurada, se debe revisar el archivo .env.
14. Comprobar el conector Derby
El proyecto dispone de una prueba de conexión en:
backend/tests/test_derby.py

Desde la raíz:
python -m backend.tests.test_derby

Si la configuración es correcta, Python utilizará:
backend/connectors/derby_connector.py

que a su vez cargará automáticamente:
backend/drivers/derby/

y realizará la conexión JDBC con la base Derby configurada.
El flujo es:
.env
  │
  │ DERBY_DATABASE
  ▼
config.py
  │
  ▼
derby_connector.py
  │
  ├── derby.jar
  ├── derbyshared.jar
  └── derbytools.jar
  │
  ▼
JPype / JayDeBeApi
  │
  ▼
JDBC
  │
  ▼
Base de datos Apache Derby

15. Qué tiene que instalar el cliente
Con la configuración actual, el cliente únicamente necesita instalar:
Python
Java 21

Después debe ejecutar:
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt

Y configurar:
.env

El cliente no tiene que instalar Apache Derby ni descargar sus drivers.
16. Resumen rápido
Para una instalación nueva:
cd ETHAZI_RETO1

Crear el entorno:
python -m venv .venv

Si PowerShell lo requiere:
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

Activar:
.\.venv\Scripts\Activate.ps1

Instalar las dependencias:
python -m pip install -r backend\requirements.txt

Crear la configuración:
Copy-Item .env.example .env

Editar .env y configurar:
DERBY_DATABASE=RUTA_DE_LA_BASE_DERBY

Finalmente comprobar:
python -m backend.tests.test_derby

Instalación final prevista
A medida que añadamos los demás conectores, este mismo manual irá creciendo, pero no habrá que repetir Python, Java, .venv ni requirements.txt.
Añadiremos secciones como:
Configuración de HSQLDB
Configuración de H2
Configuración de Oracle
Configuración de MariaDB
Configuración de SQLite