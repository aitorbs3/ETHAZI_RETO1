
using System; // Permite utilizar excepciones y el atributo Serializable.
using System.Collections; // Permite crear corrutinas para realizar tareas asíncronas.
using TMPro; // Permite trabajar con campos de texto de TextMeshPro.
using UnityEngine; // Incluye las funciones principales de Unity.
using UnityEngine.Networking; // Permite realizar peticiones HTTP a la API.
using UnityEngine.UI; // Permite trabajar con botones de la interfaz.

public class ApiManager : MonoBehaviour
{
    // Dirección base de la API FastAPI.
    // 127.0.0.1 hace referencia al propio dispositivo donde se ejecuta Unity.
    private const string BaseUrl = "http://127.0.0.1:8000";

    // Tiempo que espera después de escribir antes de iniciar la búsqueda.
    // Evita realizar una petición por cada tecla pulsada.
    private const float PausaBusqueda = 0.5f;

    // Tiempo máximo de espera de una petición HTTP, en segundos.
    private const int TimeoutSegundos = 30;

    [Header("Buscador")]
    // Campo donde el usuario introduce el nombre del alumno.
    [SerializeField] private TMP_InputField nombreInput;

    // Panel que contiene el buscador y la lista de resultados.
    [SerializeField] private GameObject searchPanel;

    // Contenedor donde se crean las tarjetas de los alumnos encontrados.
    [SerializeField] private Transform resultadosContent;

    // Prefab que sirve como plantilla para crear cada tarjeta de alumno.
    [SerializeField] private AlumnoItemUI alumnoItemPrefab;

    [Header("Ficha del alumno")]
    // Panel que muestra la información del alumno seleccionado.
    [SerializeField] private GameObject detailPanel;

    // Texto donde aparece el nombre del alumno seleccionado.
    [SerializeField] private TMP_Text nombreAlumnoText;

    // Texto donde aparece el nombre de su Patronus.
    [SerializeField] private TMP_Text nombreAnimalText;

    // Botón que permite volver al buscador.
    [SerializeField] private Button volverButton;

    [Header("Animaciones de Patronus")]
    // Selector que activa la animación correspondiente al Patronus.
    [SerializeField]
    private PatronusAnimationSelector patronusAnimationSelector;

    // Guarda la corrutina que espera antes de buscar.
    private Coroutine busquedaCoroutine;

    // Guarda la petición HTTP que se está ejecutando actualmente.
    private UnityWebRequest peticionActual;

    // Almacena el último texto introducido para identificar
    // si una respuesta pertenece a la búsqueda más reciente.
    private string ultimaBusqueda = "";

    // Se ejecuta al iniciar el componente.
    private void Start()
    {
        // Muestra el panel del buscador al comenzar.
        if (searchPanel != null)
            searchPanel.SetActive(true);

        // Oculta la ficha del alumno al comenzar.
        if (detailPanel != null)
            detailPanel.SetActive(false);

        // Escucha los cambios de texto para iniciar las búsquedas.
        if (nombreInput != null)
            nombreInput.onValueChanged.AddListener(AlCambiarTexto);
        else
            // Avisa si falta configurar el campo en el Inspector.
            Debug.LogError(
                "Falta asignar NombreInput en el Inspector."
            );

        // Asocia el botón Volver con el método que regresa al buscador.
        if (volverButton != null)
            volverButton.onClick.AddListener(VolverAlBuscador);

        // Avisa si no se ha asignado el selector de animaciones.
        if (patronusAnimationSelector == null)
        {
            Debug.LogWarning(
                "Falta asignar PatronusAnimationSelector " +
                "en el Inspector de ApiManager."
            );
        }
    }

    // Se ejecuta cuando se destruye este objeto.
    private void OnDestroy()
    {
        // Elimina el evento del campo de búsqueda para evitar
        // que siga apuntando a este componente.
        if (nombreInput != null)
            nombreInput.onValueChanged.RemoveListener(AlCambiarTexto);

        // Elimina el evento del botón Volver.
        if (volverButton != null)
            volverButton.onClick.RemoveListener(VolverAlBuscador);

        // Si hay una petición HTTP activa, intenta cancelarla.
        if (peticionActual != null)
        {
            peticionActual.Abort();
            peticionActual = null;
        }
    }

