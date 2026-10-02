# Manual de instalación

## 1. Requisitos

- Git
- Python 3.14.7

## 2. Obtener el proyecto

Clonar el repositorio:

```bash
git clone URL_DEL_REPOSITORIO
cd RETO1

## Instalación del backend

1. Instalar Python 3.14.7

2. Crear entorno virtual:
   python -m venv .venv

3. Instalar dependencias:
   pip install -r requirements.txt

4. Ejecutar API:
   cd backend
   ..\.venv\Scripts\python.exe -m uvicorn api.main:app --reload