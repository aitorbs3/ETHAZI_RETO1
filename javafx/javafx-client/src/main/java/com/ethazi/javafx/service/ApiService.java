package com.ethazi.javafx.service;

import com.ethazi.javafx.model.Student;
import com.ethazi.javafx.model.NuevoAlumno;
import com.fasterxml.jackson.databind.node.ObjectNode;
import com.fasterxml.jackson.databind.JsonNode;
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
 * Cliente HTTP para consultar alumnos a través de FastAPI.
 * No accede directamente a ninguna base de datos.
 */
public class ApiService {

    private static final String BASE_URL = "http://127.0.0.1:8000";
    private static final ObjectMapper JSON = new ObjectMapper();

    private final HttpClient client = HttpClient.newBuilder()
            .version(HttpClient.Version.HTTP_1_1)
            .connectTimeout(Duration.ofSeconds(5))
            .build();

    /** Consulta de conectividad opcional. */
    public CompletableFuture<Boolean> comprobarConexion() {
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/health"))
                .timeout(Duration.ofSeconds(5))
                .GET()
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.discarding())
                .thenApply(response -> response.statusCode() == 200);
    }

    /**
     * Busca por nombre en /students?nombre=... .
     * Si el nombre está vacío, consulta /students (alumnos ya guardados localmente).
     * La petición se realiza de forma asíncrona para no bloquear JavaFX.
     */
    public CompletableFuture<List<Student>> buscarAlumnosPorNombre(String nombre) {
        String busqueda = nombre == null ? "" : nombre.strip();
        String ruta = busqueda.isEmpty()
                ? "/students"
                : "/students?nombre=" + URLEncoder.encode(busqueda, StandardCharsets.UTF_8);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + ruta))
                .timeout(Duration.ofSeconds(20))
                .GET()
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {
                    if (response.statusCode() != 200) {
                        throw new CompletionException(new IOException(
                                "FastAPI devolvió HTTP " + response.statusCode()
                        ));
                    }

                    try {
                        return convertirAlumnos(response.body());
                    } catch (IOException ex) {
                        throw new CompletionException(ex);
                    }
                });
    }

    /** Registra un alumno de Hogwarths mediante POST /students. */
    public CompletableFuture<Student> crearAlumno(NuevoAlumno alumno) {
        ObjectNode datos = jsonAlumno(alumno);

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/students"))
                .timeout(Duration.ofSeconds(20))
                .header("Content-Type", "application/json; charset=UTF-8")
                .header("Accept", "application/json")
                .POST(HttpRequest.BodyPublishers.ofString(datos.toString(), StandardCharsets.UTF_8))
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {
                    if (response.statusCode() != 200 && response.statusCode() != 201) {
                        throw new CompletionException(new IOException(
                                "HTTP " + response.statusCode() + ": "
                                        + detalleError(response.body())
                        ));
                    }
                    try {
                        JsonNode nodo = JSON.readTree(response.body());
                        if (nodo == null || !nodo.isObject()) {
                            throw new IOException("La API no devolvió el alumno creado.");
                        }
                        return convertirAlumno(nodo);
                    } catch (IOException ex) {
                        throw new CompletionException(ex);
                    }
                });
    }

    /** Modifica un alumno nuevo por su UUID sin bloquear el hilo de JavaFX. */
    public CompletableFuture<Student> actualizarAlumno(String id, NuevoAlumno alumno) {
        if (id == null || id.isBlank() || "—".equals(id)) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El alumno no tiene un ID válido."));
        }
        if (!"Hogwarths".equalsIgnoreCase(alumno.casa())) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("Solo se pueden modificar alumnos de Hogwarths."));
        }

        ObjectNode datos = jsonAlumno(alumno);
        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/students/"
                        + URLEncoder.encode(id, StandardCharsets.UTF_8)))
                .timeout(Duration.ofSeconds(20))
                .header("Content-Type", "application/json; charset=UTF-8")
                .header("Accept", "application/json")
                .PUT(HttpRequest.BodyPublishers.ofString(datos.toString(), StandardCharsets.UTF_8))
                .build();

        return client.sendAsync(request, HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {
                    if (response.statusCode() != 200) {
                        throw new CompletionException(new IOException(
                                "HTTP " + response.statusCode() + ": "
                                        + detalleError(response.body())));
                    }
                    try {
                        JsonNode nodo = JSON.readTree(response.body());
                        if (nodo == null || !nodo.isObject()) {
                            throw new IOException("La API no devolvió el alumno actualizado.");
                        }
                        return convertirAlumno(nodo);
                    } catch (IOException ex) {
                        throw new CompletionException(ex);
                    }
                });
    }

    /** Elimina exclusivamente un alumno nuevo por su UUID interno. */
    public CompletableFuture<Void> eliminarAlumno(String id) {
        if (id == null || id.isBlank() || "—".equals(id)) {
            return CompletableFuture.failedFuture(
                    new IllegalArgumentException("El alumno no tiene un ID válido."));
        }

        HttpRequest request = HttpRequest.newBuilder()
                .uri(URI.create(BASE_URL + "/students/"
                        + URLEncoder.encode(id, StandardCharsets.UTF_8)))
                .timeout(Duration.ofSeconds(20))
                .header("Accept", "application/json")
                .DELETE()
                .build();

        return client.sendAsync(request,
                        HttpResponse.BodyHandlers.ofString(StandardCharsets.UTF_8))
                .thenApply(response -> {
                    int codigo = response.statusCode();
                    if (codigo != 200 && codigo != 202 && codigo != 204) {
                        throw new CompletionException(new IOException(
                                "HTTP " + codigo + ": " + detalleError(response.body())
                        ));
                    }
                    return null;
                });
    }

    /** Genera el mismo JSON para POST y PUT, incluyendo los campos opcionales. */
    private static ObjectNode jsonAlumno(NuevoAlumno alumno) {
        ObjectNode datos = JSON.createObjectNode();
        datos.put("nombre", alumno.nombre());
        datos.put("casa", "Hogwarths");
        campoNulo(datos, "especie", alumno.especie());
        campoNulo(datos, "genero", alumno.genero());
        campoNulo(datos, "nacimiento", alumno.nacimiento());
        campoNulo(datos, "nacionalidad", alumno.nacionalidad());
        campoNulo(datos, "patronus", alumno.patronus());
        campoNulo(datos, "imagen", alumno.imagen());
        // Compatibilidad con el modelo Python si patronus_origen sigue siendo obligatorio.
        datos.put("patronus_origen", alumno.patronus() == null
                ? "No especificado" : "Introducido manualmente");
        return datos;
    }

    private static void campoNulo(ObjectNode nodo, String nombre, String valor) {
        if (valor == null || valor.isBlank()) {
            nodo.putNull(nombre);
        } else {
            nodo.put(nombre, valor.strip());
        }
    }

    private static String detalleError(String cuerpo) {
        try {
            JsonNode error = JSON.readTree(cuerpo);
            if (error != null && error.has("detail")) {
                String mensaje = error.get("detail").toString();
                return mensaje.length() > 600 ? mensaje.substring(0, 600) + "..." : mensaje;
            }
        } catch (Exception ignored) { }
        return cuerpo.length() > 400 ? cuerpo.substring(0, 400) + "..." : cuerpo;
    }

    private Student convertirAlumno(JsonNode nodo) {
        return new Student(
                campo(nodo, "id"), campo(nodo, "nombre"),
                campo(nodo, "casa"), campo(nodo, "especie"),
                campo(nodo, "genero"), campo(nodo, "nacimiento"),
                campo(nodo, "nacionalidad"), campo(nodo, "patronus"),
                campoOpcional(nodo, "imagen")
        );
    }

    private List<Student> convertirAlumnos(String contenido) throws IOException {
        JsonNode raiz = JSON.readTree(contenido);
        if (raiz == null || !raiz.isArray()) {
            throw new IOException("La API no devolvió una lista JSON de alumnos.");
        }

        List<Student> resultado = new ArrayList<>();
        for (JsonNode nodo : raiz) {
            resultado.add(convertirAlumno(nodo));
        }
        return resultado;
    }

    private static String campo(JsonNode nodo, String nombreCampo) {
        JsonNode valor = nodo.path(nombreCampo);
        if (valor.isMissingNode() || valor.isNull()) {
            return "—";
        }
        String texto = valor.asText().strip();
        return texto.isEmpty() ? "—" : texto;
    }

    /** Devuelve null si la API no incluye una URL de imagen utilizable. */
    private static String campoOpcional(JsonNode nodo, String nombreCampo) {
        JsonNode valor = nodo.path(nombreCampo);
        if (valor.isMissingNode() || valor.isNull()) {
            return null;
        }
        String texto = valor.asText().strip();
        return texto.isEmpty() ? null : texto;
    }

}
