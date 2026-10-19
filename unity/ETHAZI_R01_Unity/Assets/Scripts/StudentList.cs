using System;

// Permite que la clase StudentList pueda serializarse
// para almacenar o procesar sus datos.
[Serializable]
public class StudentList
{
    // Array que contiene los objetos Student
    // correspondientes a los alumnos recibidos.
    public Student[] estudiantes;
}