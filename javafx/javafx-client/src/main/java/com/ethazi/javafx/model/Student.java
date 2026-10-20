package com.ethazi.javafx.model;

/**
 * Representa a un alumno cuyos datos se han recibido desde el backend FastAPI.
 *
 * Esta clase actúa como modelo de datos dentro de la aplicación JavaFX.
 * Almacena la información de cada alumno para poder mostrarla en la tabla
 * y en su ficha de detalles.
 *
 * El identificador se conserva internamente para poder identificar al alumno
 * en operaciones como la consulta, modificación o eliminación de registros,
 * aunque no se muestre como columna en la tabla.
 *
 * La imagen se utiliza en la ficha de detalles del alumno y no se muestra
 * como una columna más de la tabla.
 */
public class Student {

    // Identificador único del alumno recibido desde el backend.
    // Se utiliza para distinguir los registros y realizar operaciones sobre ellos.
    private final String id;

    // Nombre completo del alumno.
    private final String nombre;

    // Casa de Hogwarts a la que pertenece el alumno.
    private final String casa;

    // Especie a la que pertenece el alumno.
    private final String especie;

    // Género del alumno.
    private final String genero;

    // Fecha de nacimiento del alumno, almacenada como texto.
    private final String fechaNacimiento;

    // Nacionalidad del alumno.
    private final String nacionalidad;

    // Tipo de Patronus asociado al alumno.
    private final String patronus;

    // Ruta o URL de la imagen utilizada en la ficha de detalles.
    private final String imagen;

    /**
     * Constructor que inicializa todos los datos de un alumno.
     *
     * Recibe los valores obtenidos desde FastAPI y los asigna a los atributos
     * correspondientes para crear el objeto Student.
     *
     * @param id              identificador del alumno
     * @param nombre          nombre del alumno
     * @param casa            casa de Hogwarts
     * @param especie         especie del alumno
     * @param genero          género del alumno
     * @param fechaNacimiento fecha de nacimiento
     * @param nacionalidad    nacionalidad del alumno
     * @param patronus        tipo de Patronus
     * @param imagen          ruta o URL de la imagen del alumno
     */
    public Student(String id, String nombre, String casa, String especie,
                   String genero, String fechaNacimiento, String nacionalidad,
                   String patronus, String imagen) {

        // Guarda el identificador recibido en el atributo del objeto.
        this.id = id;

        // Inicializa el nombre del alumno.
        this.nombre = nombre;

        // Inicializa la casa a la que pertenece.
        this.casa = casa;

        // Inicializa la especie del alumno.
        this.especie = especie;

        // Inicializa el género del alumno.
        this.genero = genero;

        // Guarda la fecha de nacimiento recibida.
        this.fechaNacimiento = fechaNacimiento;

        // Inicializa la nacionalidad del alumno.
        this.nacionalidad = nacionalidad;

        // Guarda el tipo de Patronus.
        this.patronus = patronus;

        // Guarda la ruta o URL de la imagen.
        this.imagen = imagen;
    }

    /**
     * Devuelve el identificador del alumno.
     *
     * @return ID del alumno
     */
    public String getId() { return id; }

    /**
     * Devuelve el nombre del alumno.
     *
     * @return nombre del alumno
     */
    public String getNombre() { return nombre; }

    /**
     * Devuelve la casa de Hogwarts del alumno.
     *
     * @return casa del alumno
     */
    public String getCasa() { return casa; }

    /**
     * Devuelve la especie del alumno.
     *
     * @return especie del alumno
     */
    public String getEspecie() { return especie; }

    /**
     * Devuelve el género del alumno.
     *
     * @return género del alumno
     */
    public String getGenero() { return genero; }

    /**
     * Devuelve la fecha de nacimiento del alumno.
     *
     * @return fecha de nacimiento como texto
     */
    public String getFechaNacimiento() { return fechaNacimiento; }

    /**
     * Devuelve la nacionalidad del alumno.
     *
     * @return nacionalidad del alumno
     */
    public String getNacionalidad() { return nacionalidad; }

    /**
     * Devuelve el tipo de Patronus del alumno.
     *
     * @return Patronus del alumno
     */
    public String getPatronus() { return patronus; }

    /**
     * Devuelve la ruta o URL de la imagen del alumno.
     *
     * @return ubicación de la imagen
     */
    public String getImagen() { return imagen; }
}