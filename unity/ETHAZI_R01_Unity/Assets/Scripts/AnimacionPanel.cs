
using System.Collections; // Permite utilizar corrutinas para ejecutar animaciones a lo largo del tiempo.
using UnityEngine; // Incluye las clases y funciones principales de Unity.

public class AnimacionPanel : MonoBehaviour
{
    [Header("Referencias")]
    // Referencia al CanvasGroup del panel.
    // Permite controlar su transparencia y la interacción con la interfaz.
    [SerializeField] private CanvasGroup canvasGroup;

    [Header("Animación de entrada")]
    // Duración total de la animación de aparición, en segundos.
    [SerializeField] private float duracionEntrada = 0.6f;

    // Escala con la que comienza el panel.
    // 0.94 significa que empieza al 94 % de su tamaño final.
    [SerializeField] private float escalaInicial = 0.94f;

    // Guarda la corrutina que está ejecutando la animación.
    // Permite detenerla si se inicia otra.
    private Coroutine animacionActual;

    // Guarda la escala original del panel para recuperarla al terminar.
    private Vector3 escalaFinal;

    // Se ejecuta una vez cuando se inicializa el objeto.
    private void Awake()
    {
        // Si no se ha asignado un CanvasGroup desde el Inspector,
        // intenta obtenerlo del mismo objeto.
        if (canvasGroup == null)
            canvasGroup = GetComponent<CanvasGroup>();

        // Guarda la escala actual del panel como escala final.
        escalaFinal = transform.localScale;
    }

    // Se ejecuta cada vez que el panel se activa.
    private void OnEnable()
    {
        // Si el panel no tiene CanvasGroup, no inicia la animación.
        if (canvasGroup == null)
            return;

        // Si ya había una animación en marcha, la detiene.
        if (animacionActual != null)
            StopCoroutine(animacionActual);

        // Inicia la animación de aparición y guarda su referencia.
        animacionActual = StartCoroutine(Aparecer());
    }

    // Activa el panel.
    // Al activarlo, Unity ejecutará OnEnable() y comenzará la animación.
    public void Mostrar()
    {
        gameObject.SetActive(true);
    }

    // Corrutina que hace aparecer el panel gradualmente.
    private IEnumerator Aparecer()
    {
        // Comienza totalmente transparente.
        canvasGroup.alpha = 0f;

        // Comienza ligeramente más pequeño que su tamaño final.
        transform.localScale = escalaFinal * escalaInicial;

        // Lleva la cuenta del tiempo transcurrido.
        float tiempo = 0f;

        // Repite la animación hasta alcanzar la duración configurada.
        while (tiempo < duracionEntrada)
        {
            // Suma el tiempo transcurrido.
            // Time.unscaledDeltaTime permite animar incluso si
            // el juego está pausado mediante Time.timeScale = 0.
            tiempo += Time.unscaledDeltaTime;

            // Calcula el progreso de la animación entre 0 y 1.
            float progreso = Mathf.Clamp01(tiempo / duracionEntrada);

            // Suaviza el movimiento para que la entrada no sea brusca.
            float suave = progreso * progreso * (3f - 2f * progreso);

            // Aumenta la opacidad progresivamente.
            // 0 es transparente y 1 es completamente opaco.
            canvasGroup.alpha = suave;

            // Aumenta el tamaño desde la escala inicial hasta la final.
            transform.localScale = Vector3.Lerp(
                escalaFinal * escalaInicial,
                escalaFinal,
                suave
            );

            // Espera al siguiente fotograma para continuar la animación.
            yield return null;
        }

        // Asegura que el panel termine completamente visible.
        canvasGroup.alpha = 1f;

        // Restablece el tamaño original del panel.
        transform.localScale = escalaFinal;

        // Indica que la animación ha terminado.
        animacionActual = null;
    }
}
