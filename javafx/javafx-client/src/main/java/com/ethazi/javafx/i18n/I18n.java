package com.ethazi.javafx.i18n;

// Permite insertar valores dinámicos dentro de los mensajes traducidos.
import java.text.MessageFormat;

// Permite representar y configurar el idioma y la región de la aplicación.
import java.util.Locale;

// Permite cargar los archivos de traducciones de la interfaz.
import java.util.ResourceBundle;

// Permite guardar preferencias del usuario entre distintas ejecuciones.
import java.util.prefs.Preferences;

/**
 * Gestiona el idioma de la interfaz gráfica de la aplicación JavaFX.
 *
 * Permite recuperar el idioma seleccionado, cambiarlo durante la ejecución
 * y obtener los mensajes traducidos desde los archivos de recursos.
 *
 * Los cambios afectan a los textos de la interfaz, pero no modifican los
 * valores originales de los datos enviados al backend FastAPI.
 */
public final class I18n {

    // Obtiene el almacenamiento de preferencias asociado a esta clase.
    // Se utiliza para recordar el idioma elegido por el usuario.
    private static final Preferences PREFS =
            Preferences.userNodeForPackage(I18n.class);

    // Clave con la que se guarda y recupera el idioma en las preferencias.
    private static final String LANGUAGE_KEY = "app.language";

    // Idioma activo de la aplicación.
    // Se inicializa recuperando el idioma guardado; si no existe,
    // se utiliza el español como idioma predeterminado.
    private static Locale locale = fromCode(PREFS.get(LANGUAGE_KEY, "es"));

    // Bloque estático que se ejecuta una sola vez cuando se carga la clase.
    static {
        // Establece el idioma activo como configuración regional predeterminada
        // de la aplicación, para que las clases que consulten Locale por defecto
        // utilicen esta configuración.
        Locale.setDefault(locale);
    }

    // Constructor privado para impedir que se creen objetos de esta clase.
    // Todos sus métodos son estáticos, por lo que se utilizan directamente.
    private I18n() { }

    /**
     * Convierte el código de idioma recibido en un objeto Locale.
     *
     * eu -> euskera de España.
     * en -> inglés de Reino Unido.
     * Cualquier otro código -> español de España.
     *
     * @param code código del idioma seleccionado
     * @return configuración regional correspondiente al idioma
     */
    private static Locale fromCode(String code) {
        if ("eu".equals(code)) return Locale.forLanguageTag("eu-ES");
        if ("en".equals(code)) return Locale.forLanguageTag("en-GB");
        return Locale.forLanguageTag("es-ES");
    }

    /**
     * Devuelve el código del idioma que está activo.
     *
     * Por ejemplo, devuelve "es", "eu" o "en".
     *
     * @return código del idioma actual
     */
    public static String language() {
        return locale.getLanguage();
    }

    /**
     * Cambia el idioma activo de la aplicación y guarda la selección.
     *
     * Primero convierte el código recibido en un Locale y actualiza
     * la configuración regional predeterminada. Después guarda el código
     * del idioma en las preferencias para conservarlo al volver a abrir
     * la aplicación.
     *
     * @param languageCode código del idioma que se quiere activar
     */
    public static void changeLanguage(String languageCode) {
        // Actualiza el idioma utilizado por esta clase.
        locale = fromCode(languageCode);

        // Actualiza la configuración regional predeterminada de Java.
        Locale.setDefault(locale);

        // Guarda el idioma seleccionado para futuras ejecuciones.
        PREFS.put(LANGUAGE_KEY, locale.getLanguage());
    }

    /**
     * Carga y devuelve el archivo de traducciones de la interfaz.
     *
     * Busca los mensajes en el conjunto de recursos "i18n.messages"
     * utilizando el idioma actualmente seleccionado.
     *
     * Los archivos de recursos deben seguir la estructura de nombres
     * correspondiente a ResourceBundle, por ejemplo:
     * messages_es.properties, messages_eu.properties y messages_en.properties.
     *
     * @return conjunto de mensajes traducidos para el idioma activo
     */
    public static ResourceBundle bundle() {
        return ResourceBundle.getBundle("i18n.messages", locale);
    }

    /**
     * Obtiene un mensaje traducido a partir de su clave.
     *
     * Si se proporcionan argumentos adicionales, los inserta en el mensaje
     * mediante MessageFormat. Esto permite construir textos dinámicos,
     * como saludos personalizados o mensajes que incluyen cantidades.
     *
     * Ejemplo:
     * tr("welcome", "Carlos")
     *
     * Si el mensaje asociado a "welcome" fuera "Bienvenido, {0}",
     * el resultado sería "Bienvenido, Carlos".
     *
     * @param key clave del mensaje que se quiere recuperar
     * @param args valores que se insertarán en el mensaje, si los hay
     * @return mensaje traducido, con los argumentos aplicados cuando proceda
     */
    public static String tr(String key, Object... args) {
        // Recupera el texto correspondiente a la clave en el idioma activo.
        String pattern = bundle().getString(key);

        // Si no hay argumentos, devuelve el texto directamente.
        // Si los hay, sustituye los marcadores de MessageFormat por sus valores.
        return args.length == 0
                ? pattern
                : new MessageFormat(pattern, locale).format(args);
    }
}