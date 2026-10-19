plugins {
    alias(libs.plugins.android.application)
    id("com.google.devtools.ksp") version "2.3.10"

}

android {
    namespace = "com.dm2.myapplication"
    compileSdk {
        version = release(37)
    }

    buildFeatures {
        viewBinding = true
    }

    defaultConfig {
        applicationId = "com.dm2.myapplication"
        minSdk = 24
        targetSdk = 37
        versionCode = 1
        versionName = "1.0"

        testInstrumentationRunner = "androidx.test.runner.AndroidJUnitRunner"
    }

    buildTypes {
        release {
            optimization {
                enable = false
            }
        }
    }
    compileOptions {
        sourceCompatibility = JavaVersion.VERSION_11
        targetCompatibility = JavaVersion.VERSION_11
    }
}

dependencies {
    implementation(libs.androidx.activity.ktx)
    implementation(libs.androidx.appcompat)
    implementation(libs.androidx.constraintlayout)
    implementation(libs.androidx.core.ktx)
    implementation(libs.material)
    testImplementation(libs.junit)
    androidTestImplementation(libs.androidx.espresso.core)
    androidTestImplementation(libs.androidx.junit)

    // Retrofit y Gson para la comunicación con la API de Python
    implementation("com.squareup.retrofit2:retrofit:2.9.0")
    implementation("com.squareup.retrofit2:converter-gson:2.9.0")

    // Glide: descargar y almacenar en caché las fotos que devuelve la API
    implementation("com.github.bumptech.glide:glide:4.16.0")

    // Room para la base de datos local (Caché offline)
    val roomVersion = "2.8.5"
    implementation("androidx.room:room-runtime:$roomVersion")
    implementation("androidx.room:room-ktx:$roomVersion")
    ksp("androidx.room:room-compiler:$roomVersion")
}