package com.dm2.myapplication

// Permite acceder a las preferencias locales de Android para guardar
// y recuperar el idioma seleccionado por el usuario.
import android.content.Context

// Permite gestionar los idiomas y las configuraciones regionales
// de la aplicación mediante AppCompat.
import androidx.appcompat.app.AppCompatDelegate

// Permite crear listas de idiomas compatibles con AndroidX.
import androidx.core.os.LocaleListCompat

/**
 * Gestor del idioma de la aplicación.
 *
 * Permite seleccionar entre español, euskera e inglés y conservar
 * la preferencia del usuario entre ejecuciones.
 *
 * Solo traduce los textos de la interfaz de usuario.
 * Los datos obtenidos de las bases de datos no se traducen ni modifican.
 */
object LanguageManager {

    // Códigos de idioma que admite la aplicación:
    // es = español, eu = euskera, en = inglés.
    val languageTags = listOf("es", "eu", "en")

    // Nombres de los idiomas que se muestran al usuario
    // en el selector de idioma de la aplicación.
    val languageLabels = listOf("Español", "Euskara", "English")

    // Nombre del archivo de preferencias donde se guarda el idioma.
    private const val PREFS = "hogwarts_language"

    // Clave utilizada para almacenar el idioma seleccionado.
    private const val KEY = "language"

    /**
     * Recupera el idioma seleccionado por el usuario.
     *
     * Si no existe una preferencia guardada o el código almacenado
     * no está entre los idiomas admitidos, devuelve español.
     */
    fun selected(context: Context): String =
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            // Lee el idioma guardado; si no existe, utiliza "es".
            .getString(KEY, "es")
            // Comprueba que el idioma pertenezca a la lista permitida.
            ?.takeIf { it in languageTags }
            // Si el valor es null o no es válido, utiliza español.
            ?: "es"

    /**
     * Aplica el idioma guardado al iniciar o configurar la aplicación.
     *
     * Solo actualiza la configuración regional si el idioma aplicado
     * actualmente es diferente del idioma seleccionado.
     */
    fun applySaved(context: Context) {

        // Recupera el idioma guardado en las preferencias.
        val tag = selected(context)

        // Compara el idioma guardado con los idiomas aplicados
        // actualmente a la aplicación.
        if (AppCompatDelegate.getApplicationLocales()
                .toLanguageTags() != tag
        ) {

            // Aplica el idioma guardado mediante AppCompat.
            // AndroidX puede actualizar los recursos de texto
            // para mostrar la traducción correspondiente.
            AppCompatDelegate.setApplicationLocales(
                LocaleListCompat.forLanguageTags(tag)
            )
        }
    }

    /**
     * Cambia el idioma de la aplicación.
     *
     * Si el idioma no está admitido o ya está seleccionado,
     * no realiza ninguna operación.
     */
    fun choose(context: Context, tag: String) {

        // Comprueba que el idioma sea válido y que sea diferente
        // del idioma que ya está seleccionado.
        if (tag !in languageTags || selected(context) == tag) return

        // Guarda el nuevo idioma en las preferencias locales.
        // apply() aplica el cambio de forma asíncrona.
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit()
            .putString(KEY, tag)
            .apply()

        // Aplica el nuevo idioma a la configuración regional
        // de la aplicación mediante AppCompat.
        AppCompatDelegate.setApplicationLocales(
            LocaleListCompat.forLanguageTags(tag)
        )
    }
}