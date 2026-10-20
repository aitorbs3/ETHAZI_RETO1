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
    private var lastSearchUiGeneration = 0

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

    /** Indica si realmente hay datos guardados en Room para consulta sin conexión. */
    private fun showCacheStatus(available: Boolean, forStudent: Boolean) {
        binding.tvCacheTitle.setText(
            if (available) R.string.local_cache_enabled else R.string.local_cache_unavailable
        )
        binding.tvCacheDescription.setText(
            when {
                available -> R.string.offline_available
                forStudent -> R.string.offline_student_unavailable
                else -> R.string.offline_unavailable
            }
        )
        binding.cacheStatusIndicator.setBackgroundResource(
            if (available) R.drawable.shape_green_dot else R.drawable.shape_gray_dot
        )
    }

    private fun updateLastSearchUI() {
        val query = lastSearch()
        val generation = ++lastSearchUiGeneration
        binding.tvLastSearchId.text = query.ifEmpty { getString(R.string.no_past_search) }
        binding.cardLastSearch.isEnabled = query.isNotEmpty()

        // El estado verde solo se muestra tras verificar la persistencia en Room.
        showCacheStatus(available = false, forStudent = query.isNotEmpty())

        // Evitar mostrar al alumno ficticio de la maqueta como si existiera.
        binding.tvPreviewName.text = getString(R.string.no_preview)
        binding.tvPreviewId.text = "—"
        binding.tvPreviewSource.text = "—"
        binding.tvPreviewPatronus.text = "—"
        binding.cardStudentPreview.isEnabled = false
        binding.cardStudentPreview.alpha = 0.75f
        StudentPhotos.load(binding.imgPreview, null)

        lifecycleScope.launch {
            try {
                val (student, cacheAvailable) = withContext(Dispatchers.IO) {
                    val dao = AppDatabase.getDatabase(applicationContext).studentDao()
                    if (query.isEmpty()) {
                        Pair<StudentEntity?, Boolean>(null, dao.hasCachedStudents())
                    } else {
                        val selectedId = getSharedPreferences("hogwarts_prefs", MODE_PRIVATE)
                            .getString("LAST_STUDENT_ID", null)
                        val cached = selectedId?.let { dao.getStudentById(it) }
                            ?: dao.getStudentById(query)
                            ?: dao.getStudentByName(query)
                        Pair(cached, cached != null)
                    }
                }
                // La respuesta de una búsqueda anterior no debe sobrescribir la actual.
                if (generation != lastSearchUiGeneration || query != lastSearch()) return@launch
                showCacheStatus(available = cacheAvailable, forStudent = query.isNotEmpty())
                if (student != null) showCachedPreview(student)
            } catch (e: Exception) {
                Log.e("HogwartsCache", "No se pudo consultar la caché local", e)
                if (generation == lastSearchUiGeneration) {
                    showCacheStatus(available = false, forStudent = query.isNotEmpty())
                }
            }
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
     * Busca todas las coincidencias en FastAPI. Nunca elige arbitrariamente la primera
     * si varias personas comparten nombre o coinciden con el texto introducido.
     */
    private fun searchStudents(query: String, showButtons: Boolean) {
        val cleanQuery = query.trim()
        if (cleanQuery.isEmpty()) return
        saveLastSearch(cleanQuery)
        binding.btnSearch.isEnabled = false

        lifecycleScope.launch {
            try {
                val students = withContext(Dispatchers.IO) {
                    val service = ApiClient.studentService(applicationContext)
                    val matchesFromServer = if (UUID_REGEX.matches(cleanQuery)) {
                        listOf(service.getStudentById(cleanQuery))
                    } else {
                        // El endpoint /students puede responder solo desde la caché.
                        // Para no ocultar homónimos, combinar también las cuatro casas.
                        val matches = mutableListOf<Student>()
                        var answered = 0
                        var firstError: Exception? = null
                        try {
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

                    matchesFromServer
                        .filter { student ->
                            student.id.isNotBlank() && (
                                    UUID_REGEX.matches(cleanQuery) ||
                                            student.name?.contains(
                                                cleanQuery,
                                                ignoreCase = true
                                            ) == true
                                    )
                        }
                        .distinctBy { it.id }

                }
                when (students.size) {

                    0 -> AlertDialog.Builder(this@MainActivity)
                        .setTitle(R.string.student_not_found)
                        .setMessage(
                            getString(R.string.no_students, cleanQuery)
                        )
                        .setPositiveButton(android.R.string.ok, null)
                        .show()

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
                // Limpiar solo si la búsqueda manual terminó con un alumno elegido
                // y guardado correctamente; mantener el texto si falla o se cancela.
                if (showButtons) binding.etSearchQuery.text?.clear()
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
