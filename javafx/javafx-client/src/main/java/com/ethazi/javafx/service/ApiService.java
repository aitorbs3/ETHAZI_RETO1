package com.ethazi.javafx.service;

// Modelo que representa los datos de un alumno dentro de JavaFX.
import com.ethazi.javafx.model.Student;

// Modelo que contiene los datos necesarios para crear o modificar un alumno.
import com.ethazi.javafx.model.NuevoAlumno;

// Permite construir objetos JSON para enviar datos a la API.
import com.fasterxml.jackson.databind.node.ObjectNode;

// Permite leer y recorrer elementos de una estructura JSON.
import com.fasterxml.jackson.databind.JsonNode;

// Objeto principal de Jackson para convertir entre JSON y estructuras Java.
import com.fasterxml.jackson.databind.ObjectMapper;

import java.io.IOException;
import java.net.URI;
import java.net.URLEncoder;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.nio.charset.StandardCharsets;
import java.time.Duration;
import java.util.ArrayList;
import java.util.List;
import java.util.concurrent.CompletableFuture;
import java.util.concurrent.CompletionException;

/**
 * Servicio encargado de comunicarse con el backend FastAPI mediante HTTP.
 *
 * Centraliza las operaciones para consultar, crear, modificar y eliminar
 * alumnos, así como para comprobar la conectividad con la API.
 *
 * Las peticiones se realizan de forma asíncrona para evitar bloquear
 * el hilo principal de JavaFX mientras se espera una respuesta del servidor.
 *
 * Esta clase no accede directamente a ninguna base de datos:
 * todas las operaciones se delegan en los endpoints de FastAPI.
 */
public class ApiService {

    // Dirección base del backend FastAPI.
    // Todas las rutas de las peticiones HTTP se construyen a partir de esta URL.
    private static final String BASE_URL = "http://127.0.0.1:8000";

    // Instancia de Jackson utilizada para generar y procesar datos JSON.
    // Al ser estática y final, se comparte entre las operaciones del servicio.
    private static final ObjectMapper JSON = new ObjectMapper();

    // Cliente HTTP utilizado para enviar peticiones al backend.
    // Se configura con HTTP/1.1 y un tiempo máximo de cinco segundos
    // para establecer la conexión inicial con el servidor.
    private final HttpClient client = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    /**
     * Comprueba si el backend responde correctamente.
     *
     * Envía una petición GET al endpoint /health y devuelve un resultado
     * booleano que indica si el código HTTP recibido es 200.
     *
     * No procesa el contenido de la respuesta porque solo interesa
     * comprobar el estado de la conexión.
     *
     * @return futuro que contiene true si la respuesta es HTTP 200,
     *         o false si se recibe otro código HTTP
     */
    public CompletableFuture<Boolean> comprobarConexion() {

        // Construye la petición GET dirigida al endpoint de salud de la API.
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/health"))
                .timeout(Duration.ofSeconds(5))
                .GET()
                .build();

        // Envía la petición de forma asíncrona y descarta el cuerpo de respuesta.
        // Cuando llega la respuesta, comprueba si el código HTTP es 200.
        return client.sendAsync(request, HttpResponse.BodyHandlers.discarding())
                .thenApply(response -> response.statusCode() == 200);
    }

