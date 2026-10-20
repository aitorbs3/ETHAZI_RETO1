
using UnityEngine;

/// <summary>
/// Mantiene la cámara en una proporción 16:9.
/// Si la pantalla tiene otra proporción, aparecen bandas
/// negras en lugar de deformar la interfaz.
/// </summary>
[RequireComponent(typeof(Camera))]
public class MantenerAspectRatio : MonoBehaviour
{
    private const float AspectRatioObjetivo = 16f / 9f;

    private Camera camara;

    private void Awake()
    {
        camara = GetComponent<Camera>();
        AjustarCamara();
    }

    private void OnPreCull()
    {
        AjustarCamara();
    }

    private void AjustarCamara()
    {
        if (camara == null)
            return;

        float proporcionPantalla =
            (float)Screen.width / Screen.height;

        // La pantalla es más ancha que 16:9:
        // añadimos bandas a los lados.
        if (proporcionPantalla > AspectRatioObjetivo)
        {
            float ancho = AspectRatioObjetivo / proporcionPantalla;

            camara.rect = new Rect(
                (1f - ancho) / 2f,
                0f,
                ancho,
                1f
            );
        }
        // La pantalla es más estrecha que 16:9:
        // añadimos bandas arriba y abajo.
        else
        {
            float alto = proporcionPantalla / AspectRatioObjetivo;

            camara.rect = new Rect(
                0f,
                (1f - alto) / 2f,
                1f,
                alto
            );
        }

        camara.ResetAspect();
    }
}
