package com.dm2.myapplication.repository

import com.dm2.myapplication.data.StudentApiService
import com.dm2.myapplication.data.StudentDao
import com.dm2.myapplication.data.StudentEntity
import com.dm2.myapplication.model.Student
import kotlinx.coroutines.delay
import java.net.ConnectException
import java.net.SocketTimeoutException

class StudentNotFoundException(query: String) : Exception("Alumno no encontrado: $query")

/** Consulta primero Room y, si no está, utiliza FastAPI. */
class StudentRepository(
    private val apiService: StudentApiService,
    private val studentDao: StudentDao,
) {
    suspend fun getStudent(query: String): StudentEntity {
        val trimmed = query.trim()
        require(trimmed.isNotEmpty()) { "Introduce el nombre o ID del alumno" }

        val cached = studentDao.getStudentById(trimmed)
            ?: if (!UUID_REGEX.matches(trimmed)) studentDao.getStudentByName(trimmed) else null
        // Priorizar SIEMPRE los datos de Room, incluso si la foto está vacía.
        // La ausencia de foto no debe obligar a usar la red ni demorar el modo offline.
        if (cached != null) return cached

        // La lista de selección pasa un UUID: solicitar exactamente ese alumno.
        // Los nombres se resuelven por búsqueda, pero nunca deben usarse para elegir
        // automáticamente entre resultados duplicados desde la pantalla principal.
        val remote = try {
            withOneNetworkRetry {
            if (UUID_REGEX.matches(trimmed)) {
                try {
                    apiService.getStudentById(trimmed)
                } catch (e: retrofit2.HttpException) {
                    if (e.code() == 404) throw StudentNotFoundException(trimmed) else throw e
                }
            } else {
                apiService.getStudents(nombre = trimmed).firstOrNull()
                    ?: throw StudentNotFoundException(trimmed)
            }
            }
        } catch (e: Exception) {
            if (cached != null) return cached // Conservar modo sin conexión.
            throw e
        }

        return cacheStudent(remote)
    }

    /** Guarda un alumno procedente de cualquier búsqueda HTTP para abrirlo por UUID. */
    suspend fun cacheStudent(remote: Student): StudentEntity {
        val entity = StudentEntity(
            id = remote.id.takeIf { it.isNotBlank() }
                ?: throw IllegalStateException("La API devolvió un alumno sin 'id'"),
            name = remote.name.orEmpty(),
            alias = remote.alias,
            house = remote.house,
            species = remote.species,
            gender = remote.gender,
            dateOfBirth = remote.dateOfBirth,
            nationality = remote.nationality,
            patronus = remote.patronus,
            imageUrl = remote.imagen?.trim()?.takeIf { it.startsWith("https://") || it.startsWith("http://") },
            sourceDatabase = remote.sourceDatabase.orEmpty(),
        )
        studentDao.insertStudent(entity)
        return entity
    }

    private suspend fun <T> withOneNetworkRetry(action: suspend () -> T): T {
        return try {
            action()
        } catch (e: SocketTimeoutException) {
            delay(400)
            action()
        } catch (e: ConnectException) {
            delay(400)
            action()
        }
    }

    private companion object {
        val UUID_REGEX = Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    }
}
