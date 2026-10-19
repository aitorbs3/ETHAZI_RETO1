# Hogwarts Mobile - Aplicación Android (Reto 01)

Esta aplicación móvil desarrollada en Kotlin forma parte del **Reto 01: Sistema de Interconexión e Integración de Datos para Hogwarts**. Permite la integración, consulta y visualización en tiempo real de los datos de los estudiantes almacenados en el sistema unificado del colegio de magia.

---

## 📋 Características Principales

1. **Consulta de Estudiantes por ID/DNI:**
   - Permite buscar cualquier alumno ingresando su identificador o seleccionando la previsualización del último alumno consultado correctamente.
2. **Caché Local Offline (Room / SQLite):**
   - Implementa un patrón *Offline-First*. Cuando se busca un estudiante:
     1. Comprueba si la información ya existe en la base de datos local SQLite mediante **Room**.
     2. Si está en la caché local, la muestra de inmediato sin requerir conexión a internet.
     3. Si no está en caché, realiza una petición HTTP a la API REST de **FastAPI** y almacena el resultado en Room para futuras consultas sin conexión.
3. **Persistencia del Último Registro Consultador (`SharedPreferences`):**
   - Guarda el ID de la última búsqueda realizada para restaurarlo automáticamente entre reinicios o sesiones de la aplicación.
4. **Concurrencia con Corrutinas (`Dispatchers.IO`):**
   - Las llamadas a la base de datos local y a la red se ejecutan en hilos secundarios para mantener una interfaz fluida e interactiva.
5. **Gestión de Errores y Notificaciones al Usuario:**
   - Informa mediante avisos y fallbacks en caso de no disponer de conexión a internet o cuando el servidor no esté accesible.

---

## 🛠️ Arquitectura del Proyecto

El proyecto sigue una arquitectura limpia basada en capas (MVI/MVVM con Repositorio):

```
app/src/main/java/com/dm2/myapplication/
│
├── MainActivity.kt                # Pantalla principal: Búsqueda e historial
├── StudentDetailActivity.kt       # Pantalla de detalle del estudiante y carga asíncrona
│
├── model/
│   └── Student.kt                 # Modelo de datos recibido desde la API REST (Gson)
│
├── data/
│   ├── AppDatabase.kt             # Instancia Singleton de la Base de Datos Room
│   ├── StudentEntity.kt           # Tabla SQLite para el almacenamiento local
│   ├── StudentDao.kt              # Interfaz DAO para consultas e inserciones
│   └── StudentApiService.kt       # Cliente de red Retrofit para comunicarse con FastAPI
│
└── repository/
    └── StudentRepository.kt       # Coordinador del flujo de datos (Caché local + API)
```

---

## 🚀 Funcionamiento Interno del Sistema

### 1. Flujo de Búsqueda de Estudiante
```
[Usuario ingresa ID] 
       │
       ▼
[StudentRepository] ──► ¿Existe en Room (SQLite)?
       │                        │
       ├──── Sí ───────────────► [Devuelve datos de Caché Offline]
       │
       └──── No ───────────────► [Llamada HTTP a la API de FastAPI (Retrofit)]
                                       │
                                       ▼
                                [Guarda respuesta en Room]
                                       │
                                       ▼
                                [Muestra datos en Pantalla]
```

### 2. Guardado de Última Búsqueda
Cuando el usuario presiona el botón "Search", el identificador introducido se almacena mediante `SharedPreferences` con la clave `"LAST_SEARCH_ID"`. Al volver a iniciar la aplicación o regresar a la pantalla principal, este valor se carga dinámicamente en la vista de *Last Search*.

---

## 💻 Requisitos del Sistema y Requisitos Técnicos

- **Android Studio:** 2024.1 o superior
- **Compile SDK:** 37
- **Min SDK:** 24 (Android 7.0 Nougat)
- **Target SDK:** 37
- **Lenguaje:** Kotlin 2.0+
- **Librerías Clave:**
  - `androidx.room:room-runtime:2.6.1` & `room-ktx`
  - `com.squareup.retrofit2:retrofit:2.9.0` & `converter-gson`
  - `androidx.lifecycle:lifecycle-runtime-ktx`
  - `androidx.core:core-ktx:1.19.0`

---

## ⚙️ Configuración del Servidor Backend (FastAPI)

Por defecto, la aplicación intenta conectarse al servidor en la dirección:
```
http://10.0.2.2:8000/
```
*(La IP `10.0.2.2` es el alias que utiliza el Emulador de Android Studio para conectarse a `localhost` en la máquina anfitriona).*

Si utilizas un dispositivo físico, pulsa **Configurar API** en la pantalla principal y escribe `http://IP_LOCAL_DEL_PC:8000/` (la misma red Wi-Fi). Pulsa **Probar conexión** para verificar el endpoint `/health`. No hace falta modificar código Kotlin.

---

## 🧪 Ejecución de Pruebas

Para ejecutar las pruebas unitarias y verificar el estado del compilador:

```bash
./gradlew app:assembleDebug
./gradlew app:testDebugUnitTest
```

---

## 👥 Integrantes del Proyecto (Proveedor Filos)

- **Ivan Alonso Fajardo**
- **Aitor Barros Segura**
- **Carlos Mendez García**

**Curso:** 2026–2027 | **Cliente:** Hogwarts

Consulta `CORRECCIONES_CONEXION_API.md` para el diagnóstico y los cambios recientes.
