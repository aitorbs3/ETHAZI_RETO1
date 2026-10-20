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

    /** Informa si existe al menos un alumno guardado para uso sin conexión. */
    @Query("SELECT EXISTS(SELECT 1 FROM students_table)")
    suspend fun hasCachedStudents(): Boolean

    /**
     * Inserta un nuevo estudiante o reemplaza el existente si ya consta en la base de datos (REPLACE).
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertStudent(student: StudentEntity)
}