    /**
     * Busca alumnos por nombre o recupera todos los alumnos disponibles
     * en el endpoint /students.
     *
     * Si el nombre recibido está vacío o contiene únicamente espacios,
     * consulta la ruta general /students.
     *
     * Si se proporciona un nombre, lo codifica para utilizarlo como
     * parámetro de una URL y realiza la búsqueda correspondiente.
     *
     * @param nombre nombre o texto utilizado para buscar alumnos
     * @return futuro con la lista de alumnos obtenida desde la API
     */
    public CompletableFuture<List<Student>> buscarAlumnosPorNombre(String nombre) {

        // Evita errores si el parámetro es null y elimina espacios exteriores.
        String busqueda = nombre == null ? "" : nombre.strip();

        // Selecciona la ruta según exista o no un término de búsqueda.
        // URLEncoder evita problemas con espacios y caracteres especiales
        // al introducir el nombre como parámetro de consulta.
        String ruta = busqueda.isEmpty()
                ? "/students"
                : "/students?nombre=" + URLEncoder.encode(busqueda, StandardCharsets.UTF_8);

        // Construye una petición GET con un tiempo máximo de veinte segundos.
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + ruta))
                .timeout(Duration.ofSeconds(20))
                .GET()
                .build();

        // Envía la petición sin bloquear el hilo principal de JavaFX.
        // La respuesta se interpreta como texto codificado en UTF-8.
        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {

                    // Si la API no responde con HTTP 200, genera un error.
                    if (response.statusCode() != 200) {
                        throw new CompletionException(new IOException(
                                "FastAPI devolvió HTTP " + response.statusCode()
                        ));
                    }

                    try {
                        // Convierte el JSON recibido en una lista de objetos Student.
                        return convertirAlumnos(response.body());
                    } catch (IOException ex) {

                        // Envuelve el error de entrada/salida para propagarlo
                        // a través de la cadena de operaciones asíncronas.
                        throw new CompletionException(ex);
                    }
                });
    }

    /**
     * Registra un alumno nuevo mediante una petición POST a /students.
     *
     * Convierte los datos del formulario a JSON, envía la petición al backend
     * y transforma la respuesta en un objeto Student.
     *
     * @param alumno objeto con los datos del alumno que se quiere crear
     * @return futuro con el alumno creado y los datos devueltos por la API
     */
    public CompletableFuture<Student> crearAlumno(NuevoAlumno alumno) {

        // Convierte los datos del formulario al formato JSON esperado por la API.
        ObjectNode datos = jsonAlumno(alumno);

        // Construye la petición POST para registrar el nuevo alumno.
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/students"))
                .timeout(Duration.ofSeconds(20))

                // Indica que el contenido enviado es JSON codificado en UTF-8.
                .header("Content-Type", "application/json; charset=UTF-8")

                // Indica que el cliente espera recibir una respuesta JSON.
                .header("Accept", "application/json")

                // Envía el objeto JSON como cuerpo de la petición.
                .POST(HttpRequest.BodyPublishers.ofString(datos.toString(), StandardCharsets.UTF_8))
                .build();

        // Ejecuta la petición y procesa la respuesta cuando esté disponible.
        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {

                    // Acepta HTTP 200 y HTTP 201 como respuestas correctas.
                    // El resto de códigos se consideran errores.
                    if (response.statusCode() != 200 && response.statusCode() != 201) {
                        throw new CompletionException(new IOException(
                                "HTTP " + response.statusCode() + ": "
                                        + detalleError(response.body())
                        ));
                    }

                    try {
                        // Interpreta el cuerpo de la respuesta como un nodo JSON.
                        JsonNode nodo = JSON.readTree(response.body());

                        // Comprueba que la API haya devuelto un objeto JSON válido.
                        if (nodo == null || !nodo.isObject()) {
                            throw new IOException("La API no devolvió el alumno creado.");
                        }

                        // Convierte los datos devueltos por FastAPI en un Student.
                        return convertirAlumno(nodo);
                    } catch (IOException ex) {
                        throw new CompletionException(ex);
                    }
                });
    }

    /**
     * Actualiza los datos de un alumno mediante una petición PUT.
     *
     * Antes de enviar la petición, comprueba que el identificador sea válido
     * y que el alumno pertenezca a la casa Hogwarths, según las reglas
     * establecidas en este cliente.
     *
     * @param id identificador del alumno que se quiere modificar
     * @param alumno nuevos datos del alumno
     * @return futuro con el alumno actualizado
     */
    public CompletableFuture<Student> actualizarAlumno(String id, NuevoAlumno alumno) {

        // Impide continuar si el identificador no existe o no es válido.
        if (id == null || id.isBlank() || "—".equals(id)) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El alumno no tiene un ID válido."));
        }

        // Restringe las modificaciones a alumnos de Hogwarths.
        // La comparación no distingue entre mayúsculas y minúsculas.
        if (!"Hogwarths".equalsIgnoreCase(alumno.casa())) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("Solo se pueden modificar alumnos de Hogwarths."));
        }

        // Convierte los datos del alumno a un objeto JSON.
        ObjectNode datos = jsonAlumno(alumno);

        // Construye la petición PUT dirigida al identificador concreto.
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/students/"
                        + URLEncoder.encode(id, StandardCharsets.UTF_8)))
                .timeout(Duration.ofSeconds(20))
                .header("Content-Type", "application/json; charset=UTF-8")
                .header("Accept", "application/json")

                // Envía los nuevos datos para sustituir o actualizar el registro.
                .PUT(HttpRequest.BodyPublishers.ofString(datos.toString(), StandardCharsets.UTF_8))
                .build();

        // Ejecuta la petición de manera asíncrona.
        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {

                    // Para esta operación, únicamente HTTP 200 se considera correcto.
                    if (response.statusCode() != 200) {
                        throw new CompletionException(new IOException(
                                "HTTP " + response.statusCode() + ": "
                                        + detalleError(response.body())));
                    }

                    try {
                        // Convierte la respuesta del servidor a un nodo JSON.
                        JsonNode nodo = JSON.readTree(response.body());

                        // Verifica que el backend haya devuelto un objeto JSON.
                        if (nodo == null || !nodo.isObject()) {
                            throw new IOException("La API no devolvió el alumno actualizado.");
                        }

                        // Devuelve el alumno con los datos confirmados por la API.
                        return convertirAlumno(nodo);
                    } catch (IOException ex) {
                        throw new CompletionException(ex);
                    }
                });
    }

    /**
     * Elimina un alumno mediante una petición DELETE.
     *
     * Comprueba primero que el identificador sea válido y después solicita
     * al backend que elimine el registro correspondiente.
     *
     * @param id identificador del alumno que se quiere eliminar
     * @return futuro que termina cuando la API confirma la operación
     */
    public CompletableFuture<Void> eliminarAlumno(String id) {

        // Evita enviar peticiones con un identificador vacío o inexistente.
        if (id == null || id.isBlank() || "—".equals(id)) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El alumno no tiene un ID válido."));
        }

        // Construye la petición DELETE para el alumno indicado.
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/students/"
                        + URLEncoder.encode(id, StandardCharsets.UTF_8)))
                .timeout(Duration.ofSeconds(20))
                .header("Accept", "application/json")
                .DELETE()
                .build();

        // Envía la petición y procesa la respuesta del servidor.
        return client.sendAsync(request,
                        HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {

                    // Guarda el código HTTP para comprobar el resultado.
                    int codigo = response.statusCode();

                    // Acepta los códigos habituales de eliminación correcta:
                    // 200 (OK), 202 (Accepted) y 204 (No Content).
                    if (codigo != 200 && codigo != 202 && codigo != 204) {
                        throw new CompletionException(new IOException(
                                "HTTP " + codigo + ": " + detalleError(response.body())
                        ));
                    }

                    // No se devuelve información porque la operación solo
                    // necesita indicar que ha terminado correctamente.
                    return null;
                });
    }

    /**
     * Construye el objeto JSON que se envía al crear o actualizar un alumno.
     *
     * Centraliza la preparación de los datos para que las operaciones POST
     * y PUT utilicen la misma estructura JSON.
     *
     * Los campos opcionales se procesan mediante campoNulo().
     *
     * @param alumno datos del formulario
     * @return objeto JSON con los campos esperados por FastAPI
     */
    private static ObjectNode jsonAlumno(NuevoAlumno alumno) {

        // Crea un objeto JSON vacío al que se añadirán los campos del alumno.
        ObjectNode datos = JSON.createObjectNode();

        // Añade el nombre del alumno.
        datos.put("nombre", alumno.nombre());

        // Establece la casa como Hogwarths, independientemente del valor
        // de casa contenido en el objeto recibido.
        datos.put("casa", "Hogwarths");

        // Añade los campos opcionales, convirtiendo los valores vacíos en null.
        campoNulo(datos, "especie", alumno.especie());
        campoNulo(datos, "genero", alumno.genero());
        campoNulo(datos, "nacimiento", alumno.nacimiento());
        campoNulo(datos, "nacionalidad", alumno.nacionalidad());
        campoNulo(datos, "patronus", alumno.patronus());
        campoNulo(datos, "imagen", alumno.imagen());

        // Mantiene la compatibilidad con el modelo de Python si el campo
        // patronus_origen continúa siendo obligatorio en el backend.
        // Si no hay Patronus, se indica que no está especificado.
        // En caso contrario, se indica que se introdujo manualmente.
        datos.put("patronus_origen", alumno.patronus() == null
                ? "No especificado" : "Introducido manualmente");

        // Devuelve el objeto JSON preparado para enviarlo a la API.
        return datos;
    }

    /**
     * Añade un campo al objeto JSON gestionando los valores vacíos.
     *
     * Si el valor es null o está vacío después de eliminar los espacios
     * exteriores, se representa como null en JSON.
     *
     * Si contiene información, se eliminan los espacios exteriores
     * y se añade como una cadena de texto.
     *
     * @param nodo objeto JSON que se va a modificar
     * @param nombre nombre del campo que se añadirá
     * @param valor valor asociado al campo
     */
    private static void campoNulo(ObjectNode nodo, String nombre, String valor) {

        // Los valores inexistentes o vacíos se representan como null en JSON.
        if (valor == null || valor.isBlank()) {
            nodo.putNull(nombre);
        } else {

            // Si existe un valor, elimina los espacios exteriores y lo guarda.
            nodo.put(nombre, valor.strip());
        }
    }

    /**
     * Extrae un mensaje de error legible a partir de la respuesta de la API.
     *
     * Intenta interpretar el cuerpo como JSON y buscar el campo "detail",
     * que suele contener información sobre el error en FastAPI.
     *
     * Si no puede interpretar el JSON o no existe ese campo, utiliza
     * directamente el cuerpo de la respuesta.
     *
     * Para evitar mensajes excesivamente largos, limita el texto devuelto.
     *
     * @param cuerpo contenido de la respuesta HTTP
     * @return mensaje de error resumido
     */
    private static String detalleError(String cuerpo) {

        try {
            // Intenta interpretar el cuerpo como una estructura JSON.
            JsonNode error = JSON.readTree(cuerpo);

            // Si existe el campo "detail", lo utiliza como descripción del error.
            if (error != null && error.has("detail")) {

                // Convierte el contenido de "detail" a texto.
                String mensaje = error.get("detail").toString();

                // Limita el mensaje a 600 caracteres cuando sea necesario.
                return mensaje.length() > 600
                        ? mensaje.substring(0, 600) + "..."
                        : mensaje;
            }
        } catch (Exception ignored) {

            // Si la respuesta no es JSON válido, continúa con el texto original.
        }

        // Como alternativa, devuelve el cuerpo de la respuesta,
        // limitado a 400 caracteres para evitar mensajes demasiado extensos.
        return cuerpo.length() > 400
                ? cuerpo.substring(0, 400) + "..."
                : cuerpo;
    }

    /**
     * Convierte un objeto JSON individual en un objeto Student.
     *
     * Recupera los campos del alumno utilizando los métodos auxiliares
     * para gestionar los valores ausentes, nulos o vacíos.
     *
     * La imagen se procesa de forma independiente porque es un campo opcional.
     *
     * @param nodo objeto JSON que representa a un alumno
     * @return objeto Student construido a partir de los datos recibidos
     */
    private Student convertirAlumno(JsonNode nodo) {

        // Extrae los datos del JSON y los utiliza para construir el alumno.
        return new Student(
                campo(nodo, "id"),
                campo(nodo, "nombre"),
                campo(nodo, "casa"),
                campo(nodo, "especie"),
                campo(nodo, "genero"),
                campo(nodo, "nacimiento"),
                campo(nodo, "nacionalidad"),
                campo(nodo, "patronus"),

                // La imagen puede no existir o no tener un valor utilizable.
                campoOpcional(nodo, "imagen")
        );
    }

    /**
     * Convierte una respuesta JSON que contiene una lista de alumnos.
     *
     * Comprueba que la estructura recibida sea un array JSON y recorre
     * sus elementos para transformar cada uno en un objeto Student.
     *
     * @param contenido respuesta JSON recibida desde FastAPI
     * @return lista de alumnos convertidos
     * @throws IOException si el JSON no puede interpretarse o no es un array
     */
    private List<Student> convertirAlumnos(String contenido) throws IOException {

        // Interpreta el texto recibido como una estructura JSON.
        JsonNode raiz = JSON.readTree(contenido);

        // Verifica que la respuesta sea un array JSON.
        if (raiz == null || !raiz.isArray()) {
            throw new IOException("La API no devolvió una lista JSON de alumnos.");
        }

        // Crea la lista que contendrá los alumnos convertidos.
        List<Student> resultado = new ArrayList<>();

        // Recorre cada elemento del array y lo convierte en un Student.
        for (JsonNode nodo : raiz) {
            resultado.add(convertirAlumno(nodo));
        }

        // Devuelve la lista completa de alumnos.
        return resultado;
    }

    /**
     * Recupera un campo de texto de un objeto JSON.
     *
     * Si el campo no existe, contiene null o está vacío, devuelve "—"
     * como valor de sustitución para mostrar que el dato no está disponible.
     *
     * @param nodo objeto JSON del que se extrae el campo
     * @param nombreCampo nombre de la propiedad que se quiere consultar
     * @return valor del campo o "—" si no contiene información utilizable
     */
    private static String campo(JsonNode nodo, String nombreCampo) {

        // Obtiene el campo solicitado.
        // path() permite consultar campos inexistentes sin lanzar una excepción.
        JsonNode valor = nodo.path(nombreCampo);

        // Si el campo no existe o su valor es null, devuelve el marcador.
        if (valor.isMissingNode() || valor.isNull()) {
            return "—";
        }

        // Convierte el valor a texto y elimina los espacios exteriores.
        String texto = valor.asText().strip();

        // Si el resultado está vacío, devuelve el marcador.
        return texto.isEmpty() ? "—" : texto;
    }

    /**
     * Recupera un campo opcional de un objeto JSON.
     *
     * A diferencia de campo(), este método devuelve null cuando la propiedad
     * no existe, contiene null o está vacía. Se utiliza para la imagen,
     * ya que puede no haber una URL disponible.
     *
     * @param nodo objeto JSON del que se extrae el campo
     * @param nombreCampo nombre de la propiedad que se quiere consultar
     * @return valor del campo o null si no existe un valor utilizable
     */
    private static String campoOpcional(JsonNode nodo, String nombreCampo) {

        // Obtiene el campo solicitado sin provocar errores si no existe.
        JsonNode valor = nodo.path(nombreCampo);

        // Si no existe o contiene null, devuelve null.
        if (valor.isMissingNode() || valor.isNull()) {
            return null;
        }

        // Convierte el valor a texto y elimina los espacios exteriores.
        String texto = valor.asText().strip();

        // Devuelve null si está vacío; en caso contrario, devuelve la URL.
        return texto.isEmpty() ? null : texto;
    }
}