package com.dm2.myapplication

import android.content.Intent
import android.os.Bundle
import android.util.Log
import android.text.InputType
import android.view.View
import android.widget.EditText
import android.widget.ArrayAdapter
import android.widget.TextView
import android.widget.LinearLayout
import android.widget.Spinner
import android.widget.AdapterView
import android.widget.Toast
import androidx.appcompat.app.AlertDialog
import androidx.appcompat.app.AppCompatActivity
import androidx.core.content.edit
import androidx.lifecycle.lifecycleScope
import com.dm2.myapplication.data.ApiClient
import com.dm2.myapplication.data.AppDatabase
import com.dm2.myapplication.data.StudentEntity
import com.dm2.myapplication.databinding.ActivityMainBinding
import com.dm2.myapplication.model.Student
import com.dm2.myapplication.repository.StudentRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

class MainActivity : AppCompatActivity() {
    private lateinit var binding: ActivityMainBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LanguageManager.applySaved(this)
        binding = ActivityMainBinding.inflate(layoutInflater)
        setContentView(binding.root)
        setupLanguageSelector()
        binding.btnSearch.setOnClickListener {
            val query = binding.etSearchQuery.text.toString().trim()
            if (query.isEmpty()) {
                binding.etSearchQuery.error = getString(R.string.enter_student)
                return@setOnClickListener
            }
            searchStudents(query, showButtons = true)
        }

        binding.cardLastSearch.setOnClickListener {
            val last = lastSearch()
            if (last.isNotEmpty()) searchStudents(last, showButtons = false)
        }

        // Ya no se utiliza un ID inventado (S001): solo datos realmente guardados en Room.
        binding.cardStudentPreview.setOnClickListener {
            val realId = binding.tvPreviewId.text.toString()
            if (binding.cardStudentPreview.isEnabled && realId.isNotBlank() && realId != "—") {
                openStudentDetails(realId, showButtons = false)
            }
        }