    // Se ejecuta cada vez que cambia el texto del buscador.
    private void AlCambiarTexto(string texto)
    {
        // Guarda el texto sin espacios al principio ni al final.
        ultimaBusqueda = texto.Trim();

        // Cancela la espera de una búsqueda anterior.
        if (busquedaCoroutine != null)
        {
            StopCoroutine(busquedaCoroutine);
            busquedaCoroutine = null;
        }

        // Exige al menos dos caracteres para iniciar una búsqueda.
        // Si hay menos, elimina las tarjetas mostradas y termina.
        if (ultimaBusqueda.Length < 2)
        {
            BorrarResultados();
            return;
        }

        // Inicia una espera antes de consultar la API.
        busquedaCoroutine =
            StartCoroutine(BuscarConPausa(ultimaBusqueda));
    }

    // Espera antes de realizar la petición para reducir
    // el número de consultas mientras el usuario escribe.
    private IEnumerator BuscarConPausa(string nombre)
    {
        // Espera medio segundo antes de buscar.
        yield return new WaitForSeconds(PausaBusqueda);

        // Indica que la corrutina de espera ha terminado.
        busquedaCoroutine = null;

        // Si el usuario ha cambiado el texto durante la espera,
        // o hay menos de dos caracteres, cancela esta búsqueda.
        if (nombre != ultimaBusqueda || nombre.Length < 2)
            yield break;

        // Inicia la petición para obtener los alumnos coincidentes.
        yield return BuscarAlumnos(nombre);
    }

    // Consulta la API y crea una tarjeta por cada alumno encontrado.
    private IEnumerator BuscarAlumnos(string nombre)
    {
        // Construye la URL del endpoint /students.
        // EscapeURL codifica caracteres especiales del nombre
        // para que puedan enviarse correctamente en la URL.
        string url = BaseUrl + "/students?nombre=" +
                     UnityWebRequest.EscapeURL(nombre);

        // Crea una petición GET y garantiza su liberación al terminar.
        using (UnityWebRequest request = UnityWebRequest.Get(url))
        {
            // Establece el tiempo máximo de espera.
            request.timeout = TimeoutSegundos;

            // Guarda la referencia a la petición actual.
            peticionActual = request;

            // Envía la petición y espera la respuesta de la API.
            yield return request.SendWebRequest();

            // Ignora la respuesta si el usuario ya ha escrito
            // un nombre diferente mientras se procesaba la petición.
            if (nombre != ultimaBusqueda)
            {
                if (peticionActual == request)
                    peticionActual = null;

                yield break;
            }

            // Comprueba si la petición ha fallado.
            if (request.result != UnityWebRequest.Result.Success)
            {
                // Muestra el error y la URL en la consola de Unity.
                Debug.LogError(
                    "Error al buscar '" + nombre + "': " +
                    request.error + " | URL: " + url
                );

                if (peticionActual == request)
                    peticionActual = null;

                yield break;
            }

            try
            {
                // Convierte la respuesta JSON de la API
                // en un array de objetos Student.
                Student[] alumnos =
                    JsonArrayHelper.FromJson<Student>(
                        request.downloadHandler.text
                    );

                // Comprueba otra vez que la búsqueda siga siendo válida.
                if (nombre != ultimaBusqueda)
                    yield break;

                // Elimina los resultados anteriores antes de mostrar
                // los correspondientes a la nueva búsqueda.
                BorrarResultados();

                // Si la API no devuelve alumnos, no crea tarjetas.
                if (alumnos == null || alumnos.Length == 0)
                {
                    Debug.Log(
                        "No se encontraron alumnos para: " + nombre
                    );
                    yield break;
                }

                // Recorre todos los alumnos recibidos de la API.
                foreach (Student alumno in alumnos)
                {
                    // Detiene el proceso si el texto ha cambiado.
                    if (nombre != ultimaBusqueda)
                        yield break;

                    // Comprueba que estén asignados los elementos
                    // necesarios para crear las tarjetas.
                    if (alumnoItemPrefab == null ||
                        resultadosContent == null)
                    {
                        Debug.LogError(
                            "Falta asignar AlumnoItemPrefab o " +
                            "ResultadosContent en el Inspector."
                        );
                        yield break;
                    }

                    // Crea una copia del prefab dentro del contenedor.
                    // Cada copia representa un alumno encontrado.
                    AlumnoItemUI fila = Instantiate(
                        alumnoItemPrefab,
                        resultadosContent
                    );

                    // Rellena la tarjeta y configura su selección.
                    // Al pulsarla, se ejecutará SeleccionarAlumno.
                    fila.Configurar(alumno, SeleccionarAlumno);
                }

                // Informa de que la búsqueda ha terminado correctamente.
                Debug.Log(
                    "Búsqueda completada: " + nombre +
                    ". Resultados: " + alumnos.Length
                );
            }
            catch (Exception ex)
            {
                // Captura errores al interpretar el JSON
                // o al procesar los datos recibidos.
                Debug.LogError(
                    "Error al interpretar la respuesta JSON: " +
                    ex.Message
                );
            }
            finally
            {
                // Limpia la referencia únicamente si sigue siendo
                // la petición guardada como actual.
                if (peticionActual == request)
                    peticionActual = null;
            }
        }
    }

