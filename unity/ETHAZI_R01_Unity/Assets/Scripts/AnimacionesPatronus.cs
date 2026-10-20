
using System.Collections; // Permite utilizar corrutinas para ejecutar acciones durante varios fotogramas.
using UnityEngine; // Incluye las funciones y herramientas principales de Unity.
using UnityEngine.UI; // Permite trabajar con elementos de interfaz, como Image.

// Exige que el objeto tenga un componente Image.
// Si no lo tiene, Unity lo añade automáticamente.
[RequireComponent(typeof(Image))]
public class AnimacionPatronus : MonoBehaviour
{
    [Header("Color mágico")]
    // Define el color del Patronus: azul claro y completamente opaco.
    // Los valores representan rojo, verde, azul y transparencia (alfa).
    [SerializeField] private Color colorPatronus =
        new Color(0.20f, 0.75f, 1f, 1f);

    [Header("Aparición")]
    // Tiempo que tarda el Patronus en aparecer completamente.
    [SerializeField] private float duracionEntrada = 1f;

    // Escala inicial del Patronus antes de alcanzar su tamaño normal.
    [SerializeField] private float escalaInicial = 0.65f;

    [Header("Movimiento")]
    // Distancia máxima que sube y baja el Patronus al flotar.
    [SerializeField] private float amplitudFlotacion = 12f;

    // Controla la velocidad del movimiento de flotación.
    [SerializeField] private float velocidadFlotacion = 1.5f;

    [Header("Brillo")]
    // Controla cuánto varía la intensidad del pulso de luminosidad.
    [SerializeField] private float intensidadPulso = 0.18f;

    // Controla la velocidad con la que cambia el brillo.
    [SerializeField] private float velocidadPulso = 2f;

    // Referencia al componente Image del objeto.
    private Image imagen;

    // Permite modificar la posición y la escala del elemento de interfaz.
    private RectTransform rectTransform;

    // Sprite creado por el script para generar el resplandor.
    private Sprite spriteGenerado;

    // Textura que contiene los píxeles del resplandor.
    private Texture2D texturaGenerada;

    // Guarda la posición original para que la flotación no acumule desplazamientos.
    private Vector2 posicionInicial;

    // Guarda la escala original del objeto.
    private Vector3 escalaFinal;

    // Acumula el tiempo necesario para calcular la animación.
    private float tiempo;

    // Guarda la corrutina de entrada para poder detenerla si es necesario.
    private Coroutine entrada;

    // Se ejecuta cuando Unity inicializa el objeto.
    private void Awake()
    {
        // Obtiene los componentes del propio objeto.
        imagen = GetComponent<Image>();
        rectTransform = GetComponent<RectTransform>();

        // Guarda la posición y la escala iniciales.
        posicionInicial = rectTransform.anchoredPosition;
        escalaFinal = rectTransform.localScale;

        // Genera una textura circular con transparencia.
        CrearResplandor();

        // Asigna el sprite generado al componente Image.
        imagen.sprite = spriteGenerado;

        // Aplica el color configurado en el Inspector.
        imagen.color = colorPatronus;

        // Evita deformar la imagen al cambiar el tamaño del objeto.
        imagen.preserveAspect = true;

        // Impide que el resplandor bloquee los clics de la interfaz.
        imagen.raycastTarget = false;
    }

    // Se ejecuta cada vez que el objeto se activa.
    private void OnEnable()
    {
        // Si la imagen todavía no está inicializada, no continúa.
        if (imagen == null)
            return;

        // Reinicia el tiempo de la animación.
        tiempo = 0f;

        // Detiene una animación de entrada anterior, si sigue ejecutándose.
        if (entrada != null)
            StopCoroutine(entrada);

        // Inicia la animación de aparición.
        entrada = StartCoroutine(Aparecer());
    }

