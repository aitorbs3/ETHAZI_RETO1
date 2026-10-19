package com.ethazi.javafx.controller;

import com.ethazi.javafx.i18n.I18n;
import com.ethazi.javafx.model.NuevoAlumno;
import com.ethazi.javafx.model.Student;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.Node;
import javafx.scene.control.*;
import javafx.scene.image.Image;
import javafx.scene.layout.*;
import javafx.stage.Stage;
import javafx.stage.Window;

import java.time.LocalDate;
import java.time.format.DateTimeParseException;
import java.util.Objects;
import java.util.Optional;

/** Formulario compartido de alta y edición para alumnos nuevos de Hogwarths. */
public final class AlumnoFormDialog {
    public static final String CASA_NUEVA = "Hogwarths";

    private AlumnoFormDialog() { }

    public static Optional<NuevoAlumno> mostrar(Window owner) {
        return mostrarFormulario(owner, null);
    }

    public static Optional<NuevoAlumno> mostrarEditar(Window owner, Student alumno) {
        if (alumno == null || !CASA_NUEVA.equalsIgnoreCase(alumno.getCasa())) {
            throw new IllegalArgumentException(I18n.tr("form.error.readOnly"));
        }
        return mostrarFormulario(owner, alumno);
    }

    private static Optional<NuevoAlumno> mostrarFormulario(Window owner, Student alumno) {
        boolean editando = alumno != null;
        Dialog<NuevoAlumno> dialogo = new Dialog<>();
        dialogo.initOwner(owner);
        dialogo.setTitle(I18n.tr(editando ? "form.edit.title" : "form.add.title"));
        dialogo.setHeaderText(editando
                ? I18n.tr("form.edit.header", alumno.getNombre())
                : I18n.tr("form.add.header"));

        // Cuando se abra el diálogo, mostrar también el escudo en la barra de Windows.
        dialogo.setOnShown(evento -> {
            Window ventana = dialogo.getDialogPane().getScene().getWindow();
            if (ventana instanceof Stage stage) {
                stage.getIcons().add(new Image(Objects.requireNonNull(
                        AlumnoFormDialog.class.getResourceAsStream("/images/icono_hogwarts.png"))));
            }
        });

        ButtonType guardar = new ButtonType(
                I18n.tr(editando ? "form.save.edit" : "form.save.add"),
                ButtonBar.ButtonData.OK_DONE);
        ButtonType cancelar = new ButtonType(I18n.tr("common.cancel"),
                ButtonBar.ButtonData.CANCEL_CLOSE);
        dialogo.getDialogPane().getButtonTypes().setAll(guardar, cancelar);
        // El diálogo respeta el ancho útil de la ventana (y el tamaño de fuente).
        double anchoDisponible = owner == null ? 560 : owner.getWidth() - 40;
        dialogo.getDialogPane().setPrefWidth(Math.max(420, Math.min(560, anchoDisponible)));
        dialogo.getDialogPane().getStylesheets().add(Objects.requireNonNull(
                AlumnoFormDialog.class.getResource("/css/styles.css")).toExternalForm());
        dialogo.getDialogPane().getStyleClass().add("student-form-dialog");

        // Facilita el uso del formulario con teclado y lectores de pantalla.
        dialogo.getDialogPane().setAccessibleText(I18n.tr(editando
                ? "form.edit.title" : "form.add.title"));

        TextField nombre = campo("form.name.prompt");
        TextField especie = campo("form.species.prompt");
        TextField genero = campo("form.gender.prompt");
        DatePicker nacimiento = new DatePicker();
        nacimiento.setEditable(false);
        nacimiento.setShowWeekNumbers(false);
        nacimiento.setPrefWidth(210);
        nacimiento.setDayCellFactory(picker -> new DateCell() {
            @Override
            public void updateItem(LocalDate fecha, boolean empty) {
                super.updateItem(fecha, empty);
                boolean futura = !empty && fecha != null && fecha.isAfter(LocalDate.now());
                setDisable(empty || futura);
                setTooltip(futura ? new Tooltip(I18n.tr("form.futureTooltip")) : null);
            }
        });
        Button limpiarFecha = new Button(I18n.tr("form.clearDate"));
        limpiarFecha.setOnAction(evento -> nacimiento.setValue(null));
        HBox campoNacimiento = new HBox(8, nacimiento, limpiarFecha);
        TextField nacionalidad = campo("form.nationality.prompt");
        TextField patronus = campo("form.optional");
        TextField imagen = campo("form.image.prompt");
        nombre.setAccessibleText(I18n.tr("form.name.required"));
        especie.setAccessibleText(I18n.tr("field.species"));
        genero.setAccessibleText(I18n.tr("field.gender"));
        nacimiento.setAccessibleText(I18n.tr("field.birth"));
        nacionalidad.setAccessibleText(I18n.tr("field.nationality"));
        patronus.setAccessibleText(I18n.tr("field.patronus"));
        imagen.setAccessibleText(I18n.tr("field.image"));

        if (editando) {
            nombre.setText(valorEditable(alumno.getNombre()));
            especie.setText(valorEditable(alumno.getEspecie()));
            genero.setText(valorEditable(alumno.getGenero()));
            nacionalidad.setText(valorEditable(alumno.getNacionalidad()));
            patronus.setText(valorEditable(alumno.getPatronus()));
            imagen.setText(valorEditable(alumno.getImagen()));
            String fechaActual = valorEditable(alumno.getFechaNacimiento());
            if (!fechaActual.isBlank()) {
                try {
                    nacimiento.setValue(LocalDate.parse(fechaActual));
                } catch (DateTimeParseException error) {
                    throw new IllegalArgumentException(
                            I18n.tr("form.error.invalidDate", fechaActual), error);
                }
            }
        }

        GridPane tabla = new GridPane();
        tabla.setHgap(12);
        tabla.setVgap(12);
        tabla.setAlignment(Pos.TOP_LEFT);
        Label casa = new Label(CASA_NUEVA);
        casa.getStyleClass().add("house-value");
        tabla.addRow(0, etiqueta("field.house"), casa);
        tabla.addRow(1, etiqueta("form.name.required"), nombre);
        tabla.addRow(2, etiqueta("field.species"), especie);
        tabla.addRow(3, etiqueta("field.gender"), genero);
        tabla.addRow(4, etiqueta("field.birth"), campoNacimiento);
        tabla.addRow(5, etiqueta("field.nationality"), nacionalidad);
        tabla.addRow(6, etiqueta("field.patronus"), patronus);
        tabla.addRow(7, etiqueta("field.image"), imagen);
        tabla.getColumnConstraints().addAll(columna(135, false), columna(310, true));

        Label ayuda = new Label(I18n.tr("form.help"));
        ayuda.setWrapText(true);
        ayuda.getStyleClass().add("detail-caption");
        Label validacion = new Label();
        validacion.getStyleClass().add("form-error");
        validacion.setWrapText(true);

        VBox contenido = new VBox(14, tabla, ayuda, validacion);
        contenido.setPadding(new Insets(12, 8, 8, 8));
        ScrollPane scroll = new ScrollPane(contenido);
        scroll.setFitToWidth(true);
        scroll.setMaxHeight(460);
        scroll.setStyle("-fx-background-color: transparent; -fx-background: transparent;");
        dialogo.getDialogPane().setContent(scroll);

        Node botonGuardar = dialogo.getDialogPane().lookupButton(guardar);
        Runnable validar = () -> {
            boolean incompleto = vacio(nombre);
            String url = imagen.getText().strip();
            boolean urlInvalida = !url.isEmpty()
                    && !(url.startsWith("http://") || url.startsWith("https://"));
            LocalDate fecha = nacimiento.getValue();
            boolean fechaFutura = fecha != null && fecha.isAfter(LocalDate.now());
            botonGuardar.setDisable(incompleto || urlInvalida || fechaFutura);
            validacion.setText(fechaFutura ? I18n.tr("form.error.futureDate")
                    : urlInvalida ? I18n.tr("form.error.invalidImage") : "");
        };
        for (TextField campo : new TextField[]{nombre, imagen}) {
            campo.textProperty().addListener((obs, anterior, actual) -> validar.run());
        }
        nacimiento.valueProperty().addListener((obs, anterior, actual) -> validar.run());
        validar.run();

        dialogo.setResultConverter(boton -> {
            if (boton != guardar) return null;
            LocalDate fecha = nacimiento.getValue();
            if (fecha != null && fecha.isAfter(LocalDate.now())) return null;
            return new NuevoAlumno(
                    nombre.getText().strip(), CASA_NUEVA,
                    opcional(especie.getText()), opcional(genero.getText()),
                    fecha == null ? null : fecha.toString(),
                    opcional(nacionalidad.getText()), opcional(patronus.getText()),
                    opcional(imagen.getText()));
        });
        return dialogo.showAndWait();
    }

    private static ColumnConstraints columna(double anchura, boolean crecer) {
        ColumnConstraints c = new ColumnConstraints();
        c.setMinWidth(anchura);
        if (crecer) c.setHgrow(Priority.ALWAYS);
        return c;
    }

    private static Label etiqueta(String clave) {
        Label label = new Label(I18n.tr(clave));
        label.getStyleClass().add("field-label");
        return label;
    }

    private static TextField campo(String clave) {
        TextField field = new TextField();
        field.setPromptText(I18n.tr(clave));
        field.setMaxWidth(Double.MAX_VALUE);
        field.getStyleClass().add("search-input");
        return field;
    }

    private static boolean vacio(TextField campo) {
        return campo.getText() == null || campo.getText().isBlank();
    }

    private static String opcional(String valor) {
        return valor == null || valor.isBlank() ? null : valor.strip();
    }

    private static String valorEditable(String valor) {
        return valor == null || valor.isBlank() || "—".equals(valor.strip())
                ? "" : valor.strip();
    }
}
