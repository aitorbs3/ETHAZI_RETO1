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

/**
 * Diálogo de formulario compartido en JavaFX para el alta y la edición de alumnos 
 * pertenecientes a la casa propia del proyecto ("Hogwarths").
 * Gestiona de forma dinámica la validación de campos obligatorios, restricciones de fechas 
 * de nacimiento y la carga de recursos gráficos corporativos.
 */
public final class AlumnoFormDialog {
    
    /** Constante que define la casa por defecto asignada para las nuevas altas y ediciones permitidas. */
    public static final String CASA_NUEVA = "Hogwarths";

    /** Constructor privado para evitar la instanciación de esta clase de utilidad estática. */
    private AlumnoFormDialog() { }

    /**
     * Muestra el formulario en modo de creación (alta de un nuevo alumno).
     * 
     * @param owner Ventana principal o propietaria del diálogo.
     * @return Un Optional que contiene el objeto NuevoAlumno si se confirma la acción, o vacío si se cancela.
     */
    public static Optional<NuevoAlumno> mostrar(Window owner) {
        return mostrarFormulario(owner, null);
    }

    /**
     * Muestra el formulario en modo de edición para un alumno existente.
     * Valida previamente que el alumno pertenezca a la casa editable ("Hogwarths").
     * 
     * @param owner  Ventana principal o propietaria del diálogo.
     * @param alumno Objeto Student con los datos actuales a precargar en el formulario.
     * @return Un Optional con los datos modificados o vacío si se cancela.
     * @throws IllegalArgumentException si el alumno es nulo o no pertenece a la casa editable.
     */
    public static Optional<NuevoAlumno> mostrarEditar(Window owner, Student alumno) {
        if (alumno == null || !CASA_NUEVA.equalsIgnoreCase(alumno.getCasa())) {
            throw new IllegalArgumentException(I18n.tr("form.error.readOnly"));
        }
        return mostrarFormulario(owner, alumno);
    }

