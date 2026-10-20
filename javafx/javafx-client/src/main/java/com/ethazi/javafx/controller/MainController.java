package com.ethazi.javafx.controller;

import com.ethazi.javafx.AppInfo;
import com.ethazi.javafx.model.Student;
import com.ethazi.javafx.model.NuevoAlumno;
import com.ethazi.javafx.service.ApiService;
import com.ethazi.javafx.i18n.I18n;
import javafx.animation.PauseTransition;
import javafx.application.Platform;
import javafx.beans.property.ReadOnlyStringWrapper;
import javafx.collections.FXCollections;
import javafx.collections.ListChangeListener;
import javafx.collections.ObservableList;
import javafx.collections.transformation.FilteredList;
import javafx.collections.transformation.SortedList;
import javafx.fxml.FXML;
import javafx.fxml.FXMLLoader;
import javafx.scene.control.Alert;
import javafx.scene.control.Button;
import javafx.scene.control.ComboBox;
import javafx.scene.control.Label;
import javafx.scene.control.TableColumn;
import javafx.scene.control.TableView;
import javafx.scene.control.TextField;
import javafx.scene.control.TextArea;
import javafx.scene.control.ButtonType;
import javafx.scene.control.ButtonBar;
import javafx.scene.control.Dialog;
import javafx.scene.control.Tooltip;
import javafx.scene.layout.HBox;
import javafx.scene.layout.BorderPane;
import javafx.scene.layout.FlowPane;
import javafx.geometry.Insets;
import javafx.geometry.Pos;
import javafx.scene.layout.VBox;
import javafx.scene.layout.Priority;
import javafx.scene.layout.Region;
import javafx.scene.Parent;
import javafx.scene.Scene;
import javafx.scene.Node;
import javafx.scene.input.KeyCode;
import javafx.scene.input.KeyCodeCombination;
import javafx.scene.input.KeyCombination;
import javafx.stage.Stage;
import javafx.stage.Window;
import javafx.scene.image.Image;
import javafx.scene.image.ImageView;
import javafx.scene.shape.Rectangle;
import javafx.util.Duration;

import java.io.ByteArrayInputStream;
import java.io.IOException;
import java.net.URI;
import java.net.http.HttpClient;
import java.net.http.HttpRequest;
import java.net.http.HttpResponse;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Locale;
import java.util.Map;
import java.util.Optional;
import java.util.Objects;

/**
 * Pantalla principal: consulta asíncrona a FastAPI y visualización de resultados.
 * Permite crear, editar y eliminar alumnos nuevos de Hogwarths.
 */
public class MainController {

    @FXML private BorderPane rootPane;
    @FXML private HBox headerRow;
    @FXML private VBox headerTitle;
    @FXML private VBox headerControls;
    @FXML private Region headerSpacer;
    @FXML private VBox footerBox;
    @FXML private HBox footerRow;
    @FXML private Region footerSpacer;
    @FXML private VBox mainCenter;
    @FXML private HBox searchRow;
    @FXML private HBox contentRow;
    @FXML private VBox searchBox;
    @FXML private VBox filterBox;
    @FXML private VBox tableCard;
    @FXML private VBox detailCard;
    @FXML private TextField searchField;
    @FXML private Button addButton;
    @FXML private Button editButton;
    @FXML private Button deleteButton;
    @FXML private Button refreshButton;
    @FXML private Button helpButton;
    @FXML private Button aboutButton;
    @FXML private Label appInfoLabel;
    @FXML private ComboBox<String> houseCombo;
    @FXML private ComboBox<String> languageCombo;
    @FXML private TableView<Student> studentsTable;
    @FXML private TableColumn<Student, String> nameColumn;
    @FXML private TableColumn<Student, String> houseColumn;
    @FXML private TableColumn<Student, String> speciesColumn;
    @FXML private TableColumn<Student, String> genderColumn;
    @FXML private TableColumn<Student, String> birthColumn;
    @FXML private TableColumn<Student, String> nationalityColumn;
    @FXML private TableColumn<Student, String> patronusColumn;
    @FXML private Label detailName;
    @FXML private Label detailHouse;
    @FXML private Label detailSpecies;
    @FXML private Label detailGender;
    @FXML private Label detailNationality;
    @FXML private Label detailPatronus;
    @FXML private Label detailBirth;
    @FXML private Label detailInitials;
    @FXML private ImageView detailImage;
    @FXML private Label countLabel;
    @FXML private Label statusLabel;

    // En ventanas estrechas, filtros y ficha se colocan debajo del listado.
    private final VBox compactSearchRow = new VBox(12);
    private final VBox compactContentRow = new VBox(16);
    private boolean vistaCompacta = false;
    private boolean cabeceraCompacta = false;
    private boolean pieCompacto = false;
    private final VBox compactHeader = new VBox(10);
    private final FlowPane compactFooter = new FlowPane(10, 8);
    private double fuenteBase = 15.0;
    private final ApiService apiService = new ApiService();
    private final ObservableList<Student> estudiantes = FXCollections.observableArrayList();
    private final FilteredList<Student> filtrados = new FilteredList<>(estudiantes);
    private final PauseTransition esperaBusqueda = new PauseTransition(Duration.millis(450));
    private long versionConsulta = 0;
    private boolean borrandoAlumno = false;
    private boolean editandoAlumno = false;
    private String seleccionarIdTrasRecarga = null;

