# Android ETHAZI — Fotografías e idiomas

## Cambios

- Las URL del campo `imagen` de FastAPI se almacenan en Room (`imageUrl`) y se cargan mediante Glide en la ficha, previsualización y lista de coincidencias. Si faltan o el servidor remoto no responde, aparece el icono local `usuario`.
- Room migra automáticamente la tabla de versión 1 a versión 2, conservando alumnos y caché existentes.
- Selector de interfaz Español / Euskara / English en la pantalla principal. Los datos de la API (nombres, casas, especie, Patronus...) **no se traducen**.
- Se conservan la búsqueda por varias casas, la selección por UUID y la dirección de API configurable.

## Probar

1. Abrir `app-android-proyecto` en Android Studio y sincronizar Gradle (se descargará Glide si no está en caché).
2. Docker/FastAPI arrancado en el PC. Para emulador con `127.0.0.1:8000`, en PowerShell del PC: `& "$env:LOCALAPPDATA\Android\Sdk\platform-tools\adb.exe" reverse tcp:8000 tcp:8000`.
3. Buscar **Harry**, abrir la ficha, cambiar idioma y volver a probar. Verificar que la API devuelve `imagen` con una URL accesible; algunas imágenes externas pueden bloquear descargas.
4. La APK está pendiente de compilación real con el SDK en Android Studio; los XML y el código han pasado verificaciones estáticas, no pruebas instrumentadas.

## Nota

Un estudiante sin `imagen` o con URL bloqueada verá el icono de usuario, pero los datos seguirán visibles. La selección de idioma se guarda localmente.
