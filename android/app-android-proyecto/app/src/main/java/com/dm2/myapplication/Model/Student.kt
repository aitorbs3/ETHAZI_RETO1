package com.dm2.myapplication.model

import com.google.gson.annotations.SerializedName

/**
 * Modelo de datos que representa a un estudiante recibido desde la API REST de FastAPI.
 */
data class Student(
    @SerializedName("id")
    val id: String = "",

    @SerializedName("nombre", alternate = ["name"])
    val name: String? = "",

    @SerializedName("alias")
    val alias: String? = null,

    @SerializedName("casa", alternate = ["house"])
    val house: String? = null,

    @SerializedName("especie", alternate = ["species"])
    val species: String? = null,

    @SerializedName("genero", alternate = ["gender"])
    val gender: String? = null,

    @SerializedName("nacimiento", alternate = ["dateOfBirth", "date_of_birth", "birth"])
    val dateOfBirth: String? = null,

    @SerializedName("nacionalidad", alternate = ["nationality"])
    val nationality: String? = null,

    @SerializedName("patronus")
    val patronus: String? = null,

    @SerializedName("imagen")
    val imagen: String? = null,

    @SerializedName("sourceDatabase", alternate = ["source_database", "source"])
    val sourceDatabase: String? = "Hogwarts Main Database",
)