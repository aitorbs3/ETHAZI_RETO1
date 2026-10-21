package com.dm2.myapplication.data

// Importa el modelo Student, que representa los datos de un estudiante.
import com.dm2.myapplication.model.Student

// Permite definir peticiones HTTP GET a los endpoints de la API.
import retrofit2.http.GET

// Permite introducir valores en los parámetros de la ruta de una URL.
import retrofit2.http.Path

// Permite enviar parámetros de consulta en la URL.
import retrofit2.http.Query

/**
 * Interfaz de Retrofit que define las peticiones HTTP
 * a la API REST desarrollada con FastAPI.
 *
 * Retrofit utiliza estas definiciones para generar automáticamente
 * las llamadas al servidor.
 */
interface StudentApiService {

    /**
     * Comprueba si la API está respondiendo correctamente.
     *
     * Realiza una petición GET al endpoint /health.
     * Devuelve un objeto Response que permite consultar el estado
     * HTTP de la respuesta y acceder a su contenido.
     */
    @GET("health")
    suspend fun getHealth(): retrofit2.Response<okhttp3.ResponseBody>

    /**
     * Obtiene una lista de estudiantes desde la API.
     *
     * El parámetro nombre permite filtrar los resultados.
     * Si es null, no se envía el parámetro de búsqueda.
     *
     * Por ejemplo:
     * /students?nombre=Harry
     *
     * Devuelve una lista de objetos Student.
     */
    @GET("students")
    suspend fun getStudents(
        // @Query añade el nombre como parámetro de consulta a la URL.
        // El valor predeterminado null permite omitir el filtro.
        @Query("nombre") nombre: String? = null
    ): List<Student>

    /**
     * Busca estudiantes directamente en un conector específico.
     *
     * Permite consultar una fuente de datos determinada sin limitar
     * la búsqueda a los resultados almacenados previamente en caché.
     */
    @GET("connectors/{connector}/students/{nombre}")
    suspend fun getStudentsFromConnector(

        // Sustituye {connector} por el nombre del conector seleccionado.
        // Por ejemplo: derby, h2 u oracle, según los admitidos por la API.
        @Path("connector") connector: String,

        // Sustituye {nombre} por el nombre del estudiante que se busca.
        @Path("nombre") nombre: String

    ): List<Student>

    /**
     * Obtiene un estudiante concreto a partir de su identificador.
     *
     * Realiza una petición GET al endpoint /students/{id}.
     * Devuelve un objeto Student con los datos del estudiante.
     */
    @GET("students/{id}")
    suspend fun getStudentById(

        // Sustituye {id} por el identificador del estudiante.
        @Path("id") id: String

    ): Student
}