Instalación y configuración de HSQLDB
1. Crear la carpeta del driver
   backend/drivers/hsqldb/
2. Descargar el driver JDBC
   - Descargar hsqldb.jar.
   - Copiarlo en:
   backend/drivers/hsqldb/hsqldb.jar
3. Crear la carpeta de la base de datos
   prueba_hsqldb/
   
   En la raíz del proyecto.
4. Configurar el archivo .env
   HSQLDB_DATABASE=<RUTA_DEL_PROYECTO>\prueba_hsqldb
5. Configurar el conector
   - El archivo backend/connectors/hsqldb_connector.py utilizará:
     - HSQLDB_DATABASE para localizar la base de datos.
     - hsqldb.jar como driver JDBC.
     - org.hsqldb.jdbc.JDBCDriver como driver de conexión.
6. Activar el entorno virtual
   .venv\Scripts\activate
7. Comprobar la conexión
   Desde la raíz del proyecto:
   python -m backend.tests.test_hsqldb
8. Resultado esperado
   Conexión con HSQLDB realizada correctamente.
9. Estructura final
   RETO1/
   ├── backend/
   │   ├── connectors/
   │   │   └── hsqldb_connector.py
   │   ├── drivers/
   │   │   └── hsqldb/
   │   │       └── hsqldb.jar
   │   └── tests/
   │       └── test_hsqldb.py
   ├── prueba_hsqldb/
   └── .env