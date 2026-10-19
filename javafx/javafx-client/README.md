# Hogwarts — Cliente JavaFX (fase 1)

Primera pantalla funcional **con datos ficticios**. No se conecta aún a FastAPI ni a ninguna base de datos. No permite realizar cambios persistentes.

## Requisitos de desarrollo

- Windows 10/11 o Linux de escritorio con entorno gráfico.
- JDK 21.
- Maven 3.9+ o Maven incluido en IntelliJ IDEA.
- Internet la primera vez para descargar las dependencias Maven.

## Abrir en IntelliJ

1. Copiar esta carpeta `javafx-client` dentro del repositorio `ETHAZI_RETO1`.
2. En IntelliJ: `File > Open` y seleccionar `javafx-client/pom.xml` (abrir como proyecto Maven).
3. Configurar **Project SDK = JDK 21** y recargar Maven.
4. Desde la terminal integrada de IntelliJ, ejecutar:

   ```powershell
   mvn clean javafx:run
   ```

   Si `mvn` no está en el PATH, ejecutar `javafx:run` desde el panel **Maven > Plugins > javafx** de IntelliJ.

## Qué funciona en esta fase

- Pantalla sin barra lateral, con estilo plateado/azul.
- Listado de seis estudiantes ficticios.
- Búsqueda por nombre o identificador en tiempo real.
- Filtro por base de datos.
- Panel de detalles al seleccionar una fila.
- Botón `Actualizar`: restablece el listado de demostración.
- Botones CRUD: muestran avisos; todavía no modifican registros.

## Siguiente fase

1. Crear `service/ApiService.java` con `java.net.http.HttpClient`.
2. Reemplazar los registros ficticios por las respuestas JSON de FastAPI.
3. Implementar consulta, alta, edición y borrado solo para los datos y operaciones autorizados en la API (las bases históricas son de lectura).
4. Manejar estados de conexión, errores y carga.
5. Preparar los empaquetados Windows y Linux. La entrega Fat JAR exige revisar las dependencias nativas de JavaFX por plataforma.