    // Descargar imágenes en segundo plano, sin bloquear la ventana.
    private static final HttpClient CLIENTE_IMAGENES = HttpClient.newBuilder()
            .connectTimeout(java.time.Duration.ofSeconds(10))
            .followRedirects(HttpClient.Redirect.NORMAL)
            .build();

    // Evitar descargar de nuevo las fotografías que ya se han mostrado.
    private final Map<String, Image> cacheImagenes = new HashMap<>();

    @FXML
    private void initialize() {
        nameColumn.setCellValueFactory(row -> new ReadOnlyStringWrapper(row.getValue().getNombre()));
        houseColumn.setCellValueFactory(row -> new ReadOnlyStringWrapper(row.getValue().getCasa()));
        speciesColumn.setCellValueFactory(row -> new ReadOnlyStringWrapper(mostrarValor(row.getValue().getEspecie())));
        genderColumn.setCellValueFactory(row -> new ReadOnlyStringWrapper(mostrarValor(row.getValue().getGenero())));
        birthColumn.setCellValueFactory(row -> new ReadOnlyStringWrapper(row.getValue().getFechaNacimiento()));
        nationalityColumn.setCellValueFactory(row -> new ReadOnlyStringWrapper(mostrarValor(row.getValue().getNacionalidad())));
        patronusColumn.setCellValueFactory(row -> new ReadOnlyStringWrapper(mostrarValor(row.getValue().getPatronus())));

        // Solo traducimos la interfaz. Los datos de las bases se muestran sin traducir.
        // Columnas adaptables: el ancho se distribuye sin salirse de la tabla.
        studentsTable.setColumnResizePolicy(TableView.CONSTRAINED_RESIZE_POLICY_ALL_COLUMNS);
        nameColumn.setMinWidth(85);
        houseColumn.setMinWidth(65);
        speciesColumn.setMinWidth(65);
        genderColumn.setMinWidth(75);
        birthColumn.setMinWidth(90);
        nationalityColumn.setMinWidth(100);
        patronusColumn.setMinWidth(85);

        nameColumn.setPrefWidth(200);
        houseColumn.setPrefWidth(100);
        speciesColumn.setPrefWidth(105);
        genderColumn.setPrefWidth(110);
        birthColumn.setPrefWidth(125);
        nationalityColumn.setPrefWidth(165);
        patronusColumn.setPrefWidth(140);

        // Recolocar los paneles al redimensionar o maximizar la ventana.
        rootPane.widthProperty().addListener((obs, anterior, nuevo) ->
                adaptarVista(nuevo.doubleValue()));
        Platform.runLater(() -> adaptarVista(rootPane.getWidth()));

        languageCombo.setItems(FXCollections.observableArrayList(
                "Euskara", "Castellano", "English"));
        int indiceIdioma = switch (I18n.language()) {
            case "eu" -> 0;
            case "en" -> 2;
            default -> 1;
        };
        languageCombo.getSelectionModel().select(indiceIdioma);

        houseCombo.setItems(FXCollections.observableArrayList(
                I18n.tr("filter.all"), "Gryffindor", "Hufflepuff", "Ravenclaw",
                "Slytherin", "Hogwarths"));
        houseCombo.getSelectionModel().selectFirst();

        // Redondea las esquinas de las imágenes para que encajen en el avatar.
        Rectangle recorte = new Rectangle(98, 98);
        recorte.setArcWidth(28);
        recorte.setArcHeight(28);
        detailImage.setClip(recorte);

        SortedList<Student> ordenados = new SortedList<>(filtrados);
        ordenados.comparatorProperty().bind(studentsTable.comparatorProperty());
        studentsTable.setItems(ordenados);

        esperaBusqueda.setOnFinished(event -> cargarAlumnos());
        searchField.textProperty().addListener((obs, anterior, actual) -> {
            versionConsulta++; // Invalida peticiones anteriores mientras se escribe
            statusLabel.setText(I18n.tr("status.preparing"));
            esperaBusqueda.playFromStart();
        });
        houseCombo.valueProperty().addListener((obs, anterior, actual) -> aplicarFiltroCasa());
        filtrados.addListener((ListChangeListener<Student>) cambio -> actualizarContador());
        studentsTable.getSelectionModel().selectedItemProperty().addListener(
                (obs, anterior, actual) -> {
                    mostrarAlumno(actual);
                    actualizarBotonEliminar(actual);
                    actualizarBotonEditar(actual);
                }
        );
        deleteButton.setTooltip(new Tooltip(I18n.tr("button.delete.tooltip")
                + " · " + I18n.tr("shortcut.delete")));
        editButton.setTooltip(new Tooltip(I18n.tr("button.edit.tooltip")
                + " · Ctrl+E"));
        addButton.setTooltip(new Tooltip(I18n.tr("button.add.tooltip")));
        refreshButton.setTooltip(new Tooltip(I18n.tr("button.refresh.tooltip")));
        helpButton.setTooltip(new Tooltip(I18n.tr("button.help.tooltip")));
        aboutButton.setTooltip(new Tooltip(I18n.tr("button.about.tooltip")));
        searchField.setTooltip(new Tooltip(I18n.tr("search.tooltip")));
        houseCombo.setTooltip(new Tooltip(I18n.tr("filter.tooltip")));
        languageCombo.setTooltip(new Tooltip(I18n.tr("language.tooltip")));

        // Textos de ayuda utilizados también por lectores de pantalla.
        searchField.setAccessibleHelp(I18n.tr("search.tooltip"));
        studentsTable.setAccessibleHelp(I18n.tr("access.studentsTable.help"));
        houseCombo.setAccessibleHelp(I18n.tr("filter.tooltip"));
        languageCombo.setAccessibleHelp(I18n.tr("language.tooltip"));
        addButton.setAccessibleHelp(I18n.tr("button.add.tooltip"));
        editButton.setAccessibleHelp(I18n.tr("button.edit.tooltip"));
        deleteButton.setAccessibleHelp(I18n.tr("button.delete.tooltip"));

        appInfoLabel.setText(I18n.tr("info.footer", AppInfo.VERSION, AppInfo.AUTHORS));
        appInfoLabel.setAccessibleText(appInfoLabel.getText());

        // Atajos de teclado en la escena principal. Tras cambiar de idioma,
        // la nueva vista vuelve a registrarlos, sin apuntar al controlador viejo.
        studentsTable.sceneProperty().addListener((obs, anterior, escena) -> {
            if (escena != null) configurarAtajos(escena);
        });
        // Supr solo actúa cuando está enfocada la tabla, nunca el buscador.
        studentsTable.setOnKeyPressed(evento -> {
            if (evento.getCode() == KeyCode.DELETE && !deleteButton.isDisabled()) {
                handleDelete();
                evento.consume();
            }
        });
        actualizarBotonEliminar(null);
        actualizarBotonEditar(null);

        actualizarContador();
        mostrarAlumno(null);
        cargarAlumnos(); // Carga inicialmente registros locales y caché, no demos
    }

