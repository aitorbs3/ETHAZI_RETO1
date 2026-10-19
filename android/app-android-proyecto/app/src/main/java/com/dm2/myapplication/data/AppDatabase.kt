package com.dm2.myapplication.data

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import androidx.room.migration.Migration
import androidx.sqlite.db.SupportSQLiteDatabase

/**
 * Base de datos local Room de la aplicación.
 * 
 * Almacena de forma persistente los registros de estudiantes consultados previamente (caché offline).
 * Define un singleton seguro para multihilos (Volatile / synchronized) mediante getDatabase().
 */
@Database(entities = [StudentEntity::class], version = 2, exportSchema = false)
abstract class AppDatabase : RoomDatabase() {

    /**
     * Retorna el DAO para ejecutar operaciones CRUD sobre la tabla de estudiantes.
     */
    abstract fun studentDao(): StudentDao

    companion object {
        @Volatile
        private var INSTANCE: AppDatabase? = null

        /**
         * Devuelve la instancia única de la base de datos Room, creándola si aún no existe.
         */
        fun getDatabase(context: Context): AppDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    AppDatabase::class.java,
                    "student_db",
                ).addMigrations(object : Migration(1, 2) {
                    override fun migrate(db: SupportSQLiteDatabase) {
                        db.execSQL("ALTER TABLE students_table ADD COLUMN imageUrl TEXT")
                    }
                }).build()
                INSTANCE = instance
                instance
            }
        }
    }
}