# ETHAZI Android — corrección de conexión con FastAPI

## Qué se ha corregido

- La URL de FastAPI ya no está repetida dentro de la ficha. La aplicación permite cambiarla desde **Configurar API** en la pantalla principal y la guarda en preferencias.
- Por defecto, en el **emulador Android Studio** se utiliza `http://10.0.2.2:8000/`.
- En **móvil físico**, utiliza `http://IP_LOCAL_DE_TU_PC:8000/` estando en la misma red. Comprueba que el firewall y Docker permitan acceder desde otros dispositivos.
- Se han ampliado los tiempos de conexión (20 s) y lectura (30 s), añadido un único reintento para errores transitorios de conexión y mejorado el aviso de error.
- Se eliminaron las referencias a los estudiantes ficticios `S001` y `Alexander Thornfield`. La previsualización muestra el último estudiante **real guardado en Room**.
- Los detalles de alumnos buscan por nombre mediante `GET /students?nombre=Harry` y, si se introduce un UUID válido, por `GET /students/{id}`.
- El indicador de caché no aparece hasta que se haya cargado un alumno correctamente.

## Cómo probar en Android Studio

1. Abre `app-android-proyecto` (esta carpeta contiene `settings.gradle.kts`).
2. Sincroniza Gradle y ejecuta la aplicación en el emulador.
3. En PowerShell, comprueba que la API funciona: `docker ps` y `Invoke-RestMethod "http://127.0.0.1:8000/students?nombre=Harry"`.
4. En Chrome **dentro del mismo emulador**, comprueba `http://10.0.2.2:8000/students?nombre=Harry`.
5. Dentro de la app, pulsa **Configurar API** y verifica `http://10.0.2.2:8000/`.
6. Pulsa **Probar conexión**: debe mostrar `API conectada correctamente`.
    7. Busca `Harry` y comprueba sus datos. Filtra Logcat con `tag:HogwartsAPI` si falla.

**Importante:** `SocketTimeoutException: failed to connect to 10.0.2.2:8000` indica un problema de conectividad. Mejorar los tiempos de espera/reintentos no sustituye tener Docker/FastAPI disponibles ni configurar correctamente la red de un móvil físico.

## Seguridad

El backend se usa por HTTP en la red local para las pruebas. Antes de distribuir la app públicamente, utiliza HTTPS y restringe `usesCleartextTraffic` a un perfil de desarrollo.

## Compilación

En Windows: `gradlew.bat :app:assembleDebug`. Requiere Android Studio, SDK instalado y acceso a las dependencias de Gradle.
No se incluye ningún APK compilado; primero comprueba la compilación en Android Studio.

Si el navegador del emulador funciona pero la propia aplicación no, **Probar conexión** hace una petición Retrofit real a `GET /health`; consulta Logcat (`HogwartsAPI`) para distinguir un problema de red, firewall, DNS, proxy o servidor.