    /** Adapta el contenido al espacio horizontal disponible. */
    private void adaptarVista(double ancho) {
        if (ancho <= 0) return;

        // El cambio de tamaño puede venir del monitor, de Ubuntu/Windows
        // o de que el usuario restaure/maximice la ventana.
        adaptarCabecera(ancho);
        adaptarPie(ancho);
        adaptarColumnas(ancho);

        boolean compacta = ancho < 1100;
        if (compacta == vistaCompacta) return;
        vistaCompacta = compacta;

        if (compacta) {
            // Cambiar a una sola columna: la tabla, y luego la ficha.
            searchRow.getChildren().clear();
            compactSearchRow.getChildren().setAll(searchBox, filterBox);
            mainCenter.getChildren().set(0, compactSearchRow);
            if (!compactSearchRow.getStyleClass().contains("search-card")) {
                compactSearchRow.getStyleClass().add("search-card");
            }

            contentRow.getChildren().clear();
            compactContentRow.getChildren().setAll(tableCard, detailCard);
            mainCenter.getChildren().set(1, compactContentRow);

            detailCard.setMinWidth(0);
            detailCard.setMaxWidth(Double.MAX_VALUE);
            studentsTable.setMinHeight(340);
            studentsTable.setPrefHeight(430);
            VBox.setVgrow(compactContentRow, Priority.NEVER);
        } else {
            compactSearchRow.getChildren().clear();
            searchRow.getChildren().setAll(searchBox, filterBox);
            mainCenter.getChildren().set(0, searchRow);

            compactContentRow.getChildren().clear();
            contentRow.getChildren().setAll(tableCard, detailCard);
            mainCenter.getChildren().set(1, contentRow);

            detailCard.setMinWidth(290);
            detailCard.setMaxWidth(340);
            studentsTable.setMinHeight(280);
            studentsTable.setPrefHeight(Region.USE_COMPUTED_SIZE);
            HBox.setHgrow(tableCard, Priority.ALWAYS);
            VBox.setVgrow(contentRow, Priority.ALWAYS);
        }
    }

    /** Tamaños visuales relativos: 1em equivale a la fuente base. */
    public void aplicarFuenteBase(double emPx) {
        fuenteBase = emPx;
        double unidad = fuenteBase;
        mainCenter.setSpacing(unidad * 1.05);
        mainCenter.setPadding(new Insets(unidad * 1.15, unidad * 1.50,
                unidad * 1.05, unidad * 1.50));
        headerRow.setSpacing(unidad * 1.05);
        headerRow.setPadding(new Insets(unidad * 1.05, unidad * 1.50,
                unidad * 1.05, unidad * 1.50));
        compactHeader.setPadding(new Insets(unidad * 0.70, unidad * 1.20,
                unidad * 0.70, unidad * 1.20));
        footerBox.setSpacing(unidad * 0.60);
        footerBox.setPadding(new Insets(unidad * 0.60, unidad * 1.50,
                unidad * 0.65, unidad * 1.50));
        searchRow.setSpacing(unidad * 1.05);
        contentRow.setSpacing(unidad * 1.05);
        compactSearchRow.setSpacing(unidad * 0.70);
        compactContentRow.setSpacing(unidad * 1.05);
        compactFooter.setHgap(unidad * 0.65);
        compactFooter.setVgap(unidad * 0.45);
    }

