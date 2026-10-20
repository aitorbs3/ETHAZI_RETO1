
using UnityEngine; // Incluye las herramientas principales de Unity.
using UnityEngine.UI; // Permite utilizar el componente Image de la interfaz.

// Exige que el objeto tenga un RectTransform,
// necesario para calcular las dimensiones y posiciones del marco.
[RequireComponent(typeof(RectTransform))]
public class BrilloContornoUI : MonoBehaviour
{
    [Header("Colores")]
    // Color del primer destello que recorrerá el marco: dorado.
    [SerializeField] private Color dorado =
        new Color(1f, 0.68f, 0.18f, 1f);

    // Color del segundo destello que recorrerá el marco: azul.
    [SerializeField] private Color azul =
        new Color(0.15f, 0.72f, 1f, 1f);

    [Header("Recorrido")]
    // Velocidad a la que avanzan los destellos por el contorno.
    [SerializeField] private float velocidad = 220f;

    // Longitud de cada destello, en unidades de la interfaz.
    [SerializeField] private float longitud = 100f;

    // Grosor de los destellos.
    [SerializeField] private float grosor = 5f;

    // Espacio que se deja libre a izquierda y derecha del marco.
    [SerializeField] private float margenHorizontal = 55f;

    // Espacio que se deja libre arriba y abajo del marco.
    [SerializeField] private float margenVertical = 55f;

    [Header("Suavidad")]
    // Número de píxeles utilizados para generar el degradado.
    // El valor se limita al rango de 16 a 128.
    [SerializeField, Range(16, 128)] private int segmentos = 64;

    // Multiplicador de la opacidad de los destellos.
    // 0 los hace transparentes y 1 mantiene la intensidad normal.
    [SerializeField, Range(0f, 2f)] private float intensidad = 1f;

    [Header("Pulso mágico")]
    // Velocidad con la que cambia la intensidad de los destellos.
    [SerializeField] private float velocidadPulso = 2f;

    // Cantidad máxima de variación de la intensidad durante el pulso.
    [SerializeField, Range(0f, 0.5f)] private float variacionPulso = 0.12f;

    // RectTransform del objeto que sirve como marco de referencia.
    private RectTransform marco;

    // Guarda los RectTransform de los dos destellos.
    private RectTransform[] luces = new RectTransform[2];

    // Guarda las imágenes que representan los destellos.
    private Image[] imagenes = new Image[2];

    // Sprite compartido por los dos destellos.
    private Sprite sprite;

    // Textura generada por código para crear el degradado.
    private Texture2D textura;

    // Distancia recorrida por el destello a lo largo del contorno.
    private float recorrido;

    // Tiempo acumulado para calcular el pulso de intensidad.
    private float fasePulso;

    // Se ejecuta al inicializar el objeto.
    private void Awake()
    {
        // Obtiene las dimensiones del marco desde su RectTransform.
        marco = GetComponent<RectTransform>();

        // Genera la textura con los extremos transparentes.
        CrearTextura();

        // Crea el destello dorado.
        CrearLuz(0, "DestelloDorado", dorado);

        // Crea el destello azul.
        CrearLuz(1, "DestelloAzul", azul);
    }

