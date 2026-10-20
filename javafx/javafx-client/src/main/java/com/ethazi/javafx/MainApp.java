package com.ethazi.javafx;

// Clase encargada de gestionar el idioma y recuperar las traducciones.
import com.ethazi.javafx.i18n.I18n;

// Clase base de JavaFX para crear y ejecutar una aplicación gráfica.
import javafx.application.Application;

// Permite cargar la interfaz gráfica definida en un archivo FXML.
import javafx.fxml.FXMLLoader;

// Controlador principal que gestiona los eventos y los datos de la interfaz.
import com.ethazi.javafx.controller.MainController;

// Representa el elemento raíz de la interfaz gráfica cargada.
import javafx.scene.Parent;

// Contenedor que agrupa la interfaz y permite configurar su presentación.
import javafx.scene.Scene;

// Permite cargar imágenes, como el icono de la ventana.
import javafx.scene.image.Image;

// Representa un área rectangular, utilizada para conocer el espacio disponible.
import javafx.geometry.Rectangle2D;

// Permite obtener información sobre las pantallas conectadas al sistema.
import javafx.stage.Screen;

// Representa la ventana principal de la aplicación JavaFX.
import javafx.stage.Stage;

import java.io.IOException;
import java.util.Objects;

/**
 * Clase principal de la aplicación JavaFX.
 *
 * Se encarga de inicializar la interfaz gráfica, cargar la vista definida
 * en FXML, configurar la ventana principal y aplicar los estilos CSS.
 *
 * También adapta el tamaño base de la fuente a la anchura de la ventana
 * y utiliza el idioma seleccionado para mostrar los textos traducidos.
 *
 * La comunicación con el backend FastAPI se gestiona mediante las clases
 * correspondientes del servicio, no directamente desde esta clase.
 */
public class MainApp extends Application {

    /**
     * Método de inicio de JavaFX.
     *
     * JavaFX lo ejecuta automáticamente después de inicializar la aplicación.
     * Aquí se carga la interfaz, se crea la escena y se configura la ventana
     * principal que verá el usuario.
     *
     * @param stage ventana principal de la aplicación
     * @throws IOException si se produce un error al cargar los recursos FXML
     */
    @Override
    public void start(Stage stage) throws IOException {

        // Crea el cargador de FXML indicando la ruta de la vista principal
        // y el conjunto de traducciones correspondiente al idioma activo.
        FXMLLoader loader = new FXMLLoader(
                MainApp.class.getResource("/fxml/main.fxml"), I18n.bundle());

        // Carga la interfaz definida en main.fxml y obtiene su nodo raíz.
        Parent root = loader.load();

        // Guarda una referencia al controlador dentro de las propiedades
        // del nodo raíz para poder recuperarlo cuando sea necesario,
        // por ejemplo, al actualizar el tamaño base de la fuente.
        root.getProperties().put("ETHAZI_CONTROLLER", loader.getController());

        // Obtiene el área visible del monitor principal, excluyendo
        // las zonas reservadas por elementos del sistema operativo.
        Rectangle2D area = Screen.getPrimary().getVisualBounds();

        // Calcula la anchura inicial de la ventana.
        // Se utiliza como máximo 1280 píxeles y, además, se limita
        // el tamaño al 94 % del espacio visible del monitor.
        double ancho = Math.min(1280, area.getWidth() * 0.94);

        // Calcula la altura inicial con un máximo de 840 píxeles
        // y respetando también el 94 % del espacio visible.
        double alto = Math.min(840, area.getHeight() * 0.94);

        // Crea la escena principal con la interfaz cargada y las dimensiones
        // calculadas según el espacio disponible en la pantalla.
        Scene scene = new Scene(root, ancho, alto);

        // Escucha los cambios en la anchura de la escena.
        // Cada vez que cambia, recalcula el tamaño base de la fuente
        // para adaptar la interfaz a las dimensiones actuales.
        // La escala de pantalla del sistema operativo ya es gestionada
        // por JavaFX, por lo que aquí se trabaja con píxeles lógicos.
        scene.widthProperty().addListener((obs, antes, despues) ->
                actualizarEscala(scene.getRoot(), despues.doubleValue()));

        // Escucha los cambios en el nodo raíz de la escena.
        // Si se sustituye la vista, por ejemplo al cambiar el idioma,
        // vuelve a aplicar la escala correspondiente a la nueva interfaz.
        scene.rootProperty().addListener((obs, anterior, actual) ->
                actualizarEscala(actual, scene.getWidth()));

        // Aplica la escala inicial antes de mostrar la ventana.
        actualizarEscala(root, ancho);

        // Carga la hoja de estilos CSS que define la apariencia visual
        // de los componentes de la interfaz.
        // Objects.requireNonNull comprueba que el recurso exista;
        // si no se encuentra, se producirá una excepción.
        scene.getStylesheets().add(
                Objects.requireNonNull(
                        MainApp.class.getResource("/css/styles.css"))
                        .toExternalForm());

        // Establece el título de la ventana utilizando la traducción
        // de la clave "app.title" del idioma actualmente seleccionado.
        stage.setTitle(I18n.tr("app.title"));

        // Define el tamaño mínimo de la ventana.
        // Si el monitor es pequeño, se adapta a su anchura disponible
        // para evitar exigir un tamaño superior al espacio visible.
        stage.setMinWidth(Math.min(600, area.getWidth()));

        // Establece una altura mínima de 470 píxeles o la altura disponible
        // del monitor si esta es inferior.
        // La interfaz puede utilizar desplazamiento vertical en pantallas
        // reducidas para facilitar el acceso al contenido.
        stage.setMinHeight(Math.min(470, area.getHeight()));

        // Asocia la escena creada a la ventana principal.
        stage.setScene(scene);

        // Carga el icono de la aplicación desde los recursos del proyecto.
        // Se comprueba que el archivo exista antes de crear la imagen.
        stage.getIcons().add(new Image(Objects.requireNonNull(
                MainApp.class.getResourceAsStream("/images/icono_hogwarts.png"))));

        // Sitúa la ventana en el centro de la pantalla principal.
        stage.centerOnScreen();

        // Muestra la ventana y hace visible la interfaz al usuario.
        stage.show();
    }