    /** La cabecera se apila al faltar ancho; los botones quedan visibles. */
    private void adaptarCabecera(double ancho) {
        boolean compacta = ancho < 760;
        if (compacta == cabeceraCompacta) return;
        cabeceraCompacta = compacta;

        rootPane.setTop(null);
        if (compacta) {
            headerRow.getChildren().clear();
            compactHeader.getChildren().setAll(headerTitle, headerControls);
            compactHeader.setAlignment(Pos.CENTER_LEFT);
            headerControls.setAlignment(Pos.CENTER_LEFT);
            if (!compactHeader.getStyleClass().contains("app-header")) {
                compactHeader.getStyleClass().add("app-header");
            }
            rootPane.setTop(compactHeader);
        } else {
            compactHeader.getChildren().clear();
            headerRow.getChildren().setAll(headerTitle, headerSpacer, headerControls);
            headerControls.setAlignment(Pos.CENTER_RIGHT);
            HBox.setHgrow(headerSpacer, Priority.ALWAYS);
            rootPane.setTop(headerRow);
        }
    }

    /** Los botones se distribuyen en varias filas cuando no caben. */
    private void adaptarPie(double ancho) {
        boolean compacto = ancho < 790;
        if (compacto == pieCompacto) return;
        pieCompacto = compacto;

        if (compacto) {
            footerRow.getChildren().clear();
            compactFooter.getChildren().setAll(addButton, editButton,
                    deleteButton, refreshButton);
            footerBox.getChildren().set(0, compactFooter);
        } else {
            compactFooter.getChildren().clear();
            footerRow.getChildren().setAll(addButton, editButton,
                    deleteButton, footerSpacer, refreshButton);
            HBox.setHgrow(footerSpacer, Priority.ALWAYS);
            footerBox.getChildren().set(0, footerRow);
        }
    }

    /** En pantallas muy estrechas deja los datos completos en la ficha. */
    private void adaptarColumnas(double ancho) {
        boolean estrecha = ancho < 760;
        speciesColumn.setVisible(!estrecha);
        genderColumn.setVisible(!estrecha);
        nationalityColumn.setVisible(!estrecha);
        patronusColumn.setVisible(!estrecha);
        // Siempre se mantienen nombre, casa y nacimiento en la tabla.
        // La ficha sigue mostrando todos los campos sin alterar los datos.
    }

    /** Muestra el dato original sin traducirlo. */
    private static String mostrarValor(String valor) {
        return valor == null || valor.isBlank() ? "—" : valor;
    }

    /** Atajos en la ventana principal (Ctrl en Windows/Linux, Command en macOS). */
    private void configurarAtajos(Scene escena) {
        // Se limpian los aceleradores propios de la vista anterior al cambiar de idioma.
        escena.getAccelerators().clear();
        escena.getAccelerators().put(
                new KeyCodeCombination(KeyCode.F, KeyCombination.SHORTCUT_DOWN),
                () -> { searchField.requestFocus(); searchField.selectAll(); });
        escena.getAccelerators().put(
                new KeyCodeCombination(KeyCode.N, KeyCombination.SHORTCUT_DOWN),
                () -> { if (!addButton.isDisabled()) handleAdd(); });
        escena.getAccelerators().put(
                new KeyCodeCombination(KeyCode.E, KeyCombination.SHORTCUT_DOWN),
                () -> { if (!editButton.isDisabled()) handleEdit(); });
        escena.getAccelerators().put(
                new KeyCodeCombination(KeyCode.L, KeyCombination.SHORTCUT_DOWN),
                () -> { languageCombo.requestFocus(); languageCombo.show(); });
        escena.getAccelerators().put(
                new KeyCodeCombination(KeyCode.R, KeyCombination.SHORTCUT_DOWN),
                this::handleRefresh);
        escena.getAccelerators().put(
                new KeyCodeCombination(KeyCode.F1),
                this::handleHelp);
    }

    /** Ayuda en el idioma elegido, disponible con F1 o desde el pie. */
    @FXML
    private void handleHelp() {
        Dialog<Void> ayuda = new Dialog<>();
        ayuda.initOwner(studentsTable.getScene().getWindow());
        ayuda.setTitle(I18n.tr("help.title"));
        ayuda.setHeaderText(I18n.tr("help.header"));
        ButtonType cerrar = new ButtonType(I18n.tr("common.ok"), ButtonBar.ButtonData.OK_DONE);
        ayuda.getDialogPane().getButtonTypes().add(cerrar);
        TextArea contenido = new TextArea(I18n.tr("help.body"));
        contenido.setEditable(false);
        contenido.setWrapText(true);
        contenido.setPrefRowCount(16);
        contenido.setPrefColumnCount(54);
        contenido.setAccessibleText(I18n.tr("help.header"));
        ayuda.getDialogPane().setContent(contenido);
        ayuda.getDialogPane().setPrefWidth(580);
        ayuda.getDialogPane().getStyleClass().add("help-dialog");
        ayuda.getDialogPane().getStylesheets().add(Objects.requireNonNull(
                getClass().getResource("/css/styles.css")).toExternalForm());
        instalarIcono(ayuda);
        ayuda.showAndWait();
    }

