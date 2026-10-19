
using System;
using System.Collections.Generic;
using UnityEngine;

public class PatronusAnimationSelector : MonoBehaviour
{
    // Clase que relaciona el nombre de un Patronus
    // con el objeto de Unity que contiene su animación.
    [Serializable]
    public class PatronusAnimation
    {
        // Nombre del Patronus, por ejemplo: "Ciervo".
        public string nombrePatronus;

        // GameObject que contiene la animación correspondiente.
        public GameObject objetoAnimacion;
    }

    [Header("Animaciones de los Patronus")]
    // Lista de Patronus y sus animaciones.
    // Se configura desde el Inspector de Unity.
    [SerializeField]
    private List<PatronusAnimation> animaciones =
        new List<PatronusAnimation>();

    private void Awake()
    {
        // Al iniciar el objeto, oculta todas las animaciones
        // para evitar que aparezcan antes de seleccionar un Patronus.
        OcultarTodas();
    }

    public void MostrarPatronus(string patronus)
    {
        // Indica si se ha encontrado una animación
        // que coincida con el Patronus recibido.
        bool encontrado = false;

        // Recorre todas las animaciones configuradas.
        foreach (PatronusAnimation animacion in animaciones)
        {
            // Si no hay ningún objeto asignado, pasa al siguiente.
            if (animacion.objetoAnimacion == null)
                continue;

            // Comprueba que el nombre recibido no esté vacío
            // y que coincida con el nombre configurado.
            // Trim() elimina espacios al principio y al final.
            // OrdinalIgnoreCase ignora las diferencias entre
            // mayúsculas y minúsculas.
            bool coincide =
                !string.IsNullOrWhiteSpace(patronus) &&
                string.Equals(
                    animacion.nombrePatronus?.Trim(),
                    patronus.Trim(),
                    StringComparison.OrdinalIgnoreCase
                );

            // Activa únicamente la animación cuyo nombre coincide.
            // Las demás animaciones quedan desactivadas.
            animacion.objetoAnimacion.SetActive(coincide);

            // Si hay coincidencia, indica que se ha encontrado.
            if (coincide)
                encontrado = true;
        }

        // Si ningún Patronus coincide con el nombre recibido,
        // muestra un mensaje informativo en la consola de Unity.
        if (!encontrado)
        {
            Debug.Log(
                "No hay animación para el Patronus: " + patronus
            );
        }
    }

    public void OcultarTodas()
    {
        // Recorre la lista de animaciones para ocultarlas todas.
        foreach (PatronusAnimation animacion in animaciones)
        {
            // Comprueba que el objeto esté asignado antes de desactivarlo.
            if (animacion.objetoAnimacion != null)
                animacion.objetoAnimacion.SetActive(false);
        }
    }
}