    /**
     * Actualiza el tamaño base de la fuente de la interfaz.
     *
     * Selecciona un tamaño de fuente según la anchura de la escena.
     * Este valor se establece como estilo del nodo raíz para que los
     * componentes que utilizan unidades relativas em puedan adaptarse.
     *
     * Si el controlador principal está asociado al nodo raíz,
     * también se le comunica el nuevo tamaño para que actualice
     * los elementos que gestiona directamente.
     *
     * @param root nodo raíz de la interfaz que se va a adaptar
     * @param ancho anchura actual de la escena, en píxeles lógicos
     */
    private static void actualizarEscala(Parent root, double ancho) {

        // Selecciona el tamaño base de la fuente según la anchura disponible:
        // menos de 760 píxeles: 15 px;
        // desde 760 y menos de 1350: 16 px;
        // desde 1350 y menos de 1900: 17 px;
        // 1900 píxeles o más: 18 px.
        double base = ancho < 760 ? 15.0 : ancho < 1350 ? 16.0
                : ancho < 1900 ? 17.0 : 18.0;

        // Aplica el tamaño base de la fuente al nodo raíz.
        // Los elementos que utilicen unidades em pueden escalar
        // en función de este tamaño.
        root.setStyle("-fx-font-size: " + base + "px;");

        // Recupera el controlador guardado en las propiedades del nodo raíz.
        Object controlador = root.getProperties().get("ETHAZI_CONTROLLER");

        // Comprueba que el objeto recuperado sea un MainController.
        // Si lo es, llama a su método para actualizar también la fuente
        // de los componentes gestionados por el controlador.
        if (controlador instanceof MainController controller) {
            controller.aplicarFuenteBase(base);
        }
    }

    /**
     * Punto de entrada de la aplicación.
     *
     * La máquina virtual de Java ejecuta este método al iniciar el programa.
     * El método launch() pone en marcha el ciclo de vida de JavaFX y,
     * una vez inicializado el entorno gráfico, invoca start().
     *
     * @param args argumentos recibidos desde la línea de comandos
     */
    public static void main(String[] args) {

        // Inicia JavaFX y transmite los argumentos al ciclo de vida
        // de la aplicación.
        launch(args);
    }
}