    /** Información de versión y autores configurada en AppInfo.java. */
    @FXML
    private void handleAbout() {
        Alert acerca = new Alert(Alert.AlertType.INFORMATION);
        acerca.initOwner(studentsTable.getScene().getWindow());
        acerca.setTitle(I18n.tr("about.title"));
        acerca.setHeaderText(I18n.tr("about.heading"));
        acerca.setContentText(I18n.tr("about.body", AppInfo.VERSION, AppInfo.AUTHORS));
        acerca.getDialogPane().getStylesheets().add(Objects.requireNonNull(
                getClass().getResource("/css/styles.css")).toExternalForm());
        instalarIcono(acerca);
        acerca.showAndWait();
    }

    private static void instalarIcono(Dialog<?> dialogo) {
        dialogo.setOnShown(evento -> {
            Window ventana = dialogo.getDialogPane().getScene().getWindow();
            if (ventana instanceof Stage stage) {
                stage.getIcons().add(new Image(Objects.requireNonNull(
                        MainController.class.getResourceAsStream(
                                "/images/icono_hogwarts.png"))));
            }
        });
    }

    /** Hace la petición HTTP sin bloquear el hilo de JavaFX. */
    private void cargarAlumnos() {
        esperaBusqueda.stop();
        String nombre = searchField.getText() == null ? "" : searchField.getText().strip();
        long version = ++versionConsulta;

        statusLabel.setText(nombre.isEmpty()
                ? I18n.tr("status.loading")
                : I18n.tr("status.searching", nombre));

        apiService.buscarAlumnosPorNombre(nombre).whenComplete((alumnos, error) ->
                Platform.runLater(() -> {
                    if (version != versionConsulta) {
                        return; // Se escribió otra búsqueda durante la petición
                    }

                    if (error != null) {
                        estudiantes.clear();
                        mostrarAlumno(null);
                        statusLabel.setText(I18n.tr("status.queryError", mensajeError(error)));
                        return;
                    }

                    estudiantes.setAll(alumnos);
                    aplicarFiltroCasa();
                    studentsTable.getSelectionModel().clearSelection();
                    boolean seleccionado = false;
                    if (seleccionarIdTrasRecarga != null) {
                        for (Student item : studentsTable.getItems()) {
                            if (seleccionarIdTrasRecarga.equals(item.getId())) {
                                studentsTable.getSelectionModel().select(item);
                                studentsTable.scrollTo(item);
                                seleccionado = true;
                                break;
                            }
                        }
                        seleccionarIdTrasRecarga = null;
                    }
                    if (!seleccionado && !studentsTable.getItems().isEmpty()) {
                        studentsTable.getSelectionModel().selectFirst();
                    } else if (!seleccionado) {
                        mostrarAlumno(null);
                    }
                    statusLabel.setText(I18n.tr("status.finished", alumnos.size()));
                })
        );
    }

    private void aplicarFiltroCasa() {
        String casa = houseCombo.getValue();
        filtrados.setPredicate(alumno -> {
            if (casa == null || I18n.tr("filter.all").equals(casa)) {
                return true;
            }
            // Etiqueta del nuevo grupo. Permite los nombres antiguos si el
            // backend aún almacena "Hogwarts" o "Howards" en algunos registros.
            if ("Hogwarths".equalsIgnoreCase(casa)) {
                return "Hogwarths".equalsIgnoreCase(alumno.getCasa())
                        || "Hogwarts".equalsIgnoreCase(alumno.getCasa())
                        || "Howards".equalsIgnoreCase(alumno.getCasa());
            }
            return casa.equalsIgnoreCase(alumno.getCasa());
        });
        actualizarContador();

        Student seleccionado = studentsTable.getSelectionModel().getSelectedItem();
        if (seleccionado == null || !filtrados.contains(seleccionado)) {
            studentsTable.getSelectionModel().clearSelection();
            if (!studentsTable.getItems().isEmpty()) {
                studentsTable.getSelectionModel().selectFirst();
            } else {
                mostrarAlumno(null);
            }
        }
    }

    private void actualizarContador() {
        countLabel.setText(I18n.tr("students.count", filtrados.size()));
    }

