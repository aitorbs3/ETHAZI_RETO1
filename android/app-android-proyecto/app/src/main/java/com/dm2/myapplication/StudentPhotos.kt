package com.dm2.myapplication

import com.bumptech.glide.Glide
import com.bumptech.glide.load.model.GlideUrl
import com.bumptech.glide.load.model.LazyHeaders
import android.widget.ImageView

/**
 * Utilidad para cargar las fotografías de los estudiantes.
 * Utiliza Glide para descargar y mostrar imágenes.
 * Si no hay foto o la descarga falla, muestra una imagen local.
 */
object StudentPhotos {

    fun load(target: ImageView, url: String?) {

        // Limpia una carga anterior asociada a esta vista.
        // Evita que una petición antigua muestre una fotografía incorrecta.
        Glide.with(target).clear(target)

        // Elimina espacios de la URL y comprueba que use HTTP o HTTPS.
        // Si la URL es nula o no es válida, clean será null.
        val clean = url?.trim()?.takeIf {
            it.startsWith("https://", ignoreCase = true) ||
            it.startsWith("http://", ignoreCase = true)
        }

        // Si no existe una URL válida, muestra la silueta local
        // y termina la función sin realizar ninguna descarga.
        if (clean == null) {
            target.setImageResource(R.drawable.usuario)
            return
        }

        // Crea una URL compatible con Glide y añade un encabezado
        // User-Agent que identifica las solicitudes de la aplicación.
        val glideUrl = GlideUrl(
            clean,
            LazyHeaders.Builder()
                .addHeader(
                    "User-Agent",
                    "Mozilla/5.0 (compatible; ETHAZI-Android/1.0)"
                )
                .build()
        )

        // Glide gestiona la descarga y la carga asíncrona de la imagen.
        Glide.with(target)
            .load(glideUrl)

            // Imagen provisional mientras se descarga la fotografía.
            .placeholder(R.drawable.usuario)

            // Imagen que se muestra si la descarga o la carga falla.
            .error(R.drawable.usuario)

            // Recorta la fotografía para adaptarla al espacio disponible.
            .centerCrop()

            // Coloca la imagen en el ImageView recibido como parámetro.
            .into(target)
    }
}