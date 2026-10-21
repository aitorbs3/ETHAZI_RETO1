package com.dm2.myapplication.data

// Importa Context para acceder a las preferencias locales de Android
// y guardar la configuración de la URL de la API.
import android.content.Context

// Cliente HTTP encargado de realizar las peticiones a la API.
import okhttp3.OkHttpClient

// Permite configurar Retrofit para comunicarse con la API REST.
import retrofit2.Retrofit

// Convierte automáticamente las respuestas JSON en objetos Kotlin.
import retrofit2.converter.gson.GsonConverterFactory

// Permite analizar y validar la estructura de una URL.
import java.net.URI

// Permite definir los tiempos máximos de espera de las peticiones.
import java.util.concurrent.TimeUnit

/**
 * Objeto que centraliza la configuración y creación del cliente de la API.
 *
 * Al ser un object, Kotlin crea una única instancia compartida.
 * Permite configurar la URL del servidor, guardar esa configuración
 * y crear el servicio que realiza las peticiones relacionadas con estudiantes.
 */
object ApiClient {

    // Nombre del archivo de preferencias donde se guarda la configuración.
    private const val PREFS_NAME = "hogwarts_server_settings"

    // Clave utilizada para almacenar la URL base de la API.
    private const val PREF_URL = "api_base_url"

    // URL predeterminada del servidor.
    // En un emulador Android, 127.0.0.1 apunta al propio emulador.
    // Para acceder al servidor del ordenador mediante esta dirección,
    // se puede utilizar adb reverse tcp:8000 tcp:8000.
    private const val DEFAULT_URL = "http://127.0.0.1:8000/"

    // Cliente HTTP compartido para realizar las peticiones.
    // by lazy hace que se cree únicamente cuando se utiliza por primera vez.
    private val httpClient: OkHttpClient by lazy {

        // Construye y configura el cliente HTTP.
        OkHttpClient.Builder()

            // Tiempo máximo de espera para establecer la conexión.
            .connectTimeout(20, TimeUnit.SECONDS)

            // Tiempo máximo de espera para recibir datos del servidor.
            .readTimeout(30, TimeUnit.SECONDS)

            // Tiempo máximo total permitido para una petición completa.
            .callTimeout(45, TimeUnit.SECONDS)

            // Permite reintentar automáticamente ante determinados
            // fallos de conexión recuperables.
            .retryOnConnectionFailure(true)

            // Finaliza la configuración y crea el cliente HTTP.
            .build()
    }

    // Obtiene la URL base de la API guardada en las preferencias.
    // Si todavía no existe una URL guardada, devuelve la predeterminada.
    fun baseUrl(context: Context): String =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(PREF_URL, DEFAULT_URL) ?: DEFAULT_URL

    /**
     * Valida y normaliza la URL base de la API.
     *
     * Solo acepta direcciones HTTP o HTTPS sin rutas adicionales,
     * parámetros ni fragmentos.
     */
    fun normalizeBaseUrl(value: String): String {

        // Elimina los espacios al principio y al final de la URL.
        val raw = value.trim()

        // Intenta interpretar el texto como una URI.
        // Si el formato es incorrecto, muestra un error comprensible.
        val uri = try {
            URI(raw)
        } catch (e: Exception) {
            throw IllegalArgumentException(
                "Introduce una URL válida, por ejemplo http://10.0.2.2:8000/"
            )
        }

        // Comprueba que la URL cumpla las condiciones permitidas:
        // - El protocolo debe ser HTTP o HTTPS.
        // - Debe incluir un nombre de host válido.
        // - No puede contener credenciales de usuario.
        // - No puede incluir parámetros de consulta ni fragmentos.
        // - Solo puede tener la ruta vacía o "/".
        // - El puerto no puede superar el máximo permitido.
        if ((uri.scheme != "http" && uri.scheme != "https") ||
            uri.host.isNullOrBlank() || uri.userInfo != null ||
            uri.query != null || uri.fragment != null ||
            (uri.path.isNotEmpty() && uri.path != "/") ||
            uri.port > 65535
        ) {
            // Si alguna condición falla, rechaza la URL.
            throw IllegalArgumentException(
                "Usa una URL base como http://10.0.2.2:8000/"
            )
        }

        // Elimina las barras finales y añade exactamente una.
        // Retrofit necesita que la URL base termine en "/".
        return raw.trimEnd('/') + "/"
    }

    // Valida la URL recibida y guarda el resultado normalizado
    // en las preferencias locales de Android.
    fun saveBaseUrl(context: Context, value: String) {

        // Comprueba que la URL sea válida antes de guardarla.
        val normalized = normalizeBaseUrl(value)

        // Accede a las preferencias y guarda la URL con su clave.
        // apply() aplica el cambio de forma asíncrona.
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit()
            .putString(PREF_URL, normalized)
            .apply()
    }

    // Crea y devuelve el servicio que permite realizar las peticiones
    // relacionadas con estudiantes definidas en StudentApiService.
    fun studentService(context: Context): StudentApiService =

        // Configura Retrofit utilizando la URL guardada.
        Retrofit.Builder()

            // Establece la dirección base del servidor.
            .baseUrl(baseUrl(context))

            // Utiliza el cliente HTTP configurado anteriormente,
            // con sus tiempos de espera y política de reintentos.
            .client(httpClient)

            // Añade el conversor que transforma JSON en objetos Kotlin.
            .addConverterFactory(GsonConverterFactory.create())

            // Construye la instancia de Retrofit.
            .build()

            // Genera una implementación de la interfaz StudentApiService.
            .create(StudentApiService::class.java)
}