    private void mostrarAlumno(Student alumno) {
        // Por defecto mostramos las iniciales; la foto se carga en segundo plano.
        detailImage.setImage(null);
        detailImage.setVisible(false);
        detailInitials.setVisible(true);

        if (alumno == null) {
            detailInitials.setText("—");
            detailName.setText(I18n.tr("detail.noSelection"));
            detailHouse.setText("—");
            detailSpecies.setText("—");
            detailGender.setText("—");
            detailBirth.setText("—");
            detailNationality.setText("—");
            detailPatronus.setText("—");
            return;
        }

        String nombre = alumno.getNombre();
        if (nombre == null || nombre.isBlank() || "—".equals(nombre)) {
            detailInitials.setText("—");
        } else {
            String[] partes = nombre.strip().split("\\s+");
            String iniciales = partes[0].substring(0, 1);
            if (partes.length > 1) {
                iniciales += partes[partes.length - 1].substring(0, 1);
            }
            detailInitials.setText(iniciales.toUpperCase(Locale.ROOT));
        }

        detailName.setText(alumno.getNombre());
        detailHouse.setText(alumno.getCasa());
        detailSpecies.setText(mostrarValor(alumno.getEspecie()));
        detailGender.setText(mostrarValor(alumno.getGenero()));
        detailBirth.setText(alumno.getFechaNacimiento());
        detailNationality.setText(mostrarValor(alumno.getNacionalidad()));
        detailPatronus.setText(mostrarValor(alumno.getPatronus()));
        mostrarFoto(alumno);
    }

    /**
     * Carga la fotografía que entrega la API. Las fotos de Fandom se solicitan
     * en formato original para evitar WebP (no compatible con JavaFX 21).
     * Si falla, deja visibles las iniciales y muestra la causa en consola.
     */
    private void mostrarFoto(Student alumno) {
        String url = alumno.getImagen();
        System.out.println("[FOTO] " + alumno.getNombre() + " -> " + url);

        if (url == null || url.isBlank() || "—".equals(url)) {
            System.out.println("[FOTO] Sin URL de imagen en el JSON de la API.");
            return;
        }
        if (!(url.startsWith("https://") || url.startsWith("http://"))) {
            System.err.println("[FOTO] URL no válida: " + url);
            return;
        }

        Image enCache = cacheImagenes.get(url);
        if (enCache != null) {
            aplicarFoto(alumno, enCache);
            return;
        }

        descargarImagen(alumno, url, urlsAlternativas(url), 0);
    }

    /** Variantes en formato original, con retroceso a la URL de origen. */
    private static List<String> urlsAlternativas(String url) {
        List<String> urls = new ArrayList<>();
        if (url.contains("static.wikia.nocookie.net/")) {
            // Fandom puede devolver WebP si no se fuerza el formato original.
            if (!url.contains("format=original")) {
                urls.add(url + (url.contains("?") ? "&" : "?") + "format=original");
            }
            if (!url.contains("/revision/")) {
                String sinConsulta = url.split("\\?", 2)[0];
                urls.add(sinConsulta + "/revision/latest?format=original");
            }
        }
        urls.add(url);
        return urls;
    }

    /**
     * Prueba las URL sin bloquear JavaFX y convierte los bytes a Image
     * solamente en el hilo de la interfaz.
     */
    private void descargarImagen(
            Student alumno, String urlOriginal, List<String> urls, int intento) {

        if (intento >= urls.size()) {
            Platform.runLater(() -> {
                if (studentsTable.getSelectionModel().getSelectedItem() == alumno) {
                    statusLabel.setText(I18n.tr("status.imageError", alumno.getNombre()));
                }
            });
            return;
        }

        String destino = urls.get(intento);
        HttpRequest peticion;
        try {
            HttpRequest.Builder builder = HttpRequest.newBuilder()
                    .uri(URI.create(destino))
                    .timeout(java.time.Duration.ofSeconds(15))
                    .header("User-Agent", "Mozilla/5.0 (compatible; ETHAZI-JavaFX/1.0)")
                    .header("Accept", "image/jpeg,image/png,image/gif,image/*;q=0.5")
                    .GET();
            if (destino.contains("static.wikia.nocookie.net/harrypotter/")) {
                builder.header("Referer", "https://harrypotter.fandom.com/");
            }
            peticion = builder.build();
        } catch (IllegalArgumentException ex) {
            System.err.println("[FOTO] URL inválida: " + destino + " -> " + ex);
            descargarImagen(alumno, urlOriginal, urls, intento + 1);
            return;
        }

        CLIENTE_IMAGENES.sendAsync(
                peticion, HttpResponse.BodyHandlers.ofByteArray()
        ).whenComplete((respuesta, error) -> {
            if (error != null) {
                System.err.println("[FOTO] Falló la descarga de " + destino + ": " + error);
                descargarImagen(alumno, urlOriginal, urls, intento + 1);
                return;
            }
            String tipo = respuesta.headers().firstValue("Content-Type").orElse("desconocido");
            if (respuesta.statusCode() != 200 || respuesta.body().length == 0) {
                System.err.println("[FOTO] HTTP " + respuesta.statusCode()
                        + ", tipo=" + tipo + ", URL=" + destino);
                descargarImagen(alumno, urlOriginal, urls, intento + 1);
                return;
            }

            Platform.runLater(() -> {
                Image foto = new Image(new ByteArrayInputStream(respuesta.body()));
                if (foto.isError()) {
                    System.err.println("[FOTO] JavaFX no pudo interpretar la imagen. "
                            + "Tipo=" + tipo + ", URL=" + destino
                            + ", causa=" + foto.getException());
                    descargarImagen(alumno, urlOriginal, urls, intento + 1);
                    return;
                }
                cacheImagenes.put(urlOriginal, foto);
                aplicarFoto(alumno, foto);
            });
        });
    }

