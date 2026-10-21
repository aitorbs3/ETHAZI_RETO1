package com.dm2.myapplication.model

// Permite indicar qué nombre tiene un campo en el JSON recibido
// y definir nombres alternativos para ese mismo campo.
import com.google.gson.annotations.SerializedName

/**
 * Modelo de datos que representa a un estudiante recibido
 * desde la API REST desarrollada con FastAPI.
 *
 * Gson utiliza las anotaciones para convertir automáticamente
 * los datos JSON en un objeto Student.
 */
data class Student(

    // Identificador del estudiante.
    // Se corresponde con el campo "id" del JSON.
    // Si no se proporciona un valor al crear el objeto, utiliza "".
    @SerializedName("id")
    val id: String = "",

    // Nombre del estudiante.
    // Acepta tanto "nombre" como "name" en el JSON.
    // Es nullable, por lo que puede contener null.
    // Su valor predeterminado es una cadena vacía.
    @SerializedName("nombre", alternate = ["name"])
    val name: String? = "",

    // Alias o apodo del estudiante.
    // Se corresponde con el campo "alias".
    // Si no aparece en el JSON, su valor predeterminado es null.
    @SerializedName("alias")
    val alias: String? = null,

    // Casa de Hogwarts a la que pertenece el estudiante.
    // Acepta los campos "casa" o "house".
    @SerializedName("casa", alternate = ["house"])
    val house: String? = null,

    // Especie del estudiante.
    // Acepta los campos "especie" o "species".
    @SerializedName("especie", alternate = ["species"])
    val species: String? = null,

    // Género del estudiante.
    // Acepta los campos "genero" o "gender".
    @SerializedName("genero", alternate = ["gender"])
    val gender: String? = null,

    // Fecha de nacimiento del estudiante.
    // Acepta varios nombres posibles para el campo en el JSON:
    // "nacimiento", "dateOfBirth", "date_of_birth" o "birth".
    @SerializedName(
        "nacimiento",
        alternate = ["dateOfBirth", "date_of_birth", "birth"]
    )
    val dateOfBirth: String? = null,

    // Nacionalidad del estudiante.
    // Acepta los campos "nacionalidad" o "nationality".
    @SerializedName("nacionalidad", alternate = ["nationality"])
    val nationality: String? = null,

    // Patronus asociado al estudiante.
    // Se corresponde con el campo "patronus".
    @SerializedName("patronus")
    val patronus: String? = null,

    // URL o dirección de la imagen del estudiante.
    // Se corresponde con el campo "imagen".
    @SerializedName("imagen")
    val imagen: String? = null,

    // Identifica la base de datos de origen del estudiante.
    // Acepta los campos "sourceDatabase", "source_database" o "source".
    // Si no se proporciona, utiliza el valor predeterminado indicado.
    @SerializedName(
        "sourceDatabase",
        alternate = ["source_database", "source"]
    )
    val sourceDatabase: String? = "Hogwarts Main Database",
)