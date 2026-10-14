# Manual de Instalación y Verificación — H2 Database Connector (DAM 2º Año)

Este documento detalla los pasos requeridos para preparar el entorno local de desarrollo y ejecutar la prueba de conexión y persistencia JDBC con la base de datos **H2** en un nuevo equipo.

---

## 1. Requisitos Previos

Antes de comenzar, asegúrate de tener instalado el siguiente software en tu sistema:

| Software | Versión Requerida | Comprobación en Terminal |
| :--- | :--- | :--- |
| **Windows** | 10 / 11 (64 bits) | N/A |
| **Python** | 3.14.x | `python --version` |
| **Java JDK** | 21 LTS | `java -version` |
| **Git** | Última versión estable | `git --version` |

> ⚠️ **Nota sobre Java:** Asegúrate de que la variable de entorno `JAVA_HOME` apunte a la instalación del JDK 21.

---

## 2. Descargar el Proyecto y Actualizar la Rama

Abre PowerShell en tu carpeta de trabajo y clona el repositorio (o haz un `pull` si ya lo tienes):

```powershell
# Acceder al proyecto
cd ETHAZI_RETO1

# Cambiar a la rama de trabajo y descargar los últimos cambios
git checkout feature/database
git pull origin feature/database


---


# 1. Crear el entorno virtual (si no lo has creado previamente)
python -m venv .venv

# 2. Desbloquear la ejecución de scripts en la sesión actual de PowerShell
Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass

# 3. Activar el entorno virtual
.\.venv\Scripts\Activate.ps1


python -m pip install -r backend\requirements.txt

Crear el archivo .env:
Duplica el archivo de plantilla .env.example para generar tu configuración local:

PowerShell
Copy-Item .env.example .env
Crear la carpeta local para la base de datos de prueba:

PowerShell
New-Item -ItemType Directory -Path .\prueba_h2 -Force
Configurar la variable de entorno H2_DATABASE:
Abre el archivo .env recién creado y define la ruta absoluta apuntando a la carpeta prueba_h2 creada, indicando el nombre base que tendrá el archivo de la base de datos (por ejemplo, datos_h2):

Fragmento de código
# .env
H2_DATABASE=C:\Ruta\De\Tu\Equipo\ETHAZI_RETO1\prueba_h2\datos_h2