    // Genera una textura horizontal con un centro luminoso
    // y los extremos transparentes.
    private void CrearTextura()
    {
        // Garantiza que la textura tenga al menos 16 segmentos.
        int cantidad = Mathf.Max(16, segmentos);

        // Crea una textura de cantidad × 1 píxeles,
        // con canales de color y transparencia.
        textura = new Texture2D(
            cantidad, 1, TextureFormat.RGBA32, false
        );

        // Evita que la textura se repita al llegar a sus bordes.
        textura.wrapMode = TextureWrapMode.Clamp;

        // Suaviza la textura al escalarla.
        textura.filterMode = FilterMode.Bilinear;

        // Recorre todos los píxeles horizontales de la textura.
        for (int x = 0; x < cantidad; x++)
        {
            // Convierte la posición del píxel a un valor entre 0 y 1.
            float t = x / (float)(cantidad - 1);

            // Calcula la transparencia mediante una función seno.
            // El centro queda más visible y los extremos desaparecen.
            float alpha = Mathf.Pow(
                Mathf.Sin(t * Mathf.PI), 2f
            );

            // Guarda un píxel blanco con la transparencia calculada.
            // El color definitivo se aplicará después a través de Image.
            textura.SetPixel(x, 0, new Color(1f, 1f, 1f, alpha));
        }

        // Aplica los píxeles calculados a la textura.
        textura.Apply();

        // Crea un sprite utilizando la textura generada.
        // El pivote queda situado en el centro.
        sprite = Sprite.Create(
            textura,
            new Rect(0, 0, cantidad, 1),
            new Vector2(0.5f, 0.5f)
        );
    }

    // Crea uno de los destellos y configura su apariencia inicial.
    // indice: posición que ocupa en los arrays.
    // nombre: nombre que tendrá el objeto en la jerarquía.
    // color: color asignado al destello.
    private void CrearLuz(int indice, string nombre, Color color)
    {
        // Crea un objeto con los componentes necesarios
        // para mostrar una imagen en la interfaz.
        GameObject objeto = new GameObject(
            nombre,
            typeof(RectTransform),
            typeof(CanvasRenderer),
            typeof(Image)
        );

        // Coloca el destello como hijo del objeto que contiene este script.
        // El parámetro false conserva el posicionamiento local de la interfaz.
        objeto.transform.SetParent(transform, false);

        // Guarda la referencia al RectTransform del destello.
        luces[indice] = objeto.GetComponent<RectTransform>();

        // Guarda la referencia al componente Image.
        imagenes[indice] = objeto.GetComponent<Image>();

        // Asigna el degradado creado anteriormente.
        imagenes[indice].sprite = sprite;

        // Establece el color del destello.
        imagenes[indice].color = color;

        // Evita que el destello intercepte clics de la interfaz.
        imagenes[indice].raycastTarget = false;

        // Sitúa los anclajes en el centro del objeto padre.
        luces[indice].anchorMin = new Vector2(0.5f, 0.5f);
        luces[indice].anchorMax = new Vector2(0.5f, 0.5f);

        // Sitúa el pivote del destello en su centro.
        luces[indice].pivot = new Vector2(0.5f, 0.5f);

        // Define la longitud y el grosor iniciales.
        luces[indice].sizeDelta = new Vector2(longitud, grosor);
    }

