# ETHAZI Android — selección entre varios alumnos y conexión con FastAPI

## Cambios

- La búsqueda por texto combina `GET /students?nombre=...` con `/connectors/{connector}/students/{nombre}` para **Derby, H2, HSQLDB y Oracle**. Así aparecen coincidencias de las cuatro casas incluso si `/students` devuelve solo alumnos cacheados.
- Si devuelve varias, aparece un cuadro de selección desplazable con **nombre completo y casa**. El alumno se abre mediante su UUID, no mediante el nombre, para distinguir homónimos.
- Si devuelve una sola coincidencia, se abre directamente. Si no devuelve ninguna, se muestra un mensaje.
- La búsqueda por UUID sigue disponible y consulta `GET /students/{id}`.
- La tarjeta *Last search* repite la búsqueda y también permite seleccionar entre varias coincidencias.
- La ficha seleccionada se guarda previamente en la caché Room por UUID; no se vuelve a buscar por nombre. Se evita consultar `/students?nombre=<UUID>` al cargarla.
- La dirección predeterminada es `http://127.0.0.1:8000/` para las pruebas con `adb reverse`. Si ya habías guardado otra dirección, se conserva; puedes cambiarla desde **Configurar API**.

## Conectar emulador en Windows

1. Arranca Docker y comprueba `http://127.0.0.1:8000/health` en Windows.
2. Arranca el emulador en Android Studio.
3. En PowerShell (Android Studio Terminal), ejecuta:

```powershell
& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000
```

4. En la aplicación, pulsa **Configurar API** y guarda `http://127.0.0.1:8000/`.
5. Comprueba **Probar conexión** y busca `Harry` o `Ha`.

> `adb reverse` no se mantiene necesariamente al reiniciar el emulador. La dirección `127.0.0.1` no sirve para un móvil físico sin redirección ADB. Para dispositivos reales, cambia la URL por la IP local del PC y permite el acceso a FastAPI desde la misma red.

## Nota del backend

Actualmente `/students?nombre=...` puede devolver solo los datos de SQLite si encuentra alguna coincidencia. Para evitar este límite, Android **combina** esa respuesta con búsquedas directas en las cuatro bases históricas. Si falla un conector, se registrará en Logcat (`HogwartsAPI`) y se muestran las coincidencias disponibles; para garantizar un resultado completo es preferible ajustar también el backend.

## Comprobar compilación

Abrir `app-android-proyecto` en Android Studio y sincronizar Gradle. Generar con `gradlew.bat :app:assembleDebug` desde Windows. Este paquete es **código fuente**, no una APK compilada.