    /**
     * Método interno encargado de construir la interfaz gráfica del diálogo, configurar los controles,
     * aplicar los estilos CSS, registrar los validadores en tiempo real y mapear los resultados.
     */
    private static Optional<NuevoAlumno> mostrarFormulario(Window owner, Student alumno) {
        boolean editando = alumno != null;
        Dialog<NuevoAlumno> dialogo = new Dialog<>();
        dialogo.initOwner(owner);
        
        // Títulos y cabeceras dinámicos según el modo (Alta vs Edición) mediante internacionalización (I18n)
        dialogo.setTitle(I18n.tr(editando ? "form.edit.title" : "form.add.title"));
        dialogo.setHeaderText(editando
                ? I18n.tr("form.edit.header", alumno.getNombre())
                : I18n.tr("form.add.header"));

        // Evento para inyectar el icono corporativo de la aplicación en la barra de tareas de la ventana del diálogo
        dialogo.setOnShown(evento -> {
            Window ventana = dialogo.getDialogPane().getScene().getWindow();
            if (ventana instanceof Stage stage) {
                stage.getIcons().add(new Image(Objects.requireNonNull(
                        AlumnoFormDialog.class.getResourceAsStream("/images/icono_hogwarts.png"))));
            }
        });

        // Configuración de los botones de acción del diálogo (Guardar / Cancelar)
        ButtonType guardar = new ButtonType(
                I18n.tr(editando ? "form.save.edit" : "form.save.add"),
                ButtonBar.ButtonData.OK_DONE);
        ButtonType cancelar = new ButtonType(I18n.tr("common.cancel"),
                ButtonBar.ButtonData.CANCEL_CLOSE);
        dialogo.getDialogPane().getButtonTypes().setAll(guardar, cancelar);
        
        // Adaptación dinámica del ancho del diálogo en función de la ventana principal
        double anchoDisponible = owner == null ? 560 : owner.getWidth() - 40;
        dialogo.getDialogPane().setPrefWidth(Math.max(420, Math.min(560, anchoDisponible)));
        
        // Carga de la hoja de estilos CSS y aplicación de clases de diseño
        dialogo.getDialogPane().getStylesheets().add(Objects.requireNonNull(
                AlumnoFormDialog.class.getResource("/css/styles.css")).toExternalForm());
        dialogo.getDialogPane().getStyleClass().add("student-form-dialog");

        // Accesibilidad: descripción para lectores de pantalla y navegación por teclado
        dialogo.getDialogPane().setAccessibleText(I18n.tr(editando
                ? "form.edit.title" : "form.add.title"));

        // Declaración de los componentes de entrada de texto y selección
        TextField nombre = campo("form.name.prompt");
        TextField especie = campo("form.species.prompt");
        TextField genero = campo("form.gender.prompt");
        
        // Selector de fecha de nacimiento con restricciones de accesibilidad y validación de días futuros
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
        
        // Botón auxiliar para limpiar la fecha seleccionada en el DatePicker
        Button limpiarFecha = new Button(I18n.tr("form.clearDate"));
        limpiarFecha.setOnAction(evento -> nacimiento.setValue(null));
        HBox campoNacimiento = new HBox(8, nacimiento, limpiarFecha);
        
        TextField nacionalidad = campo("form.nationality.prompt");
        TextField patronus = campo("form.optional");
        TextField imagen = campo("form.image.prompt");

        // Configuración de etiquetas accesibles por campo
        nombre.setAccessibleText(I18n.tr("form.name.required"));
        especie.setAccessibleText(I18n.tr("field.species"));
        genero.setAccessibleText(I18n.tr("field.gender"));
        nacimiento.setAccessibleText(I18n.tr("field.birth"));
        nacionalidad.setAccessibleText(I18n.tr("field.nationality"));
        patronus.setAccessibleText(I18n.tr("field.patronus"));
        imagen.setAccessibleText(I18n.tr("field.image"));

        // Precarga de datos en modo edición si se recibe un alumno válido
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

        // Distribución tabular de los campos del formulario mediante GridPane
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

        // Componentes informativos y de visualización de errores de validación
        Label ayuda = new Label(I18n.tr("form.help"));
        ayuda.setWrapText(true);
        ayuda.getStyleClass().add("detail-caption");
        
        Label validacion = new Label();
        validacion.getStyleClass().add("form-error");
        validacion.setWrapText(true);

        // Contenedor principal con barra de desplazamiento (ScrollPane) para asegurar responsividad
        VBox contenido = new VBox(14, tabla, ayuda, validacion);
        contenido.setPadding(new Insets(12, 8, 8, 8));
        ScrollPane scroll = new ScrollPane(contenido);
        scroll.setFitToWidth(true);
        scroll.setMaxHeight(460);
        scroll.setStyle("-fx-background-color: transparent; -fx-background: transparent;");
        dialogo.getDialogPane().setContent(scroll);

        // Lógica de validación reactiva en tiempo real sobre los campos de entrada
        Node botonGuardar = dialogo.getDialogPane().lookupButton(guardar);
        Runnable validar = () -> {
            boolean incompleto = vacio(nombre);
            String url = imagen.getText().strip();
            boolean urlInvalida = !url.isEmpty()
                    && !(url.startsWith("http://") || url.startsWith("https://"));
            LocalDate fecha = nacimiento.getValue();
            boolean fechaFutura = fecha != null && fecha.isAfter(LocalDate.now());
            
            // Deshabilita el botón de guardado si hay errores de validación críticos
            botonGuardar.setDisable(incompleto || urlInvalida || fechaFutura);
            validacion.setText(fechaFutura ? I18n.tr("form.error.futureDate")
                    : urlInvalida ? I18n.tr("form.error.invalidImage") : "");
        };

        // Registro de listeners para la validación automática ante cambios en los campos clave
        for (TextField campoTexto : new TextField[]{nombre, imagen}) {
            campoTexto.textProperty().addListener((obs, anterior, actual) -> validar.run());
        }
        nacimiento.valueProperty().addListener((obs, anterior, actual) -> validar.run());
        validar.run();

        // Conversor del resultado del diálogo al pulsar el botón de confirmación
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

    /** Método auxiliar para definir restricciones de ancho y crecimiento en las columnas de la tabla. */
    private static ColumnConstraints columna(double anchura, boolean crecer) {
        ColumnConstraints c = new ColumnConstraints();
        c.setMinWidth(anchura);
        if (crecer) c.setHgrow(Priority.ALWAYS);
        return c;
    }

    /** Método auxiliar para instanciar etiquetas de texto aplicando estilos estándar. */
    private static Label etiqueta(String clave) {
        Label label = new Label(I18n.tr(clave));
        label.getStyleClass().add("field-label");
        return label;
    }

    /** Método auxiliar para instanciar campos de texto estandarizados con prompts internacionalizados. */
    private static TextField campo(String clave) {
        TextField field = new TextField();
        field.setPromptText(I18n.tr(clave));
        field.setMaxWidth(Double.MAX_VALUE);
        field.getStyleClass().add("search-input");
        return field;
    }

    /** Valida si un campo de texto obligatorio se encuentra vacío o en blanco. */
    private static boolean vacio(TextField campo) {
        return campo.getText() == null || campo.getText().isBlank();
    }

    /** Limpia y normaliza una cadena de texto opcional, devolviendo null si está vacía. */
    private static String opcional(String valor) {
        return valor == null || valor.isBlank() ? null : valor.strip();
    }

    /** Formatea un valor para que sea editable en el formulario, descartando guiones o nulos. */
    private static String valorEditable(String valor) {
        return valor == null || valor.isBlank() || "—".equals(valor.strip())
                ? "" : valor.strip();
    }
}