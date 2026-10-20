package com.dm2.myapplication

import com.bumptech.glide.Glide
import com.bumptech.glide.load.model.GlideUrl
import com.bumptech.glide.load.model.LazyHeaders
import android.widget.ImageView

/** Muestra la URL de imagen de FastAPI. Sin foto o HTTP fallido: silueta local. */
object StudentPhotos {
    fun load(target: ImageView, url: String?) {
        Glide.with(target).clear(target)
        val clean = url?.trim()?.takeIf {
            it.startsWith("https://", ignoreCase = true) || it.startsWith("http://", ignoreCase = true)
        }
        if (clean == null) {
            target.setImageResource(R.drawable.usuario)
            return
        }
        val glideUrl = GlideUrl(clean, LazyHeaders.Builder()
            .addHeader("User-Agent", "Mozilla/5.0 (compatible; ETHAZI-Android/1.0)")
            .build())
        Glide.with(target)
            .load(glideUrl)
            .placeholder(R.drawable.usuario)
            .error(R.drawable.usuario)
            .centerCrop()
            .into(target)
    }
}