    // Se ejecuta en cada fotograma mientras el componente está activo.
    private void Update()
    {
        // Si no existe el marco, no puede calcular el recorrido.
        if (marco == null)
            return;

        // Calcula la anchura útil del contorno descontando los márgenes.
        float ancho = marco.rect.width - margenHorizontal * 2f;

        // Calcula la altura útil descontando los márgenes.
        float alto = marco.rect.height - margenVertical * 2f;

        // Si las dimensiones son demasiado pequeñas,
        // evita realizar cálculos con medidas no válidas.
        if (ancho <= 0f || alto <= 0f)
            return;

        // Calcula la longitud total del recorrido rectangular.
        float perimetro = 2f * (ancho + alto);

        // Avanza el destello según la velocidad y el tiempo transcurrido.
        // Repeat hace que vuelva al principio al completar una vuelta.
        recorrido = Mathf.Repeat(
            recorrido + velocidad * Time.deltaTime,
            perimetro
        );

        // Actualiza la fase del pulso de intensidad.
        fasePulso += Time.deltaTime * velocidadPulso;

        // Actualiza los dos destellos.
        for (int i = 0; i < luces.Length; i++)
        {
            // Calcula la posición de cada destello en el recorrido.
            // El segundo comienza desplazado media vuelta respecto al primero.
            float distancia = Mathf.Repeat(
                recorrido - i * perimetro * 0.5f,
                perimetro
            );

            // Obtiene la posición y la orientación correspondientes
            // al punto del contorno donde se encuentra el destello.
            ObtenerPosicion(
                distancia, ancho, alto,
                out Vector2 posicion,
                out float angulo
            );

            // Sitúa el destello en el punto calculado.
            luces[i].anchoredPosition = posicion;

            // Actualiza su longitud y grosor por si se modificaron.
            luces[i].sizeDelta = new Vector2(longitud, grosor);

            // Gira el destello para orientarlo con el lado del marco.
            luces[i].localRotation = Quaternion.Euler(0f, 0f, angulo);

            // Calcula una variación suave de intensidad.
            // El segundo destello tiene una fase opuesta al primero.
            float pulso = 1f + Mathf.Sin(
                fasePulso + i * Mathf.PI
            ) * variacionPulso;

            // Selecciona el color según el destello.
            Color color = i == 0 ? dorado : azul;

            // Ajusta la transparencia combinando la intensidad
            // configurada con el pulso, limitándola entre 0 y 1.
            color.a *= Mathf.Clamp01(intensidad * pulso);

            // Aplica el color y la transparencia a la imagen.
            imagenes[i].color = color;

            // Coloca el destello al final de la lista de hijos,
            // para que aparezca por delante de los demás hijos del marco.
            luces[i].SetAsLastSibling();
        }
    }

    // Calcula la posición y el ángulo de un punto del contorno rectangular.
    // distancia: distancia recorrida desde el inicio del lado superior.
    // ancho y alto: dimensiones útiles del recorrido.
    // posicion: coordenada local que se devuelve.
    // angulo: rotación necesaria para orientar el destello.
    private void ObtenerPosicion(
        float distancia,
        float ancho,
        float alto,
        out Vector2 posicion,
        out float angulo)
    {
        // PRIMER LADO: parte superior, de izquierda a derecha.
        if (distancia < ancho)
        {
            // Calcula la posición horizontal y mantiene la altura superior.
            posicion = new Vector2(
                -ancho / 2f + distancia,
                alto / 2f
            );

            // Orientación horizontal hacia la derecha.
            angulo = 0f;
        }
        // SEGUNDO LADO: parte derecha, de arriba hacia abajo.
        else if (distancia < ancho + alto)
        {
            // Calcula cuánto ha avanzado por el lado derecho.
            float d = distancia - ancho;

            // Mantiene la posición horizontal derecha y baja verticalmente.
            posicion = new Vector2(
                ancho / 2f,
                alto / 2f - d
            );

            // Gira el destello 90 grados en sentido horario.
            angulo = -90f;
        }
        // TERCER LADO: parte inferior, de derecha a izquierda.
        else if (distancia < 2f * ancho + alto)
        {
            // Calcula el avance por el lado inferior.
            float d = distancia - ancho - alto;

            // Se desplaza hacia la izquierda por la parte inferior.
            posicion = new Vector2(
                ancho / 2f - d,
                -alto / 2f
            );

            // Orientación horizontal hacia la izquierda.
            angulo = 180f;
        }
        // CUARTO LADO: parte izquierda, de abajo hacia arriba.
        else
        {
            // Calcula el avance por el lado izquierdo.
            float d = distancia - 2f * ancho - alto;

            // Mantiene la posición horizontal izquierda y sube verticalmente.
            posicion = new Vector2(
                -ancho / 2f,
                -alto / 2f + d
            );

            // Gira el destello 90 grados en sentido antihorario.
            angulo = 90f;
        }
    }

    // Se ejecuta cuando se destruye el objeto.
    private void OnDestroy()
    {
        // Libera el sprite creado por este script.
        if (sprite != null)
            Destroy(sprite);

        // Libera la textura creada para generar el degradado.
        if (textura != null)
            Destroy(textura);
    }
}
