# Diagnóstico: Android y FastAPI

## 1. Arrancar API en el PC

Desde `backend/`, con el entorno virtual activo:

```powershell
python -m uvicorn api.main:app --host 0.0.0.0 --port 8000 --reload
```

Comprobar desde el navegador del PC:
- http://127.0.0.1:8000/docs
- http://127.0.0.1:8000/students

## 2. Elegir URL en Android

- Emulador de Android Studio: `http://10.0.2.2:8000/` (ya configurado).
- Móvil físico, misma red wifi: `http://IP_LOCAL_DEL_PC:8000/`, cambiando la URL en `StudentDetailActivity.kt`. El firewall del PC debe permitir las conexiones del móvil en la red privada.

Abrir desde el navegador del emulador `http://10.0.2.2:8000/students`. Si no responde, el problema es de conexión/servidor.

## 3. Revisar compatibilidad de endpoints

La app presupone:

- `GET /students?nombre=...` devuelve un *array JSON* de estudiantes, por ejemplo `[{"id":"S001","nombre":"Harry"}]`.
- `GET /students/{id}` devuelve un *objeto JSON* con las mismas propiedades.

**Esto debe comprobarse con vuestro código real de FastAPI**. Si devuelve `{"students": [...]}` o `{"data": [...]}` en lugar de un array, hay que adaptar Retrofit/Gson a la respuesta real. Si el campo ID se llama `dni` o `student_id`, hay que actualizar `Student.kt` o el backend.

## 4. Problema corregido de Room

El proyecto tenía `annotationProcessor` en un proyecto Kotlin. Se ha sustituido por KSP para que se generen las implementaciones de la base de datos Room. Una excepción `Cannot find implementation for AppDatabase` indica ese problema.

En Android Studio pulsa **Sync Project with Gradle Files** y **Build > Rebuild Project**.

## 5. Diagnosticar error exacto

En Android Studio, abre **Logcat** y filtra por `HogwartsAPI`. El código registra la excepción original, sin disfrazarla con una segunda petición al servidor. Posibles resultados:

- `Failed to connect to /10.0.2.2:8000`: servidor apagado o red.
- `HTTP 404`: endpoint equivocado o alumno inexistente.
- `Expected BEGIN_ARRAY but was BEGIN_OBJECT`: formato JSON distinto del esperado.
- `Cannot find implementation for AppDatabase`: Room no se generó correctamente; sincronizar y compilar.

**Nota**: los endpoints y el JSON real del backend no estaban incluidos en el ZIP. No se ha podido validar la integración extremo a extremo.
