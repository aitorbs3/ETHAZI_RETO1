package com.ethazi.javafx.i18n;

// Permite normalizar cadenas de texto para eliminar diferencias
// relacionadas con los acentos y los caracteres Unicode.
import java.text.Normalizer;

// Proporciona herramientas para trabajar con idiomas y configuraciones regionales.
import java.util.Locale;

// Permite acceder a los archivos de recursos que contienen las traducciones.
import java.util.ResourceBundle;

/**
 * Clase auxiliar encargada de traducir los valores de los datos
 * que se muestran en la interfaz gráfica de JavaFX.
 *
 * Las traducciones afectan únicamente a la presentación visual:
 * no modifican los objetos Student ni los datos enviados a FastAPI.
 *
 * Si un valor no tiene una traducción disponible, se conserva
 * el texto original para evitar perder información.
 */
public final class DataTranslations {

    /**
     * Constructor privado para impedir que se creen objetos de esta clase.
     *
     * Todos sus métodos son estáticos, por lo que se pueden utilizar
     * directamente sin necesidad de instanciar DataTranslations.
     */
    private DataTranslations() { }


    /**
     * Traduce el nombre de una especie al idioma seleccionado.
     *
     * @param valor nombre original de la especie
     * @return nombre traducido o valor original si no existe traducción
     */
    public static String species(String valor) {
        return translate("species", valor);
    }


    /**
     * Traduce el género del alumno al idioma seleccionado.
     *
     * @param valor género original
     * @return género traducido o valor original si no existe traducción
     */
    public static String gender(String valor) {
        return translate("gender", valor);
    }


    /**
     * Traduce la nacionalidad del alumno al idioma seleccionado.
     *
     * @param valor nacionalidad original
     * @return nacionalidad traducida o valor original si no existe traducción
     */
    public static String nationality(String valor) {
        return translate("nationality", valor);
    }


    /**
     * Traduce el patronus del alumno al idioma seleccionado.
     *
     * @param valor nombre original del patronus
     * @return patronus traducido o valor original si no existe traducción
     */
    public static String patronus(String valor) {
        return translate("patronus", valor);
    }


    /**
     * Busca la traducción de un valor dentro del archivo de recursos
     * correspondiente al idioma activo de la aplicación.
     *
     * Construye una clave combinando el campo y el valor normalizado.
     * Por ejemplo, un valor como "Half-Blood" puede convertirse en
     * una clave similar a "species.half_blood".
     *
     * Si el dato está vacío, es nulo o no existe en el archivo de
     * traducciones, se devuelve el valor original.
     *
     * @param field campo al que pertenece el valor que se va a traducir
     * @param valor texto original que se desea traducir
     * @return traducción encontrada o texto original si no existe
     */
    public static String translate(String field, String valor) {

        // Evita intentar traducir valores nulos, vacíos o que representan
        // la ausencia de información mediante un guion largo.
        if (valor == null || valor.isBlank() || "—".equals(valor.strip())) {

            // Sustituye null por un guion largo para mostrar un valor
            // uniforme en la interfaz.
            // Los demás valores se conservan sin modificaciones.
            return valor == null ? "—" : valor;
        }

        // Construye la clave de búsqueda a partir del nombre del campo
        // y del valor normalizado.
        // Ejemplo: field = "gender", valor = "Female"
        // Resultado: "gender.female".
        String key = field + "." + normalize(valor);

        // Si la normalización no genera una clave válida, conserva
        // el texto original en lugar de buscar una traducción inexistente.
        if (key.endsWith(".")) {
            return valor;
        }

        // Obtiene el idioma configurado actualmente en la aplicación
        // y lo convierte en una configuración regional de Java.
        Locale locale = Locale.forLanguageTag(I18n.language());

        // Carga el archivo de recursos i18n.data correspondiente al idioma.
        // Los archivos pueden organizarse, por ejemplo, como:
        // data.properties, data_es.properties, data_en.properties.
        ResourceBundle values = ResourceBundle.getBundle(
                "i18n.data", locale);

        // Comprueba si el archivo contiene una traducción para la clave.
        // Si existe, devuelve el texto traducido; de lo contrario,
        // conserva el valor original recibido.
        return values.containsKey(key)
                ? values.getString(key)
                : valor;
    }


    /**
     * Normaliza un texto para facilitar la búsqueda de su traducción.
     *
     * El proceso:
     * 1. Elimina los espacios exteriores y convierte el texto a minúsculas.
     * 2. Separa los caracteres de sus marcas diacríticas.
     * 3. Elimina las marcas diacríticas, como los acentos.
     * 4. Sustituye los grupos de caracteres no alfanuméricos por guiones bajos.
     * 5. Elimina los guiones bajos situados al principio o al final.
     *
     * La normalización solo se utiliza para generar claves de búsqueda.
     * Nunca se emplea para modificar ni guardar los datos originales.
     *
     * @param value texto que se desea normalizar
     * @return texto normalizado que puede utilizarse como clave
     */
    private static String normalize(String value) {

        // Elimina los espacios exteriores, convierte el texto a minúsculas
        // y separa los caracteres acentuados de sus marcas diacríticas.
        String text = Normalizer.normalize(
                value.strip().toLowerCase(Locale.ROOT),
                Normalizer.Form.NFD);

        // Elimina las marcas diacríticas, como los acentos gráficos.
        // Por ejemplo, "águila" pasa a "aguila".
        text = text.replaceAll("\\p{M}+", "");

        // Sustituye los caracteres que no sean letras ASCII o números
        // por guiones bajos y elimina los guiones sobrantes de los extremos.
        // Por ejemplo, "Half-Blood" pasa a "half_blood".
        return text.replaceAll("[^a-z0-9]+", "_")
                .replaceAll("^_+|_+$", "");
    }
}