    /** Nunca coloca la foto de un alumno sobre la ficha de otro. */
    private void aplicarFoto(Student alumno, Image foto) {
        if (studentsTable.getSelectionModel().getSelectedItem() != alumno) {
            return;
        }
        detailImage.setImage(foto);
        detailImage.setVisible(true);
        detailInitials.setVisible(false);
        System.out.println("[FOTO] Mostrada correctamente: " + alumno.getNombre());
    }

    /** Vuelve a cargar la vista con el idioma seleccionado; no cambia datos en la API. */
    @FXML
    private void handleChangeLanguage() {
        if (languageCombo == null || languageCombo.getSelectionModel().isEmpty()) return;
        String code = switch (languageCombo.getSelectionModel().getSelectedIndex()) {
            case 0 -> "eu";
            case 2 -> "en";
            default -> "es";
        };
        if (code.equals(I18n.language())) return;
        I18n.changeLanguage(code);
        try {
            FXMLLoader loader = new FXMLLoader(
                    getClass().getResource("/fxml/main.fxml"), I18n.bundle());
            Parent contenido = loader.load();
            // El arranque adapta la fuente incluso después de cambiar de idioma.
            contenido.getProperties().put("ETHAZI_CONTROLLER", loader.getController());
            Stage stage = (Stage) languageCombo.getScene().getWindow();
            stage.getScene().setRoot(contenido);
            stage.setTitle(I18n.tr("app.title"));
        } catch (IOException error) {
            mostrarAviso("No se pudo cargar el idioma: " + error.getMessage());
        }
    }

    @FXML
    private void handleRefresh() {
        cargarAlumnos(); // Repite la búsqueda actual, no recupera datos ficticios
    }

    @FXML
    private void handleAdd() {
        Optional<NuevoAlumno> datos = AlumnoFormDialog.mostrar(
                studentsTable.getScene().getWindow()
        );
        if (datos.isEmpty()) return;

        addButton.setDisable(true);
        statusLabel.setText(I18n.tr("status.saving"));
        apiService.crearAlumno(datos.get()).whenComplete((creado, error) ->
                Platform.runLater(() -> {
                    addButton.setDisable(false);
                    if (error != null) {
                        String mensaje = mensajeError(error);
                        statusLabel.setText(I18n.tr("status.saveError", mensaje));
                        Alert aviso = new Alert(Alert.AlertType.ERROR);
                        aviso.setTitle(I18n.tr("alert.addError.title"));
                        aviso.setHeaderText(I18n.tr("alert.addError.header"));
                        aviso.setContentText(mensaje);
                        aviso.showAndWait();
                        return;
                    }

                    // Mostrar al nuevo alumno incluso si había una búsqueda anterior.
                    // GET /students incluye alumnos locales según el repositorio actual.
                    searchField.clear();
                    houseCombo.setValue(AlumnoFormDialog.CASA_NUEVA);
                    cargarAlumnos();
                    statusLabel.setText(I18n.tr("status.created", creado.getNombre()));

                    Alert aviso = new Alert(Alert.AlertType.INFORMATION);
                    aviso.setTitle(I18n.tr("alert.addSuccess.title"));
                    aviso.setHeaderText(creado.getNombre());
                    aviso.setContentText(I18n.tr("alert.addSuccess.body"));
                    aviso.show();
                })
        );
    }

    @FXML
    private void handleEdit() {
        Student seleccionado = studentsTable.getSelectionModel().getSelectedItem();
        if (!esAlumnoNuevo(seleccionado)) {
            mostrarAviso(I18n.tr("alert.onlyNew.edit"));
            return;
        }

        Optional<NuevoAlumno> cambios;
        try {
            cambios = AlumnoFormDialog.mostrarEditar(
                    studentsTable.getScene().getWindow(), seleccionado);
        } catch (IllegalArgumentException error) {
            mostrarAviso(error.getMessage());
            return;
        }
        if (cambios.isEmpty()) return;

        editandoAlumno = true;
        actualizarBotonEditar(seleccionado);
        actualizarBotonEliminar(seleccionado);
        statusLabel.setText(I18n.tr("status.editing", seleccionado.getNombre()));

        apiService.actualizarAlumno(seleccionado.getId(), cambios.get())
                .whenComplete((actualizado, error) -> Platform.runLater(() -> {
                    editandoAlumno = false;
                    actualizarBotonEditar(studentsTable.getSelectionModel().getSelectedItem());
                    actualizarBotonEliminar(studentsTable.getSelectionModel().getSelectedItem());

                    if (error != null) {
                        String mensaje = mensajeError(error);
                        statusLabel.setText(I18n.tr("status.editError", mensaje));
                        Alert aviso = new Alert(Alert.AlertType.ERROR);
                        aviso.setTitle(I18n.tr("alert.editError.title"));
                        aviso.setHeaderText(I18n.tr("alert.editError.header"));
                        aviso.setContentText(mensaje);
                        aviso.showAndWait();
                        return;
                    }

                    // Mostrar el registro actualizado, aunque cambiase el nombre buscado.
                    searchField.clear();
                    houseCombo.setValue(AlumnoFormDialog.CASA_NUEVA);
                    seleccionarIdTrasRecarga = actualizado.getId();
                    cargarAlumnos();
                    statusLabel.setText(I18n.tr("status.edited", actualizado.getNombre()));
                }));
    }

