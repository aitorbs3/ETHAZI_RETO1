package com.dm2.myapplication.repository

// Importa el servicio de Retrofit que permite consultar la API REST.
import com.dm2.myapplication.data.StudentApiService

// Importa el DAO que permite acceder a la base de datos SQLite local.
import com.dm2.myapplication.data.StudentDao

// Importa la entidad que representa un estudiante almacenado localmente.
import com.dm2.myapplication.data.StudentEntity

// Importa el modelo de estudiante recibido desde la API.
import com.dm2.myapplication.model.Student

// Permite introducir una pausa antes de volver a intentar una petición.
import kotlinx.coroutines.delay

// Excepción que puede producirse cuando no se consigue establecer
// una conexión con el servidor.
import java.net.ConnectException

// Excepción que puede producirse cuando una operación supera
// el tiempo máximo de espera.
import java.net.SocketTimeoutException

// Excepción personalizada para indicar que no se ha encontrado
// el estudiante solicitado.
class StudentNotFoundException(query: String) :
    Exception("Alumno no encontrado: $query")

/**
 * Repositorio encargado de gestionar las consultas de estudiantes.
 *
 * Consulta primero la base de datos local Room y, cuando necesita
 * obtener datos actualizados o no dispone de un registro adecuado,
 * recurre a la API REST.
 *
 * También transforma los datos recibidos del servidor en entidades
 * que pueden almacenarse en la caché local.
 */
