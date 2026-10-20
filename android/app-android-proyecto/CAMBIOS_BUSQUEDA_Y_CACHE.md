# Ajustes de búsqueda y caché (20/10/2026)

Cambios en el proyecto original:
- `MainActivity.kt`: elimina el contenido del buscador **solo después** de localizar, seleccionar y guardar correctamente un alumno en Room. No borra el texto si la búsqueda falla, no devuelve resultados o se cancela la lista de coincidencias.
- `MainActivity.kt`: consulta Room para mostrar un estado real de caché. Al iniciarse sin alumnos guardados aparece «Caché no disponible» con indicador gris. Cuando hay alumnos guardados muestra la disponibilidad sin conexión en verde. Cuando se inicia una búsqueda que todavía no está guardada, muestra que el alumno no está disponible offline hasta guardarlo.
- `StudentDao.kt`: agrega la consulta `hasCachedStudents()`.
- `activity_main.xml`: agrega IDs a las etiquetas de estado y al indicador de caché.
- `shape_gray_dot.xml`: estado gris de caché no disponible.
- `strings.xml`: añade mensajes en español, inglés y euskera.

## Instalación
1. Descomprimir el ZIP.
2. Abrir `app-android-proyecto` en Android Studio.
3. Esperar a que Gradle sincronice y ejecutar la aplicación.
4. Probar inicialmente con la caché vacía (instalación limpia o eliminando datos de la app en un dispositivo de pruebas; esto borra los datos locales previos).
5. Buscar un alumno real que no esté en Room: antes de guardarlo, la caché aparecerá como no disponible; tras resolver y guardar el alumno, aparecerá disponible. El campo de búsqueda se limpiará al abrir su ficha.
6. Probar un nombre inexistente: el campo de búsqueda se conserva.

No se ha generado ni validado una APK con Android SDK en este entorno. Se ha verificado que los XML son válidos.