    // Hace que el Patronus aparezca gradualmente.
    private IEnumerator Aparecer()
    {
        // Activa la imagen para que pueda visualizarse.
        imagen.enabled = true;

        // Comienza con un tamaño reducido.
        rectTransform.localScale = escalaFinal * escalaInicial;

        // Establece inicialmente la transparencia a cero.
        Color color = colorPatronus;
        color.a = 0f;
        imagen.color = color;

        // Controla cuánto tiempo ha pasado desde el inicio.
        float transcurrido = 0f;

        // Repite la animación hasta completar su duración.
        while (transcurrido < duracionEntrada)
        {
            // Suma el tiempo real transcurrido, incluso si el juego está pausado.
            transcurrido += Time.unscaledDeltaTime;

            // Calcula el progreso entre 0 y 1.
            // Evita dividir entre cero si la duración no es positiva.
            float progreso = duracionEntrada > 0f
                ? Mathf.Clamp01(transcurrido / duracionEntrada)
                : 1f;

            // Suaviza la transición para evitar una aparición brusca.
            float suave = progreso * progreso * (3f - 2f * progreso);

            // Aumenta progresivamente la opacidad.
            color = colorPatronus;
            color.a = suave;
            imagen.color = color;

            // Amplía progresivamente el Patronus hasta su tamaño original.
            rectTransform.localScale = Vector3.Lerp(
                escalaFinal * escalaInicial,
                escalaFinal,
                suave
            );

            // Espera al siguiente fotograma antes de continuar.
            yield return null;
        }

        // Garantiza que la imagen termine completamente visible.
        color = colorPatronus;
        color.a = 1f;
        imagen.color = color;

        // Restaura el tamaño original.
        rectTransform.localScale = escalaFinal;

        // Indica que la corrutina de entrada ha terminado.
        entrada = null;
    }

    // Se ejecuta una vez por fotograma mientras el componente está activo.
    private void Update()
    {
        // No hace nada si el componente está desactivado o no hay imagen.
        if (!isActiveAndEnabled || imagen == null)
            return;

        // Actualiza el tiempo de la animación.
        tiempo += Time.unscaledDeltaTime;

        // Calcula un movimiento vertical periódico mediante el seno.
        // Esto hace que el Patronus suba y baje suavemente.
        float desplazamiento =
            Mathf.Sin(tiempo * velocidadFlotacion) *
            amplitudFlotacion;

        // Aplica el desplazamiento respecto a la posición original.
        rectTransform.anchoredPosition = posicionInicial +
            new Vector2(0f, desplazamiento);

        // Calcula un pulso de brillo que oscila alrededor de 1.
        float pulso = 1f +
            Mathf.Sin(tiempo * velocidadPulso) *
            intensidadPulso;

        // Actualiza el color y limita la transparencia al rango 0-1.
        Color color = colorPatronus;
        color.a = Mathf.Clamp01(pulso);
        imagen.color = color;
    }

    // Crea una textura circular blanca con los bordes transparentes.
    private void CrearResplandor()
    {
        // Define la resolución de la textura: 128 × 128 píxeles.
        const int tamano = 128;

        // Crea una textura con canales rojo, verde, azul y alfa.
        texturaGenerada = new Texture2D(
            tamano,
            tamano,
            TextureFormat.RGBA32,
            false
        );

        // Asigna un nombre para identificar la textura durante la ejecución.
        texturaGenerada.name = "ResplandorPatronus";

        // Evita que la textura se repita más allá de sus bordes.
        texturaGenerada.wrapMode = TextureWrapMode.Clamp;

        // Suaviza el aspecto de la textura al escalarla.
        texturaGenerada.filterMode = FilterMode.Bilinear;

        // Recorre todas las filas de píxeles de la textura.
        for (int y = 0; y < tamano; y++)
        {
            // Recorre todos los píxeles de cada fila.
            for (int x = 0; x < tamano; x++)
            {
                // Convierte la coordenada X al rango -1 a 1.
                float dx = (x + 0.5f) / tamano * 2f - 1f;

                // Convierte la coordenada Y al rango -1 a 1.
                float dy = (y + 0.5f) / tamano * 2f - 1f;

                // Calcula la distancia del píxel al centro.
                float distancia = Mathf.Sqrt(dx * dx + dy * dy);

                // Calcula la transparencia:
                // el centro es más opaco y los bordes se desvanecen.
                float alpha = Mathf.Pow(
                    Mathf.Clamp01(1f - distancia),
                    2.5f
                );

                // Asigna al píxel el color blanco y la transparencia calculada.
                texturaGenerada.SetPixel(
                    x, y,
                    new Color(1f, 1f, 1f, alpha)
                );
            }
        }

        // Aplica los píxeles calculados a la textura.
        texturaGenerada.Apply();

        // Crea un sprite a partir de la textura.
        // El punto de pivote queda en el centro.
        spriteGenerado = Sprite.Create(
            texturaGenerada,
            new Rect(0, 0, tamano, tamano),
            new Vector2(0.5f, 0.5f)
        );
    }

    // Se ejecuta cuando se destruye el objeto.
    private void OnDestroy()
    {
        // Libera el sprite creado para evitar mantener recursos innecesarios.
        if (spriteGenerado != null)
            Destroy(spriteGenerado);

        // Libera la textura creada por el script.
        if (texturaGenerada != null)
            Destroy(texturaGenerada);
    }
}