    // Elimina todas las tarjetas de alumnos del contenedor.
    private void BorrarResultados()
    {
        // Si no existe el contenedor, no hay nada que borrar.
        if (resultadosContent == null)
            return;

        // Recorre los elementos desde el último hasta el primero.
        for (int i = resultadosContent.childCount - 1; i >= 0; i--)
        {
            // Programa la destrucción de cada tarjeta.
            Destroy(resultadosContent.GetChild(i).gameObject);
        }
    }

    // Se ejecuta cuando el usuario selecciona una tarjeta de alumno.
    private void SeleccionarAlumno(Student alumno)
    {
        // Si el alumno es nulo, no continúa.
        if (alumno == null)
            return;

        // Oculta el buscador.
        if (searchPanel != null)
            searchPanel.SetActive(false);

        // Muestra la ficha del alumno seleccionado.
        if (detailPanel != null)
            detailPanel.SetActive(true);

        // Muestra el nombre del alumno.
        if (nombreAlumnoText != null)
            nombreAlumnoText.text = alumno.nombre;

        // Muestra el Patronus o un mensaje si no está registrado.
        if (nombreAnimalText != null)
        {
            nombreAnimalText.text =
                string.IsNullOrWhiteSpace(alumno.patronus)
                    ? "Patronus no registrado"
                    : alumno.patronus;
        }

        // Activa la animación correspondiente al Patronus.
        if (patronusAnimationSelector != null)
        {
            patronusAnimationSelector.MostrarPatronus(
                alumno.patronus
            );
        }

        // Registra en la consola qué alumno se ha seleccionado.
        Debug.Log("Alumno seleccionado: " + alumno.nombre);
    }

    // Cierra la ficha y regresa al buscador.
    private void VolverAlBuscador()
    {
        // Oculta la ficha del alumno.
        if (detailPanel != null)
            detailPanel.SetActive(false);

        // Oculta todas las animaciones de Patronus.
        if (patronusAnimationSelector != null)
            patronusAnimationSelector.OcultarTodas();

        // Vuelve a mostrar el buscador.
        if (searchPanel != null)
            searchPanel.SetActive(true);
    }
}

// Ayudante para convertir un array JSON en un array de objetos C#.
// JsonUtility de Unity necesita un objeto contenedor para procesar arrays.
public static class JsonArrayHelper
{
    // Clase genérica que contiene un array de cualquier tipo T.
    // Serializable permite que JsonUtility la procese.
    [Serializable]
    private class Wrapper<T>
    {
        // Campo donde se almacenan los elementos del array JSON.
        public T[] items;
    }

    // Convierte un array JSON en un array de objetos del tipo indicado.
    public static T[] FromJson<T>(string json)
    {
        // Envuelve el array recibido en un objeto JSON con la propiedad
        // "items", que es compatible con JsonUtility.
        string wrapped = "{\"items\":" + json + "}";

        // Convierte el JSON envuelto en una instancia de Wrapper<T>.
        Wrapper<T> resultado =
            JsonUtility.FromJson<Wrapper<T>>(wrapped);

        // Devuelve el array si la conversión ha funcionado;
        // de lo contrario, devuelve null.
        return resultado != null ? resultado.items : null;
    }
}
