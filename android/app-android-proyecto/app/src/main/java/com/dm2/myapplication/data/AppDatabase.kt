package com.dm2.myapplication.data

// Permite acceder al contexto de Android para configurar la base de datos.
import android.content.Context

// Anotación que define la configuración de la base de datos Room.
import androidx.room.Database

// Permite construir una instancia de la base de datos Room.
import androidx.room.Room

// Clase base de la que heredan las bases de datos de Room.
import androidx.room.RoomDatabase

// Permite definir migraciones entre distintas versiones de la base de datos.
import androidx.room.migration.Migration

// Proporciona acceso a la base de datos SQLite para ejecutar operaciones SQL.
import androidx.sqlite.db.SupportSQLiteDatabase

/**
 * Base de datos local de la aplicación, gestionada mediante Room.
 *
 * Almacena de forma persistente los estudiantes consultados anteriormente,
 * permitiendo recuperar sus datos desde la caché local cuando sea necesario.
 *
 * Utiliza un singleton para compartir una única instancia de la base de datos.
 * Volatile y synchronized ayudan a garantizar que la instancia se gestione
 * correctamente cuando se accede a ella desde varios hilos.
 */

// Define las entidades que forman parte de la base de datos.
// En este caso, StudentEntity representa los registros de estudiantes.
// La versión 2 identifica el esquema actual de la base de datos.
// exportSchema = false indica que Room no exportará el esquema a archivos.
@Database(
    entities = [StudentEntity::class],
    version = 2,
    exportSchema = false
)
abstract class AppDatabase : RoomDatabase() {

    /**
     * Devuelve el DAO encargado de realizar las operaciones CRUD
     * sobre los registros de estudiantes.
     */
    abstract fun studentDao(): StudentDao

    // Agrupa los miembros estáticos de la clase.
    companion object {

        // Almacena la instancia única de la base de datos.
        // Volatile hace que los cambios en esta variable sean visibles
        // inmediatamente para los distintos hilos.
        @Volatile
        private var INSTANCE: AppDatabase? = null

        /**
         * Devuelve la instancia única de la base de datos.
         * Si todavía no existe, la crea.
         */
        fun getDatabase(context: Context): AppDatabase {

            // Si INSTANCE ya contiene una base de datos,
            // devuelve directamente esa instancia.
            // Si es null, ejecuta el bloque synchronized.
            return INSTANCE ?: synchronized(this) {

                // Construye la base de datos local utilizando Room.
                val instance = Room.databaseBuilder(

                    // Utiliza el contexto general de la aplicación
                    // para evitar mantener referencias innecesarias
                    // a una Activity.
                    context.applicationContext,

                    // Indica la clase que define la base de datos.
                    AppDatabase::class.java,

                    // Nombre del archivo de la base de datos SQLite.
                    "student_db",

                // Registra la migración del esquema de la versión 1 a la 2.
                ).addMigrations(object : Migration(1, 2) {

                    // Define los cambios necesarios al actualizar
                    // la base de datos de la versión 1 a la versión 2.
                    override fun migrate(db: SupportSQLiteDatabase) {

                        // Añade la columna imageUrl a la tabla de estudiantes.
                        // Los registros existentes conservan sus datos.
                        db.execSQL(
                            "ALTER TABLE students_table ADD COLUMN imageUrl TEXT"
                        )
                    }

                // Finaliza la configuración de Room y crea la instancia.
                }).build()

                // Guarda la instancia creada para reutilizarla
                // en las siguientes llamadas a getDatabase().
                INSTANCE = instance

                // Devuelve la base de datos recién creada.
                instance
            }
        }
    }
}