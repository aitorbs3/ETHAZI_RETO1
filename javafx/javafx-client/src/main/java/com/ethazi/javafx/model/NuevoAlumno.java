package com.ethazi.javafx.model;

/**
 * Representa los datos de un alumno que se van a enviar desde el formulario
 * de la aplicación JavaFX al backend para crear un nuevo registro.
 *
 * Contiene los campos necesarios para dar de alta al alumno.
 * El identificador (ID) no se incluye porque lo genera automáticamente
 * el backend FastAPI.
 *
 * Al ser un record de Java, sus atributos son finales y dispone
 * automáticamente de un constructor, métodos de acceso, equals(),
 * hashCode() y toString().
 *
 * @param nombre       nombre del alumno
 * @param casa         casa de Hogwarts a la que pertenece
 * @param especie      especie del alumno
 * @param genero       género del alumno
 * @param nacimiento   fecha de nacimiento del alumno
 * @param nacionalidad nacionalidad del alumno
 * @param patronus     tipo de Patronus del alumno
 * @param imagen       ruta o URL de la imagen del alumno
 */
public record NuevoAlumno(
        String nombre,
        String casa,
        String especie,
        String genero,
        String nacimiento,
        String nacionalidad,
        String patronus,
        String imagen
) { }