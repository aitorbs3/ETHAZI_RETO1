package com.dm2.myapplication

// Permite acceder al entorno de instrumentación para obtener información
// sobre la aplicación que se está ejecutando durante la prueba.
import androidx.test.platform.app.InstrumentationRegistry

// Proporciona el ejecutor de pruebas que permite ejecutar el test
// en un dispositivo Android o en un emulador.
import androidx.test.ext.junit.runners.AndroidJUnit4

// Importa la anotación @Test para identificar los métodos de prueba.
import org.junit.Test

// Permite indicar que la clase utilizará el ejecutor AndroidJUnit4.
import org.junit.runner.RunWith

// Importa las funciones de aserción de JUnit, como assertEquals,
// que permiten comprobar si un resultado coincide con el esperado.
import org.junit.Assert.*

/**
 * Prueba instrumentada que se ejecuta en un dispositivo Android
 * o en un emulador.
 *
 * A diferencia de una prueba unitaria local, esta prueba permite
 * interactuar con el entorno real de la aplicación Android.
 */
@RunWith(AndroidJUnit4::class)
class ExampleInstrumentedTest {

    // Indica que este método es una prueba que debe ejecutar JUnit.
    @Test
    fun useAppContext() {

        // Obtiene el contexto de la aplicación que se está probando.
        // El contexto permite acceder a información y recursos
        // propios de la aplicación instalada.
        val appContext = InstrumentationRegistry
            .getInstrumentation()
            .targetContext

        // Comprueba que el nombre del paquete de la aplicación
        // coincide con el esperado.
        // Si ambos valores son iguales, la prueba se supera.
        // Si son diferentes, JUnit marca la prueba como fallida.
        assertEquals("com.dm2.myapplication", appContext.packageName)
    }
}