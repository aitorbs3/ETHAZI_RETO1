package com.dm2.myapplication.data

import androidx.room.Dao
import androidx.room.Insert
import androidx.room.OnConflictStrategy
import androidx.room.Query

/**
 * Data Access Object (DAO) de Room para interactuar con la tabla 'students_table' en SQLite.
 */
@Dao
interface StudentDao {

    /**
     * Busca y retorna un estudiante guardado en la base de datos local por su ID.
     */
    @Query("SELECT * FROM students_table WHERE id = :studentId")
    suspend fun getStudentById(studentId: String): StudentEntity?

    /**
     * NUEVO: Busca y retorna un estudiante guardado en la base de datos local por su nombre.
     */
    @Query("SELECT * FROM students_table WHERE name LIKE '%' || :studentName || '%' LIMIT 1")
    suspend fun getStudentByName(studentName: String): StudentEntity?

    /** Devuelve TODAS las coincidencias locales, sin perder homónimos. */
    @Query("SELECT * FROM students_table WHERE LOWER(name) LIKE '%' || LOWER(:studentName) || '%' ORDER BY name COLLATE NOCASE")
    suspend fun getStudentsByName(studentName: String): List<StudentEntity>

    /**
     * Inserta un nuevo estudiante o reemplaza el existente si ya consta en la base de datos (REPLACE).
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertStudent(student: StudentEntity)
}