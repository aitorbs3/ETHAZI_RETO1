package com.ethazi.javafx;

import com.ethazi.javafx.i18n.I18n;
import javafx.application.Application;
import javafx.fxml.FXMLLoader;
import com.ethazi.javafx.controller.MainController;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.image.Image;
import javafx.geometry.Rectangle2D;
import javafx.stage.Screen;
import javafx.stage.Stage;

import java.io.IOException;
import java.util.Objects;

/** Cliente JavaFX: muestra el idioma elegido y consulta los datos mediante FastAPI. */
public class MainApp extends Application {

    @Override
    public void start(Stage stage) throws IOException {
        FXMLLoader loader = new FXMLLoader(
                MainApp.class.getResource("/fxml/main.fxml"), I18n.bundle());
        Parent root = loader.load();
        root.getProperties().put("ETHAZI_CONTROLLER", loader.getController());

        // Tamaño inicial adaptado al espacio útil del monitor.
        Rectangle2D area = Screen.getPrimary().getVisualBounds();
        double ancho = Math.min(1280, area.getWidth() * 0.94);
        double alto = Math.min(840, area.getHeight() * 0.94);
        Scene scene = new Scene(root, ancho, alto);
        // Los controles utilizan 'em' en CSS y se reescalan desde aquí.
        // JavaFX ya tiene en cuenta la escala de pantalla del sistema.
        scene.widthProperty().addListener((obs, antes, despues) ->
                actualizarEscala(scene.getRoot(), despues.doubleValue()));
        // Al cambiar el idioma JavaFX crea una raíz nueva: hay que adaptar también esa vista.
        scene.rootProperty().addListener((obs, anterior, actual) ->
                actualizarEscala(actual, scene.getWidth()));
        actualizarEscala(root, ancho);
        scene.getStylesheets().add(
                Objects.requireNonNull(MainApp.class.getResource("/css/styles.css")).toExternalForm());

        stage.setTitle(I18n.tr("app.title"));
        // En pantallas reducidas la zona central dispone de desplazamiento vertical.
        stage.setMinWidth(Math.min(600, area.getWidth()));
        stage.setMinHeight(Math.min(470, area.getHeight()));
        stage.setScene(scene);
        stage.getIcons().add(new Image(Objects.requireNonNull(
                MainApp.class.getResourceAsStream("/images/icono_hogwarts.png"))));
        stage.centerOnScreen();
        stage.show();
    }

    /** Tamaño base en píxeles lógicos; las medidas en em siguen esta escala. */
    private static void actualizarEscala(Parent root, double ancho) {
        double base = ancho < 760 ? 15.0 : ancho < 1350 ? 16.0
                : ancho < 1900 ? 17.0 : 18.0;
        root.setStyle("-fx-font-size: " + base + "px;");
        Object controlador = root.getProperties().get("ETHAZI_CONTROLLER");
        if (controlador instanceof MainController controller) {
            controller.aplicarFuenteBase(base);
        }
    }

    public static void main(String[] args) {
        launch(args);
    }
}
