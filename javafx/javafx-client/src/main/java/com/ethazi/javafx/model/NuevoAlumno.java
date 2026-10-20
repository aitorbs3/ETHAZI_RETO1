package com.ethazi.javafx.model;

/** Datos del formulario; el ID lo genera FastAPI. */
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
