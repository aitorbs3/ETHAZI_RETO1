package com.dm2.myapplication

import android.os.Bundle
import android.util.Log
import android.view.View
import android.widget.Toast
import androidx.appcompat.app.AppCompatActivity
import androidx.lifecycle.lifecycleScope
import com.dm2.myapplication.data.ApiClient
import com.dm2.myapplication.data.AppDatabase
import com.dm2.myapplication.data.StudentEntity
import com.dm2.myapplication.databinding.ActivityStudentDetailBinding
import com.dm2.myapplication.repository.StudentNotFoundException
import com.dm2.myapplication.repository.StudentRepository
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import retrofit2.HttpException
import java.net.ConnectException
import java.net.SocketTimeoutException
import java.net.UnknownHostException

/**
 * Pantalla de detalle de un estudiante real.
 * Obtiene los datos mediante StudentRepository, que gestiona el acceso a Room y FastAPI.
 */
class StudentDetailActivity : AppCompatActivity() {
    // View Binding permite acceder a los elementos de activity_student_detail.xml.
    private lateinit var binding: ActivityStudentDetailBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // Aplica el idioma guardado antes de cargar el diseño de la pantalla.
        LanguageManager.applySaved(this)

        // Infla el XML y conecta sus vistas con la propiedad binding.
        binding = ActivityStudentDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        // Los tres botones cierran esta pantalla y vuelven a la anterior.
        binding.btnBack.setOnClickListener { finish() }
        binding.btnSave.setOnClickListener { finish() }
        binding.btnNewSearch.setOnClickListener { finish() }

        // Muestra u oculta los botones de acción según el valor recibido desde MainActivity.
        // Si el Intent no incluye el extra, se utiliza true como valor predeterminado.
        binding.layoutActionButtons.visibility = if (
            intent.getBooleanExtra("SHOW_ACTION_BUTTONS", true)
        ) View.VISIBLE else View.GONE

        // Oculta el indicador de caché hasta que los datos del estudiante se hayan cargado.
        binding.cacheStatusChip.visibility = View.GONE

        // Inicializa la pantalla con un estado de carga y valores provisionales.
        binding.tvDetailName.text = getString(R.string.loading_student)
        StudentPhotos.load(binding.imgDetailPhoto, null)
        binding.tvDetailHouse.text = "—"
        binding.tvDetailSpecies.text = "—"
        binding.tvDetailGender.text = "—"
        binding.tvDetailBirth.text = "—"
        binding.tvDetailNationality.text = "—"
        binding.tvDetailPatronus.text = "—"

        // Recupera el identificador o texto de búsqueda enviado mediante el Intent.
        // trim() elimina espacios al principio y al final; orEmpty() evita trabajar con null.
        val query = intent.getStringExtra("EXTRA_STUDENT_ID")?.trim().orEmpty()

        // Si no se ha recibido ninguna consulta, informa al usuario y cierra la pantalla.
        if (query.isEmpty()) {
            Toast.makeText(this, getString(R.string.no_student_query), Toast.LENGTH_LONG).show()
            finish()
            return
        }

        // Con una consulta válida, inicia la carga del estudiante.
        loadStudentData(query)
    }

    private fun loadStudentData(query: String) {
        // La corrutina está ligada al ciclo de vida de esta Activity.
        lifecycleScope.launch {
            try {
                // Construye el repositorio con dos dependencias:
                // 1. El servicio Retrofit para comunicarse con FastAPI.
                // 2. El DAO de Room para consultar y guardar estudiantes localmente.
                val repository = StudentRepository(
                    ApiClient.studentService(applicationContext),
                    AppDatabase.getDatabase(applicationContext).studentDao()
                )

                // Ejecuta la operación de datos en Dispatchers.IO para no bloquear la interfaz.
                // La estrategia concreta de consulta a caché/API está implementada en el repositorio.
                val student = withContext(Dispatchers.IO) { repository.getStudent(query) }

                // Si la operación termina correctamente, muestra la información recibida.
                showStudent(student)
            } catch (e: Exception) {
                // Registra el error con información útil para depuración.
                // El detalle incluye la consulta y la URL del servidor configurado.
                Log.e(
                    "HogwartsAPI",
                    "Error al buscar el estudiante $query; servidor: ${ApiClient.baseUrl(this@StudentDetailActivity)}",
                    e
                )

                // Cambia el nombre para indicar que no se pudo completar la carga
                // y oculta el indicador que señala que hay una ficha cargada.
                binding.tvDetailName.text = getString(R.string.load_failed)
                binding.cacheStatusChip.visibility = View.GONE

                // Traduce distintos tipos de excepción a mensajes comprensibles.
                val detail = when (e) {
                    // El repositorio indica que no existe un estudiante con ese identificador.
                    is StudentNotFoundException -> getString(R.string.missing_student, query)

                    // La API respondió con un código HTTP de error, como 404 o 500.
                    is HttpException -> getString(R.string.http_error, e.code())

                    // No se pudo conectar con el servidor, resolver su nombre o completar la conexión.
                    is SocketTimeoutException, is ConnectException, is UnknownHostException ->
                        getString(R.string.network_error, ApiClient.baseUrl(this@StudentDetailActivity))

                    // Para otros errores, muestra el mensaje de la excepción o uno genérico.
                    else -> e.localizedMessage ?: getString(R.string.unknown_error)
                }

                // Muestra el error al usuario sin provocar el cierre inesperado de la aplicación.
                Toast.makeText(this@StudentDetailActivity, detail, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun showStudent(student: StudentEntity) {
        // Rellena cada campo de la interfaz con los datos guardados en la entidad de Room.
        // Si un dato opcional está vacío o es null, muestra un valor alternativo.
        binding.tvDetailName.text = student.name.ifBlank { getString(R.string.unknown_name) }
        StudentPhotos.load(binding.imgDetailPhoto, student.imageUrl)
        binding.tvDetailHouse.text = student.house ?: "—"
        binding.tvDetailSpecies.text = student.species ?: "—"
        binding.tvDetailGender.text = student.gender ?: "—"
        binding.tvDetailBirth.text = student.dateOfBirth ?: "—"
        binding.tvDetailNationality.text = student.nationality ?: "—"
        binding.tvDetailPatronus.text = student.patronus ?: "—"

        // El repositorio ha devuelto una entidad de Room; muestra el indicador de ficha cargada.
        // Esto no demuestra por sí solo que se haya consultado Internet en esta ejecución.
        binding.cacheStatusChip.visibility = View.VISIBLE
    }
}