        binding.btnServerSettings.setOnClickListener { showServerSettings() }
        binding.btnTestApi.setOnClickListener { testApiConnection() }
        binding.tvServerUrl.text = ApiClient.baseUrl(this)
        updateLastSearchUI()
    }


    private fun setupLanguageSelector() {
        val spinner = binding.spinnerLanguage

        // Adaptador con nuestro diseño personalizado
        val adapter = ArrayAdapter(
            this,
            R.layout.spinner_idioma_item,
            LanguageManager.languageLabels
        )

        // Diseño del menú desplegable
        adapter.setDropDownViewResource(
            R.layout.spinner_idioma_item
        )

        spinner.adapter = adapter

        // Recuperar el idioma seleccionado
        val selectedIndex = LanguageManager.languageTags.indexOf(
            LanguageManager.selected(this)
        )

        spinner.setSelection(selectedIndex.coerceAtLeast(0), false)

        // Detectar cambios de idioma
        spinner.onItemSelectedListener =
            object : AdapterView.OnItemSelectedListener {

                override fun onNothingSelected(
                    parent: AdapterView<*>?
                ) = Unit

                override fun onItemSelected(
                    parent: AdapterView<*>?,
                    view: View?,
                    position: Int,
                    id: Long
                ) {
                    LanguageManager.choose(
                        this@MainActivity,
                        LanguageManager.languageTags[position]
                    )
                }
            }
    }


    override fun onResume() {
        super.onResume()
        if (::binding.isInitialized) {
            binding.tvServerUrl.text = ApiClient.baseUrl(this)
            updateLastSearchUI()
        }
    }

    private fun lastSearch(): String =
        getSharedPreferences("hogwarts_prefs", MODE_PRIVATE)
            .getString("LAST_SEARCH_ID", "")?.trim().orEmpty()

    private fun saveLastSearch(query: String) {
        getSharedPreferences("hogwarts_prefs", MODE_PRIVATE)
            .edit {
                putString("LAST_SEARCH_ID", query)
                remove("LAST_STUDENT_ID")
            }
        updateLastSearchUI()
    }

    private fun updateLastSearchUI() {
        val query = lastSearch()
        binding.tvLastSearchId.text = query.ifEmpty { getString(R.string.no_past_search) }
        binding.cardLastSearch.isEnabled = query.isNotEmpty()

        // Evitar mostrar al alumno ficticio de la maqueta como si existiera.
        binding.tvPreviewName.text = getString(R.string.no_preview)
        binding.tvPreviewId.text = "—"
        binding.tvPreviewSource.text = "—"
        binding.tvPreviewPatronus.text = "—"
        binding.cardStudentPreview.isEnabled = false
        binding.cardStudentPreview.alpha = 0.75f
        StudentPhotos.load(binding.imgPreview, null)
        if (query.isEmpty()) return

        lifecycleScope.launch {
            val student = withContext(Dispatchers.IO) {
                val dao = AppDatabase.getDatabase(applicationContext).studentDao()
                val selectedId = getSharedPreferences("hogwarts_prefs", MODE_PRIVATE)
                    .getString("LAST_STUDENT_ID", null)
                selectedId?.let { dao.getStudentById(it) }
                    ?: dao.getStudentById(query)
                    ?: dao.getStudentByName(query)
            }
            // Si el usuario escribió otra búsqueda durante la consulta, descartar la anterior.
            if (query != lastSearch()) return@launch
            if (student != null) showCachedPreview(student)
        }
    }

    private fun showCachedPreview(student: StudentEntity) {
        binding.tvPreviewName.text = student.name.ifBlank { getString(R.string.unknown_name) }
        binding.tvPreviewId.text = student.id
        binding.tvPreviewSource.text = student.sourceDatabase.ifBlank { getString(R.string.unknown_source) }
        binding.tvPreviewPatronus.text = student.patronus ?: "—"
        StudentPhotos.load(binding.imgPreview, student.imageUrl)
        binding.cardStudentPreview.isEnabled = true
        binding.cardStudentPreview.alpha = 1f
    }

    /** Comprueba conectividad REAL desde Retrofit, no solo desde el navegador del emulador. */
    private fun testApiConnection() {
        binding.btnTestApi.isEnabled = false
        lifecycleScope.launch {
            try {
                val response = withContext(Dispatchers.IO) {
                    ApiClient.studentService(applicationContext).getHealth()
                }
                val message = if (response.isSuccessful) {
                    getString(R.string.api_connected)
                } else {
                    getString(R.string.api_http, response.code())
                }
                Toast.makeText(this@MainActivity, message, Toast.LENGTH_LONG).show()
            } catch (e: Exception) {
                Log.e("HogwartsAPI", "No se pudo conectar a ${ApiClient.baseUrl(this@MainActivity)}", e)
                Toast.makeText(this@MainActivity, getString(R.string.connection_error, e.localizedMessage ?: getString(R.string.unknown_error)), Toast.LENGTH_LONG).show()
            } finally {
                binding.btnTestApi.isEnabled = true
            }
        }
    }

    private fun showServerSettings() {
        val input = EditText(this).apply {
            inputType = InputType.TYPE_CLASS_TEXT or InputType.TYPE_TEXT_VARIATION_URI
            isSingleLine = true
            setText(ApiClient.baseUrl(this@MainActivity))
            setSelection(text.length)
        }
        val spacing = (20 * resources.displayMetrics.density).toInt()
        val container = LinearLayout(this).apply {
            orientation = LinearLayout.VERTICAL
            setPadding(spacing, 0, spacing, 0)
            addView(input)
        }
        val dialog = AlertDialog.Builder(this)
            .setTitle(R.string.server_title)
            .setMessage(R.string.server_hint)
            .setView(container)
            .setNegativeButton(R.string.cancel, null)
            .setPositiveButton(R.string.save_server, null)
            .create()

        dialog.setOnShowListener {
            dialog.getButton(AlertDialog.BUTTON_POSITIVE).setOnClickListener {
                try {
                    ApiClient.saveBaseUrl(this, input.text.toString())
                    binding.tvServerUrl.text = ApiClient.baseUrl(this)
                    Toast.makeText(this, getString(R.string.server_saved), Toast.LENGTH_SHORT).show()
                    dialog.dismiss()
                } catch (e: IllegalArgumentException) {
                    input.error = getString(R.string.invalid_api_url)
                }
            }
        }
        dialog.show()
    }

    /**
     * Consulta primero Room para poder encontrar alumnos ya vistos sin conexión.
     * Si no existe ninguna coincidencia local, consulta las fuentes de FastAPI
     * y GUARDA todas las coincidencias válidas, no solo la elegida.
     */
    private fun searchStudents(query: String, showButtons: Boolean) {
        val cleanQuery = query.trim()
        if (cleanQuery.isEmpty()) return
        saveLastSearch(cleanQuery)
        binding.btnSearch.isEnabled = false

        lifecycleScope.launch {
            try {
                val students = withContext(Dispatchers.IO) {
                    val dao = AppDatabase.getDatabase(applicationContext).studentDao()
                    val locallyCached = if (UUID_REGEX.matches(cleanQuery)) {
                        listOfNotNull(dao.getStudentById(cleanQuery))
                    } else {
                        dao.getStudentsByName(cleanQuery)
                    }

                    if (locallyCached.isNotEmpty()) {
                        // Alumnos ya consultados: respuesta inmediata, sin internet.
                        locallyCached.map { it.toStudentModel() }
                    } else {
                        val service = ApiClient.studentService(applicationContext)
                        val remote = if (UUID_REGEX.matches(cleanQuery)) {
                            listOf(service.getStudentById(cleanQuery))
                        } else {
                            val matches = mutableListOf<Student>()
                            var answered = 0
                            var firstError: Exception? = null
                            try {
                                // El backend puede ignorar ?nombre y devolver TODOS;
                                // por eso filtramos también en la propia aplicación.
                                matches += service.getStudents(nombre = cleanQuery)
                                answered++
                            } catch (e: Exception) {
                                firstError = e
                                Log.w("HogwartsAPI", "No responde /students para '$cleanQuery'", e)
                            }
                            for (houseSource in listOf("derby", "h2", "hsqldb", "oracle")) {
                                try {
                                    matches += service.getStudentsFromConnector(houseSource, cleanQuery)
                                    answered++
                                } catch (e: Exception) {
                                    if (firstError == null) firstError = e
                                    Log.w("HogwartsAPI", "No se pudo consultar $houseSource", e)
                                }
                            }
                            if (answered == 0) {
                                throw firstError ?: IllegalStateException("FastAPI no responde")
                            }
                            matches
                        }

                        val filtered = remote
                            .filter { student ->
                                student.id.isNotBlank() &&
                                    (UUID_REGEX.matches(cleanQuery) ||
                                        student.name.orEmpty().contains(cleanQuery, ignoreCase = true))
                            }
                            .distinctBy { it.id }
                            .sortedWith(compareBy<Student> { it.name.orEmpty().lowercase() }
                                .thenBy { it.house.orEmpty().lowercase() })

                        // Persistimos todas las fichas recibidas, aunque el usuario
                        // todavía no haya elegido una de las coincidencias.
                        val repository = StudentRepository(service, dao)
                        filtered.forEach { student -> repository.cacheStudent(student) }
                        filtered
                    }
                }

                // Actualizar vista previa tras persistir la nueva búsqueda en Room.
                updateLastSearchUI()
                when (students.size) {
                    0 -> Toast.makeText(
                        this@MainActivity,
                        getString(R.string.no_students, cleanQuery),
                        Toast.LENGTH_LONG
                    ).show()
                    1 -> openChosenStudent(students[0], showButtons)
                    else -> showStudentChoices(cleanQuery, students, showButtons)
                }
            } catch (e: Exception) {
                Log.e("HogwartsAPI", "Error al buscar '$cleanQuery' en ${ApiClient.baseUrl(this@MainActivity)}", e)
                val message = if (e is retrofit2.HttpException && e.code() == 404) {
                    getString(R.string.student_not_found)
                } else {
                    getString(R.string.search_error)
                }
                Toast.makeText(this@MainActivity, message, Toast.LENGTH_LONG).show()
            } finally {
                binding.btnSearch.isEnabled = true
            }
        }
    }

    /** Adaptar los registros locales al modelo que ya usa el selector de alumnos. */
    private fun StudentEntity.toStudentModel(): Student = Student(
        id = id,
        name = name,
        alias = alias,
        house = house,
        species = species,
        gender = gender,
        dateOfBirth = dateOfBirth,
        nationality = nationality,
        patronus = patronus,
        imagen = imageUrl,
        sourceDatabase = sourceDatabase
    )

    /** Lista desplazable con nombre completo y casa; cada posición conserva su UUID. */
    private fun showStudentChoices(query: String, students: List<Student>, showButtons: Boolean) {
        val adapter = object : ArrayAdapter<Student>(this, R.layout.item_student_choice, students) {
            override fun getView(position: Int, convertView: View?, parent: android.view.ViewGroup): View {
                val row = convertView ?: layoutInflater.inflate(R.layout.item_student_choice, parent, false)
                val student = getItem(position)!!
                row.findViewById<TextView>(R.id.tvChoiceName).text =
                    student.name?.takeIf { it.isNotBlank() } ?: getString(R.string.unknown_name)
                row.findViewById<TextView>(R.id.tvChoiceHouse).text =
                    getString(R.string.choice_house,
                        student.house?.takeIf { it.isNotBlank() } ?: getString(R.string.unknown_house))
                StudentPhotos.load(row.findViewById(R.id.imgChoicePhoto), student.imagen)
                return row
            }
        }

        AlertDialog.Builder(this)
            .setTitle(getString(R.string.choice_title, students.size, query))
            .setAdapter(adapter) { _, position ->
                openChosenStudent(students[position], showButtons)
            }
            .setNegativeButton(R.string.cancel, null)
            .show()
    }

    /** Guardar en Room la ficha elegida, incluso si vino de un conector histórico.
     * Así la siguiente pantalla abre exactamente ese UUID, sin repetir búsqueda ambigua.
     */
    private fun openChosenStudent(student: Student, showButtons: Boolean) {
        lifecycleScope.launch {
            try {
                withContext(Dispatchers.IO) {
                    val repository = StudentRepository(
                        ApiClient.studentService(applicationContext),
                        AppDatabase.getDatabase(applicationContext).studentDao()
                    )
                    repository.cacheStudent(student)
                }
                getSharedPreferences("hogwarts_prefs", MODE_PRIVATE).edit {
                    putString("LAST_STUDENT_ID", student.id)
                }
                updateLastSearchUI()
                openStudentDetails(student.id, showButtons)
            } catch (e: Exception) {
                Log.e("HogwartsAPI", "No se pudo guardar la ficha de ${student.name}", e)
                Toast.makeText(this@MainActivity, getString(R.string.cant_open_student), Toast.LENGTH_LONG).show()
            }
        }
    }

    private companion object {
        val UUID_REGEX = Regex("^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{4}-[0-9a-fA-F]{12}$")
    }

    private fun openStudentDetails(query: String, showButtons: Boolean) {
        startActivity(Intent(this, StudentDetailActivity::class.java).apply {
            putExtra("EXTRA_STUDENT_ID", query)
            putExtra("SHOW_ACTION_BUTTONS", showButtons)
        })
    }
}
