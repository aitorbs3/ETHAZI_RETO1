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

/** Detalle de estudiantes reales: primero Room y después FastAPI. */
class StudentDetailActivity : AppCompatActivity() {
    private lateinit var binding: ActivityStudentDetailBinding

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        LanguageManager.applySaved(this)
        binding = ActivityStudentDetailBinding.inflate(layoutInflater)
        setContentView(binding.root)

        binding.btnBack.setOnClickListener { finish() }
        binding.btnSave.setOnClickListener { finish() }
        binding.btnNewSearch.setOnClickListener { finish() }
        binding.layoutActionButtons.visibility = if (
            intent.getBooleanExtra("SHOW_ACTION_BUTTONS", true)
        ) View.VISIBLE else View.GONE

        // Esta etiqueta solo será visible cuando realmente se haya cargado el alumno.
        binding.cacheStatusChip.visibility = View.GONE
        binding.tvDetailName.text = getString(R.string.loading_student)
        StudentPhotos.load(binding.imgDetailPhoto, null)
        binding.tvDetailHouse.text = "—"
        binding.tvDetailSpecies.text = "—"
        binding.tvDetailGender.text = "—"
        binding.tvDetailBirth.text = "—"
        binding.tvDetailNationality.text = "—"
        binding.tvDetailPatronus.text = "—"
        val query = intent.getStringExtra("EXTRA_STUDENT_ID")?.trim().orEmpty()
        if (query.isEmpty()) {
            Toast.makeText(this, getString(R.string.no_student_query), Toast.LENGTH_LONG).show()
            finish()
            return
        }
        loadStudentData(query)
    }

    private fun loadStudentData(query: String) {
        lifecycleScope.launch {
            try {
                val repository = StudentRepository(
                    ApiClient.studentService(applicationContext),
                    AppDatabase.getDatabase(applicationContext).studentDao()
                )
                val student = withContext(Dispatchers.IO) { repository.getStudent(query) }
                showStudent(student)
            } catch (e: Exception) {
                Log.e("HogwartsAPI", "Error al buscar el estudiante $query; servidor: ${ApiClient.baseUrl(this@StudentDetailActivity)}", e)
                binding.tvDetailName.text = getString(R.string.load_failed)
                binding.cacheStatusChip.visibility = View.GONE
                val detail = when (e) {
                    is StudentNotFoundException -> getString(R.string.missing_student, query)
                    is HttpException -> getString(R.string.http_error, e.code())
                    is SocketTimeoutException, is ConnectException, is UnknownHostException ->
                        getString(R.string.network_error, ApiClient.baseUrl(this@StudentDetailActivity))
                    else -> e.localizedMessage ?: getString(R.string.unknown_error)
                }
                Toast.makeText(this@StudentDetailActivity, detail, Toast.LENGTH_LONG).show()
            }
        }
    }

    private fun showStudent(student: StudentEntity) {
        binding.tvDetailName.text = student.name.ifBlank { getString(R.string.unknown_name) }
        StudentPhotos.load(binding.imgDetailPhoto, student.imageUrl)
        binding.tvDetailHouse.text = student.house ?: "—"
        binding.tvDetailSpecies.text = student.species ?: "—"
        binding.tvDetailGender.text = student.gender ?: "—"
        binding.tvDetailBirth.text = student.dateOfBirth ?: "—"
        binding.tvDetailNationality.text = student.nationality ?: "—"
        binding.tvDetailPatronus.text = student.patronus ?: "—"
        // El repositorio ha leído o guardado este alumno en Room.
        binding.cacheStatusChip.visibility = View.VISIBLE
    }
}