class StudentRepository(

    // Servicio que permite realizar las peticiones HTTP a FastAPI.
    private val apiService: StudentApiService,

    // DAO que permite consultar e insertar estudiantes en Room.
    private val studentDao: StudentDao,

) {

    /**
     * Busca un estudiante utilizando su identificador o su nombre.
     *
     * Primero consulta la caché local. Si no encuentra un registro
     * adecuado, realiza una petición a la API.
     *
     * Si existe un registro local y falla la petición remota,
     * puede devolver los datos guardados para mantener el acceso
     * sin conexión.
     */
    suspend fun getStudent(query: String): StudentEntity {

        // Elimina los espacios al principio y al final de la búsqueda.
        val trimmed = query.trim()

        // Comprueba que el usuario haya introducido algún dato.
        // Si la cadena está vacía, lanza una excepción con un mensaje claro.
        require(trimmed.isNotEmpty()) {
            "Introduce el nombre o ID del alumno"
        }

        // Busca primero por identificador en la base de datos local.
        // Si no encuentra el estudiante y la consulta no tiene formato UUID,
        // intenta localizarlo mediante su nombre.
        val cached = studentDao.getStudentById(trimmed)
            ?: if (!UUID_REGEX.matches(trimmed)) {
                studentDao.getStudentByName(trimmed)
            } else {
                null
            }

        // Las versiones anteriores de la aplicación pueden tener registros
        // sin URL de imagen. Si el registro tiene imagen, se devuelve
        // directamente sin realizar una nueva petición HTTP.
        if (cached != null && !cached.imageUrl.isNullOrBlank()) {
            return cached
        }

        // Si la consulta tiene formato UUID, se busca exactamente
        // ese estudiante por su identificador.
        // Si contiene un nombre, se utiliza el endpoint de búsqueda.
        val remote = try {

            // Ejecuta la petición remota con un único reintento
            // ante los errores de conexión contemplados más abajo.
            withOneNetworkRetry {

                if (UUID_REGEX.matches(trimmed)) {

                    // Consulta al estudiante mediante su identificador.
                    try {
                        apiService.getStudentById(trimmed)

                    } catch (e: retrofit2.HttpException) {

                        // Si el servidor responde con HTTP 404,
                        // transforma el error en una excepción propia
                        // para indicar que el estudiante no existe.
                        if (e.code() == 404) {
                            throw StudentNotFoundException(trimmed)
                        } else {
                            // Los demás errores HTTP se propagan.
                            throw e
                        }
                    }

                } else {

                    // Busca estudiantes por nombre y obtiene el primero.
                    // Si la API no devuelve resultados, indica que no existe
                    // un estudiante que coincida con la consulta.
                    apiService.getStudents(nombre = trimmed).firstOrNull()
                        ?: throw StudentNotFoundException(trimmed)
                }
            }

        } catch (e: Exception) {

            // Si falla la petición y existe una copia local,
            // devuelve esa copia para permitir el uso sin conexión.
            if (cached != null) return cached

            // Si tampoco hay datos locales disponibles,
            // propaga el error para que otra capa lo gestione.
            throw e
        }

        // Convierte el estudiante recibido de la API en una entidad,
        // lo guarda en Room y devuelve el registro almacenado.
        return cacheStudent(remote)
    }

    /**
     * Convierte un estudiante recibido desde la API en una entidad
     * de Room y lo guarda en la base de datos local.
     *
     * Permite reutilizar la misma operación de almacenamiento
     * independientemente del endpoint que haya devuelto los datos.
     */
    suspend fun cacheStudent(remote: Student): StudentEntity {

        // Construye la entidad que se almacenará en SQLite.
        val entity = StudentEntity(

            // Comprueba que la API haya proporcionado un identificador.
            // Si está vacío, no se puede guardar el estudiante correctamente.
            id = remote.id.takeIf { it.isNotBlank() }
                ?: throw IllegalStateException(
                    "La API devolvió un alumno sin 'id'"
                ),

            // Convierte un nombre nulo en una cadena vacía.
            name = remote.name.orEmpty(),

            // Copia el alias del estudiante.
            alias = remote.alias,

            // Copia la casa de Hogwarts.
            house = remote.house,

            // Copia la especie.
            species = remote.species,

            // Copia el género.
            gender = remote.gender,

            // Copia la fecha de nacimiento.
            dateOfBirth = remote.dateOfBirth,

            // Copia la nacionalidad.
            nationality = remote.nationality,

            // Copia el Patronus.
            patronus = remote.patronus,

            // Limpia los espacios de la URL y acepta únicamente
            // direcciones que comiencen por HTTP o HTTPS.
            // Si la URL no cumple la condición, guarda null.
            imageUrl = remote.imagen?.trim()?.takeIf {
                it.startsWith("https://") ||
                    it.startsWith("http://")
            },

            // Copia la base de datos de origen.
            // Si el valor es null, utiliza una cadena vacía.
            sourceDatabase = remote.sourceDatabase.orEmpty(),
        )

        // Inserta el estudiante en Room.
        // Según la configuración del DAO, si existe un registro
        // con la misma clave primaria, se reemplaza.
        studentDao.insertStudent(entity)

        // Devuelve la entidad que se acaba de guardar.
        return entity
    }

    /**
     * Ejecuta una operación de red y permite un reintento
     * cuando se produce un timeout o un error de conexión.
     */
    private suspend fun <T> withOneNetworkRetry(
        action: suspend () -> T
    ): T {

        return try {

            // Intenta ejecutar la petición por primera vez.
            action()

        } catch (e: SocketTimeoutException) {

            // Si se supera el tiempo de espera, pausa 400 milisegundos.
            delay(400)

            // Vuelve a ejecutar la petición una sola vez.
            action()

        } catch (e: ConnectException) {

            // Si falla el establecimiento de la conexión,
            // espera 400 milisegundos antes de volver a intentarlo.
            delay(400)

            // Realiza el segundo intento.
            action()
        }
    }

    // Agrupa los elementos privados asociados al repositorio.
    private companion object {

        // Expresión regular que comprueba el formato UUID:
        // cinco grupos hexadecimales separados por guiones,
        // con longitudes de 8-4-4-4-12 caracteres.
        // Se admiten letras hexadecimales en mayúsculas o minúsculas.
        val UUID_REGEX = Regex(
            "^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$"
        )
    }
}