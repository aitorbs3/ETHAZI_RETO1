package com.dm2.myapplication.data

// Anotación que permite definir una clase como entidad de Room,
// es decir, como una tabla dentro de la base de datos SQLite.
import androidx.room.Entity

// Anotación que identifica la clave primaria de la tabla.
import androidx.room.PrimaryKey

/**
 * Entidad de Room que representa la estructura de la tabla
 * students_table en la base de datos SQLite local.
 *
 * Cada objeto StudentEntity representa un registro de estudiante.
 */
@Entity(tableName = "students_table")
data class StudentEntity(

    // Identificador único del estudiante.
    // Se utiliza como clave primaria para distinguir cada registro.
    @PrimaryKey val id: String,

    // Nombre del estudiante.
    val name: String,

    // Alias o apodo del estudiante.
    // El símbolo ? indica que el campo puede contener null.
    val alias: String?,

    // Casa de Hogwarts a la que pertenece el estudiante.
    // Puede ser null si no se dispone de esta información.
    val house: String?,

    // Especie del estudiante, por ejemplo, humano.
    // Puede ser null si el dato no está disponible.
    val species: String?,

    // Género del estudiante.
    // Puede ser null si no se dispone del dato.
    val gender: String?,

    // Fecha de nacimiento del estudiante, almacenada como texto.
    // Puede ser null si no está disponible.
    val dateOfBirth: String?,

    // Nacionalidad del estudiante.
    // Puede ser null si no se conoce.
    val nationality: String?,

    // Patronus asociado al estudiante.
    // Puede ser null si no tiene uno registrado.
    val patronus: String?,

    // URL de la imagen del estudiante.
    // Puede ser null si no existe una imagen disponible.
    val imageUrl: String?,

    // Nombre de la base de datos de origen de la que proceden los datos.
    // Este campo es obligatorio y no admite null.
    val sourceDatabase: String
)