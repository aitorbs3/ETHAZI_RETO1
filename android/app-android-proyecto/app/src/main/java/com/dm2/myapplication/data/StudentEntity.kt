package com.dm2.myapplication.data

import androidx.room.Entity
import androidx.room.PrimaryKey

/**
 * Entidad de base de datos de Room que representa la estructura de la tabla 'students_table' en SQLite.
 */
@Entity(tableName = "students_table")
data class StudentEntity(
    @PrimaryKey val id: String,
    val name: String,
    val alias: String?,
    val house: String?,
    val species: String?,
    val gender: String?,
    val dateOfBirth: String?,
    val nationality: String?,
    val patronus: String?,
    val imageUrl: String?,
    val sourceDatabase: String
)