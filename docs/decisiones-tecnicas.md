SQLite es la caché principal y debe estar lo más actualizada posible.
Si SQLite está disponible, las consultas empiezan siempre ahí.
Si no encuentra el estudiante, se buscan los datos necesarios en las fuentes externas.
Si SQLite está caída, solo se permiten consultas.
En ese caso el orden es MariaDB → Oracle → H2 → HSQLDB → Derby.
Si SQLite está caída, MariaDB no se utiliza como caché.
Oracle, H2, HSQLDB y Derby son solo lectura.
SQLite y MariaDB permiten modificaciones.
Las modificaciones se aplican primero en SQLite y después se sincronizan con MariaDB.
Si MariaDB está caída, el cambio queda pendiente de sincronización, pero SQLite mantiene el cambio.
Una búsqueda que encuentra un estudiante en una fuente externa guarda el estudiante completo en SQLite.
Para búsquedas múltiples, se combinan resultados y se eliminan duplicados usando el ID del estudiante.
Las aplicaciones no eligen la BD. Solo consumen la API.
Las tres aplicaciones consultan mediante los mismos servicios/endpoints.
La API devuelve JSON, que consumen JavaFX, Android y Unity.
Unity usará el campo patronus para representar el prefab.
Android tendrá además su propia caché SQLite local.