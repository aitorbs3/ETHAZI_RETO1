# Corrección de búsqueda sin conexión (Room)

- `MainActivity.kt`: `searchStudents` consulta primero Room por nombre (incluidas coincidencias parciales) o UUID interno; si hay datos locales, abre inmediatamente la lista/ficha sin llamar a FastAPI.
- `StudentDao.kt`: se incorpora `getStudentsByName` para recuperar TODAS las coincidencias, sin usar `LIMIT 1` para las búsquedas.
- `MainActivity.kt`: cuando no hay coincidencias locales, las consultas a la API almacenan todas las fichas recibidas en Room, no solo la ficha seleccionada. Además se filtra por nombre cuando `/students` devuelve un listado completo.
- `StudentRepository.kt`: si existe la ficha en Room, se devuelve aunque no tenga fotografía, evitando esperas de red innecesarias.
- Se mantienen los campos internos (ID, alias, fuente) para Room y las consultas. Siguen ocultos en la pantalla de detalles.

## Comprobarlo

1. Instalar la APK actualizada **sin desinstalar** la anterior para conservar Room, usando la misma firma de depuración.
2. Con conexión a la API, buscar un nombre de alumno y abrir su ficha; volver a la pantalla de búsqueda.
3. Activar modo avión y realizar la misma búsqueda. Debe devolver los datos desde Room sin depender de la API.
4. Buscar también nombres que devuelvan varias coincidencias: deben aparecer las fichas guardadas en Room.

**Límite de diseño:** se prioriza la caché local. Para actualizar una ficha que ya existe en Room habrá que incorporar un comando explícito de sincronización/actualización desde la API en una futura versión.

**Sin compilación verificada:** este entorno no incluye Android SDK. Probar `Sync Project` y `Build APK(s)` en Android Studio.
