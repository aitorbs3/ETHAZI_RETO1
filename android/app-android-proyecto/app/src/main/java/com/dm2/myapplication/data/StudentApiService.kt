package com.dm2.myapplication.data

import com.dm2.myapplication.model.Student
import retrofit2.http.GET
import retrofit2.http.Path
import retrofit2.http.Query

/**
 * Interfaz de Retrofit para definir las llamadas HTTP a la API REST desarrollada en FastAPI.
 */
interface StudentApiService {

    /** Verifica desde la propia app que FastAPI responde. */
    @GET("health")
    suspend fun getHealth(): retrofit2.Response<okhttp3.ResponseBody>


    @GET("students")
    suspend fun getStudents(
        @Query("nombre") nombre: String? = null
    ): List<Student> // Devuelve una lista, ya que el endpoint soporta filtrado por nombre

    /** Buscar también en cada casa, para no limitarse a resultados ya cacheados. */
    @GET("connectors/{connector}/students/{nombre}")
    suspend fun getStudentsFromConnector(
        @Path("connector") connector: String,
        @Path("nombre") nombre: String
    ): List<Student>

    @GET("students/{id}")
    suspend fun getStudentById(
        @Path("id") id: String
    ): Student
}