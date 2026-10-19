
using System; // Permite utilizar Action y DateTime.
using TMPro; // Permite trabajar con textos de TextMeshPro.
using UnityEngine; // Incluye las funciones básicas de Unity.
using UnityEngine.UI; // Permite utilizar componentes de interfaz, como Button.

public class AlumnoItemUI : MonoBehaviour
{
    // Organiza las variables en el Inspector de Unity.
    [Header("Nombre del alumno")]
    // Referencia al texto donde se muestra el nombre del alumno.
    [SerializeField] private TMP_Text nombreText;

    [Header("Fila 1: casa, especie y género")]
    // Referencias a los textos que muestran estos tres datos.
    [SerializeField] private TMP_Text textoCasa;
    [SerializeField] private TMP_Text textoEspecie;
    [SerializeField] private TMP_Text textoGenero;

    [Header("Fila 2: nacimiento, nacionalidad y patronus")]
    // Referencias a los textos de la segunda fila.
    [SerializeField] private TMP_Text textoNacimiento;
    [SerializeField] private TMP_Text textoNacionalidad;
    [SerializeField] private TMP_Text textoPatronus;

    [Header("Botón de la tarjeta")]
    // Referencia al botón que permite seleccionar al alumno.
    [SerializeField] private Button boton;

    // Guarda el alumno cuyos datos se muestran en esta tarjeta.
    private Student alumno;

    // Configura la tarjeta con los datos de un estudiante.
    // estudiante: contiene la información del alumno.
    // alSeleccionar: función que se ejecutará cuando se pulse la tarjeta.
    public void Configurar(
        Student estudiante,
        Action<Student> alSeleccionar)
    {
        // Guarda el estudiante recibido para utilizarlo después.
        alumno = estudiante;

        // Si no existe un estudiante, vacía los campos y termina.
        if (alumno == null)
        {
            LimpiarCampos();
            return;
        }

        // Comprueba que cada referencia exista antes de modificarla.
        // Texto() evita mostrar valores vacíos o espacios en blanco.
        if (nombreText != null)
            nombreText.text = Texto(alumno.nombre);

        if (textoCasa != null)
            textoCasa.text = Texto(alumno.casa);

        if (textoEspecie != null)
            textoEspecie.text = Texto(alumno.especie);

        if (textoGenero != null)
            textoGenero.text = Texto(alumno.genero);

        // Convierte la fecha de nacimiento al formato yyyy-MM-dd.
        if (textoNacimiento != null)
            textoNacimiento.text =
                FormatearNacimiento(alumno.nacimiento);

        if (textoNacionalidad != null)
            textoNacionalidad.text = Texto(alumno.nacionalidad);

        if (textoPatronus != null)
            textoPatronus.text = Texto(alumno.patronus);

        // Configura el comportamiento del botón si existe.
        if (boton != null)
        {
            // Elimina los eventos anteriores para evitar
            // que se acumulen acciones al reutilizar la tarjeta.
            boton.onClick.RemoveAllListeners();

            // Añade una acción que se ejecuta al pulsar el botón.
            // Envía el alumno guardado a la función recibida.
            // ?. evita invocar la función si es null.
            boton.onClick.AddListener(
                () => alSeleccionar?.Invoke(alumno)
            );
        }
    }

    // Devuelve el texto recibido limpio.
    // Si está vacío, es null o solo contiene espacios,
    // devuelve "No registrado".
    private string Texto(string valor)
    {
        if (string.IsNullOrWhiteSpace(valor))
            return "No registrado";

        // Trim() elimina espacios al principio y al final.
        return valor.Trim();
    }

    // Intenta convertir una fecha al formato yyyy-MM-dd.
    private string FormatearNacimiento(string valor)
    {
        // Si no hay fecha, indica que no está registrada.
        if (string.IsNullOrWhiteSpace(valor))
            return "No registrado";

        // Intenta interpretar el texto como una fecha válida.
        // Si funciona, la devuelve como año-mes-día.
        if (DateTime.TryParse(valor, out DateTime fecha))
            return fecha.ToString("yyyy-MM-dd");

        // Si no puede interpretarla como fecha,
        // devuelve el valor original sin espacios exteriores.
        return valor.Trim();
    }

    // Vacía todos los textos cuando no hay ningún alumno.
    private void LimpiarCampos()
    {
        if (nombreText != null) nombreText.text = "";
        if (textoCasa != null) textoCasa.text = "";
        if (textoEspecie != null) textoEspecie.text = "";
        if (textoGenero != null) textoGenero.text = "";
        if (textoNacimiento != null) textoNacimiento.text = "";
        if (textoNacionalidad != null) textoNacionalidad.text = "";
        if (textoPatronus != null) textoPatronus.text = "";
    }
}
