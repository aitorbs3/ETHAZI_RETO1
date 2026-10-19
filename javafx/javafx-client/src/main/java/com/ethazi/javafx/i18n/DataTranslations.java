package com.ethazi.javafx.i18n;

import java.text.Normalizer;
import java.util.Locale;
import java.util.ResourceBundle;

/**
 * Traduce solamente los valores mostrados en JavaFX.
 * NO modifica Student ni los datos enviados a FastAPI.
 * Si falta una traducción, conserva el valor original.
 */
public final class DataTranslations {

    private DataTranslations() { }

    public static String species(String valor) {
        return translate("species", valor);
    }

    public static String gender(String valor) {
        return translate("gender", valor);
    }

    public static String nationality(String valor) {
        return translate("nationality", valor);
    }

    public static String patronus(String valor) {
        return translate("patronus", valor);
    }

    public static String translate(String field, String valor) {
        if (valor == null || valor.isBlank() || "—".equals(valor.strip())) {
            return valor == null ? "—" : valor;
        }

        String key = field + "." + normalize(valor);
        if (key.endsWith(".")) {
            return valor;
        }

        Locale locale = Locale.forLanguageTag(I18n.language());
        ResourceBundle values = ResourceBundle.getBundle("i18n.data", locale);
        return values.containsKey(key) ? values.getString(key) : valor;
    }

    /** La normalización sirve solo para localizar claves, nunca para guardar datos. */
    private static String normalize(String value) {
        String text = Normalizer.normalize(
                value.strip().toLowerCase(Locale.ROOT), Normalizer.Form.NFD);
        text = text.replaceAll("\\p{M}+", "");
        return text.replaceAll("[^a-z0-9]+", "_")
                .replaceAll("^_+|_+$", "");
    }
}
