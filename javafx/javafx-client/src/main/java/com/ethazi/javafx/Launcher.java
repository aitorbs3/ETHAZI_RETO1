package com.ethazi.javafx;

/**
 * Clase de arranque de la aplicación JavaFX.
 *
 * Actúa como punto de entrada cuando se ejecuta la aplicación desde
 * un FAT JAR (JAR que incluye las dependencias necesarias para su ejecución).
 *
 * Su función es delegar el inicio de la aplicación en la clase MainApp,
 * que contiene la lógica principal de arranque de JavaFX.
 */
public class Launcher {

    /**
     * Método principal de entrada del programa.
     *
     * Recibe los argumentos proporcionados al ejecutar la aplicación
     * y los transmite al método main() de MainApp para iniciar JavaFX.
     *
     * @param args argumentos recibidos desde la línea de comandos
     */
    public static void main(String[] args) {

        // Delega el arranque de la aplicación en la clase principal MainApp.
        MainApp.main(args);
    }
}