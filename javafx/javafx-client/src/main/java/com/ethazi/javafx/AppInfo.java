package com.ethazi.javafx;

/**
 * Contiene la información general de la aplicación que se muestra
 * en elementos de la interfaz, como el pie de página y la ventana
 * «Acerca de».
 *
 * Centraliza los datos de versión y autoría para evitar tener que
 * repetirlos en diferentes partes del código.
 *
 * La versión debe mantenerse sincronizada con la definida en pom.xml
 * cuando se publique una nueva versión de la aplicación.
 */
public final class AppInfo {

    // Versión actual de la aplicación.
    // El sufijo SNAPSHOT indica que se trata de una versión de desarrollo
    // que todavía puede sufrir cambios antes de una publicación definitiva.
    public static final String VERSION = "0.1.0-SNAPSHOT";

    // Nombre del equipo responsable del desarrollo de la aplicación.
    public static final String AUTHORS = "Equipo FILOS";

    // Constructor privado para impedir la creación de objetos de esta clase.
    // Como los datos son constantes y estáticos, se accede a ellos directamente
    // mediante AppInfo.VERSION y AppInfo.AUTHORS.
    private AppInfo() { }
}