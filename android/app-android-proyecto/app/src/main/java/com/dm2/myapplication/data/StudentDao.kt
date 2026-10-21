package com.dm2.myapplication.data

// Anotación que identifica la interfaz como un DAO de Room.
import androidx.room.Dao

// Permite insertar entidades en la base de datos.
import androidx.room.Insert

// Define qué hacer cuando se intenta insertar un registro que ya existe.
import androidx.room.OnConflictStrategy

// Permite ejecutar consultas SQL directamente sobre SQLite.
import androidx.room.Query

/**
 * DAO (Data Access Object) de Room.
 *
 * Define las operaciones para consultar e insertar estudiantes
 * en la tabla students_table de la base de datos SQLite local.
 */
@Dao
interface StudentDao {

    /**
     * Busca un estudiante por su identificador en la base de datos local.
     *
     * Si encuentra un registro, devuelve su entidad StudentEntity.
     * Si no existe, devuelve null.
     */
    @Query("SELECT * FROM students_table WHERE id = :studentId")
    suspend fun getStudentById(studentId: String): StudentEntity?

    /**
     * Busca un estudiante cuyo nombre contenga el texto indicado.
     *
     * LIKE permite buscar coincidencias parciales.
     * Los símbolos % permiten que existan caracteres antes y después
     * del nombre buscado.
     * LIMIT 1 hace que se devuelva como máximo un resultado.
     *
     * Si no encuentra coincidencias, devuelve null.
     */
    @Query("SELECT * FROM students_table WHERE name LIKE '%' || :studentName || '%' LIMIT 1")
    suspend fun getStudentByName(studentName: String): StudentEntity?

    /**
     * Comprueba si existe al menos un estudiante almacenado
     * en la base de datos local.
     *
     * Devuelve true si hay registros y false si la tabla está vacía.
     * Esta comprobación puede utilizarse para saber si hay datos
     * disponibles localmente cuando no existe conexión a Internet.
     */
    @Query("SELECT EXISTS(SELECT 1 FROM students_table)")
    suspend fun hasCachedStudents(): Boolean

    /**
     * Inserta un estudiante en la base de datos local.
     *
     * Si ya existe un registro con la misma clave primaria,
     * OnConflictStrategy.REPLACE sustituye el registro existente
     * por los nuevos datos.
     */
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insertStudent(student: StudentEntity)
}