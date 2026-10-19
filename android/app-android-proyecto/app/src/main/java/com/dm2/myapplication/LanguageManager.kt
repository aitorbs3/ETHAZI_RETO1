package com.dm2.myapplication

import android.content.Context
import androidx.appcompat.app.AppCompatDelegate
import androidx.core.os.LocaleListCompat

/** Traduce exclusivamente la interfaz; nunca los datos de las bases de datos. */
object LanguageManager {
    val languageTags = listOf("es", "eu", "en")
    val languageLabels = listOf("Español", "Euskara", "English")
    private const val PREFS = "hogwarts_language"
    private const val KEY = "language"

    fun selected(context: Context): String = context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
        .getString(KEY, "es")?.takeIf { it in languageTags } ?: "es"

    fun applySaved(context: Context) {
        val tag = selected(context)
        if (AppCompatDelegate.getApplicationLocales().toLanguageTags() != tag) {
            AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(tag))
        }
    }

    fun choose(context: Context, tag: String) {
        if (tag !in languageTags || selected(context) == tag) return
        context.getSharedPreferences(PREFS, Context.MODE_PRIVATE)
            .edit().putString(KEY, tag).apply()
        AppCompatDelegate.setApplicationLocales(LocaleListCompat.forLanguageTags(tag))
    }
}
