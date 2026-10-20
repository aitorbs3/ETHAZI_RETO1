package com.ethazi.javafx.i18n;

import java.text.MessageFormat;
import java.util.Locale;
import java.util.ResourceBundle;
import java.util.prefs.Preferences;

/** Idiomas de la interfaz; no traduce los valores enviados a FastAPI. */
public final class I18n {
    private static final Preferences PREFS = Preferences.userNodeForPackage(I18n.class);
    private static final String LANGUAGE_KEY = "app.language";
    private static Locale locale = fromCode(PREFS.get(LANGUAGE_KEY, "es"));

    static {
        Locale.setDefault(locale);
    }

    private I18n() { }

    private static Locale fromCode(String code) {
        if ("eu".equals(code)) return Locale.forLanguageTag("eu-ES");
        if ("en".equals(code)) return Locale.forLanguageTag("en-GB");
        return Locale.forLanguageTag("es-ES");
    }

    public static String language() {
        return locale.getLanguage();
    }

    public static void changeLanguage(String languageCode) {
        locale = fromCode(languageCode);
        Locale.setDefault(locale);
        PREFS.put(LANGUAGE_KEY, locale.getLanguage());
    }

    public static ResourceBundle bundle() {
        return ResourceBundle.getBundle("i18n.messages", locale);
    }

    public static String tr(String key, Object... args) {
        String pattern = bundle().getString(key);
        return args.length == 0 ? pattern : new MessageFormat(pattern, locale).format(args);
    }
}
