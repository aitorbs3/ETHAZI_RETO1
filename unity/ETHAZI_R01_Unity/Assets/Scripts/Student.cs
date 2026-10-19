
using System;

// Permite que la clase Student pueda serializarse,
// por ejemplo, para convertir datos JSON en objetos de C#.
[Serializable]
public class Student
{
    // Identificador único del alumno.
    public string id;

    // Nombre del alumno.
    public string nombre;

    // Casa de Hogwarts a la que pertenece.
    public string casa;

    // Especie o tipo de ser al que pertenece.
    public string especie;

    // Género del alumno.
    public string genero;

    // Fecha de nacimiento del alumno.
    // Se almacena como texto, no como una fecha de tipo DateTime.
    public string nacimiento;

    // Nacionalidad del alumno.
    public string nacionalidad;

    // Patronus del alumno, por ejemplo, un ciervo o una nutria.
    public string patronus;
}