    /** La interfaz solo ofrece el borrado de alumnos de la nueva casa. */
    private static boolean esAlumnoNuevo(Student alumno) {
        return alumno != null
                && "Hogwarths".equalsIgnoreCase(alumno.getCasa())
                && alumno.getId() != null
                && !alumno.getId().isBlank()
                && !"—".equals(alumno.getId());
    }

    private void actualizarBotonEditar(Student alumno) {
        editButton.setDisable(editandoAlumno || borrandoAlumno || !esAlumnoNuevo(alumno));
    }

    private void actualizarBotonEliminar(Student alumno) {
        deleteButton.setDisable(borrandoAlumno || editandoAlumno || !esAlumnoNuevo(alumno));
    }

    @FXML
    private void handleDelete() {
        Student alumno = studentsTable.getSelectionModel().getSelectedItem();
        if (!esAlumnoNuevo(alumno)) {
            mostrarAviso(I18n.tr("alert.onlyNew.delete"));
            return;
        }

        Alert confirmacion = new Alert(Alert.AlertType.CONFIRMATION);
        confirmacion.initOwner(studentsTable.getScene().getWindow());
        confirmacion.setTitle(I18n.tr("alert.deleteConfirm.title"));
        confirmacion.setHeaderText(I18n.tr("alert.deleteConfirm.header", alumno.getNombre()));
        confirmacion.setContentText(I18n.tr("alert.deleteConfirm.body"));
        javafx.scene.control.ButtonType confirmarBorrado = new javafx.scene.control.ButtonType(
                I18n.tr("button.delete"), javafx.scene.control.ButtonBar.ButtonData.OK_DONE);
        javafx.scene.control.ButtonType cancelarBorrado = new javafx.scene.control.ButtonType(
                I18n.tr("common.cancel"), javafx.scene.control.ButtonBar.ButtonData.CANCEL_CLOSE);
        confirmacion.getButtonTypes().setAll(confirmarBorrado, cancelarBorrado);
        Optional<javafx.scene.control.ButtonType> respuesta = confirmacion.showAndWait();
        if (respuesta.isEmpty() || respuesta.get() != confirmarBorrado) {
            return;
        }

        borrandoAlumno = true;
        actualizarBotonEliminar(alumno);
        actualizarBotonEditar(alumno);
        statusLabel.setText(I18n.tr("status.deleting", alumno.getNombre()));

        apiService.eliminarAlumno(alumno.getId()).whenComplete((resultado, error) ->
                Platform.runLater(() -> {
                    borrandoAlumno = false;
                    actualizarBotonEditar(studentsTable.getSelectionModel().getSelectedItem());
                    if (error != null) {
                        actualizarBotonEliminar(studentsTable.getSelectionModel().getSelectedItem());
                        String mensaje = mensajeError(error);
                        statusLabel.setText(I18n.tr("status.deleteError", mensaje));
                        Alert aviso = new Alert(Alert.AlertType.ERROR);
                        aviso.setTitle(I18n.tr("alert.deleteError.title"));
                        aviso.setHeaderText(I18n.tr("alert.deleteError.header"));
                        aviso.setContentText(mensaje);
                        aviso.showAndWait();
                        return;
                    }

                    // Quita el registro inmediatamente de la interfaz y vuelve
                    // a consultar la API para reflejar su estado real.
                    estudiantes.removeIf(item -> alumno.getId().equals(item.getId()));
                    studentsTable.getSelectionModel().clearSelection();
                    mostrarAlumno(null);
                    searchField.clear();
                    houseCombo.setValue(AlumnoFormDialog.CASA_NUEVA);
                    cargarAlumnos();
                    statusLabel.setText(I18n.tr("status.deleted", alumno.getNombre()));
                })
        );
    }

    private void mostrarPendiente(String titulo) {
        Alert alerta = new Alert(Alert.AlertType.INFORMATION);
        alerta.setTitle(I18n.tr("alert.version.title"));
        alerta.setHeaderText(titulo);
        alerta.setContentText(I18n.tr("alert.version.body"));
        alerta.showAndWait();
    }

    private void mostrarAviso(String mensaje) {
        Alert alerta = new Alert(Alert.AlertType.WARNING);
        alerta.setTitle(I18n.tr("common.attention"));
        alerta.setHeaderText(null);
        alerta.setContentText(mensaje);
        alerta.showAndWait();
    }

    private static String mensajeError(Throwable error) {
        Throwable causa = error;
        while (causa.getCause() != null) {
            causa = causa.getCause();
        }
        return causa.getMessage() == null ? causa.getClass().getSimpleName() : causa.getMessage();
    }
}
