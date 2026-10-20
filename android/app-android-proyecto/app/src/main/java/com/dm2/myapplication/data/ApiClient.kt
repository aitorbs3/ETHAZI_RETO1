package com.dm2.myapplication.data

import android.content.Context
import okhttp3.OkHttpClient
import retrofit2.Retrofit
import retrofit2.converter.gson.GsonConverterFactory
import java.net.URI
import java.util.concurrent.TimeUnit

/** URL configurable. Para 127.0.0.1 en el emulador, activar adb reverse tcp:8000 tcp:8000. */
object ApiClient {
    private const val PREFS_NAME = "hogwarts_server_settings"
    private const val PREF_URL = "api_base_url"
    private const val DEFAULT_URL = "http://127.0.0.1:8000/"

    private val httpClient: OkHttpClient by lazy {
        OkHttpClient.Builder()
            .connectTimeout(20, TimeUnit.SECONDS)
            .readTimeout(30, TimeUnit.SECONDS)
            .callTimeout(45, TimeUnit.SECONDS)
            .retryOnConnectionFailure(true)
            .build()
    }

    fun baseUrl(context: Context): String =
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .getString(PREF_URL, DEFAULT_URL) ?: DEFAULT_URL

    /** Acepta solo una URL HTTP(S) base, sin ruta adicional ni parámetros. */
    fun normalizeBaseUrl(value: String): String {
        val raw = value.trim()
        val uri = try {
            URI(raw)
        } catch (e: Exception) {
            throw IllegalArgumentException("Introduce una URL válida, por ejemplo http://10.0.2.2:8000/")
        }
        if ((uri.scheme != "http" && uri.scheme != "https") ||
            uri.host.isNullOrBlank() || uri.userInfo != null ||
            uri.query != null || uri.fragment != null ||
            (uri.path.isNotEmpty() && uri.path != "/") ||
            uri.port > 65535
        ) {
            throw IllegalArgumentException("Usa una URL base como http://10.0.2.2:8000/")
        }
        return raw.trimEnd('/') + "/"
    }

    fun saveBaseUrl(context: Context, value: String) {
        val normalized = normalizeBaseUrl(value)
        context.getSharedPreferences(PREFS_NAME, Context.MODE_PRIVATE)
            .edit().putString(PREF_URL, normalized).apply()
    }

    fun studentService(context: Context): StudentApiService =
        Retrofit.Builder()
            .baseUrl(baseUrl(context))
            .client(httpClient)
            .addConverterFactory(GsonConverterFactory.create())
            .build()
            .create(StudentApiService::class.java)
}
