package com.ethazi.javafx.model;

/**
 * Datos de un alumno recibidos desde FastAPI.
 * El identificador se conserva internamente, aunque no se muestre en la tabla.
 * La imagen se muestra en la ficha del alumno, no como columna.
 */
public class Student {
    private final String id;
    private final String nombre;
    private final String casa;
    private final String especie;
    private final String genero;
    private final String fechaNacimiento;
    private final String nacionalidad;
    private final String patronus;
    private final String imagen;

    public Student(String id, String nombre, String casa, String especie,
                   String genero, String fechaNacimiento, String nacionalidad,
                   String patronus, String imagen) {
        this.id = id;
        this.nombre = nombre;
        this.casa = casa;
        this.especie = especie;
        this.genero = genero;
        this.fechaNacimiento = fechaNacimiento;
        this.nacionalidad = nacionalidad;
        this.patronus = patronus;
        this.imagen = imagen;
    }

    public String getId() { return id; }
    public String getNombre() { return nombre; }
    public String getCasa() { return casa; }
    public String getEspecie() { return especie; }
    public String getGenero() { return genero; }
    public String getFechaNacimiento() { return fechaNacimiento; }
    public String getNacionalidad() { return nacionalidad; }
    public String getPatronus() { return patronus; }
    public String getImagen() { return imagen; }
}
