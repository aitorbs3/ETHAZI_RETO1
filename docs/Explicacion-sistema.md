# ETHAZI Reto 01 — Sistema de integración de bases de datos

## 1. Descripción del proyecto

ETHAZI Reto 01 es un proyecto de integración de datos que permite trabajar con diferentes sistemas de bases de datos relacionales mediante una arquitectura común. El sistema incorpora un backend desarrollado en Python, una API REST, conectores para diferentes bases de datos y varias aplicaciones cliente que permiten consultar y gestionar la información.

El objetivo principal es centralizar la lógica de acceso a los datos, facilitar la interoperabilidad entre sistemas heterogéneos y disponer de mecanismos de persistencia que permitan conservar la información.

El proyecto incluye tres clientes diferenciados: una aplicación de escritorio desarrollada con JavaFX, una aplicación móvil para Android y una aplicación interactiva desarrollada con Unity.

## 2. Arquitectura del sistema

La solución se organiza en diferentes componentes, cada uno con una responsabilidad específica:

- **Backend y API REST:** desarrollados en Python mediante FastAPI. Gestionan las peticiones, centralizan la lógica de acceso a los datos y exponen las operaciones del sistema mediante endpoints HTTP.
- **Capa de acceso a datos:** contiene la lógica necesaria para trabajar con los distintos sistemas de bases de datos. Su objetivo es separar el acceso a los datos de la lógica de los clientes y facilitar la reutilización de operaciones.
- **Bases de datos de origen:** Apache Derby, HSQLDB, H2 y Oracle. Estos sistemas representan las diferentes fuentes de información con las que trabaja el proyecto.
- **Persistencia central:** MariaDB y SQLite permiten almacenar información en los sistemas centrales definidos para el reto.
- **Aplicación de escritorio:** desarrollada con JavaFX, proporciona una interfaz para consultar y realizar operaciones CRUD sobre las bases de datos.
- **Aplicación móvil:** desarrollada para Android. Permite consultar información y utiliza una base de datos SQLite local para almacenar datos previamente obtenidos.
- **Cliente interactivo:** desarrollado con Unity. Permite buscar estudiantes por nombre y representar visualmente el Patronus asociado mediante un prefab.
- **Docker Compose:** coordina la ejecución del backend y los servicios de bases de datos configurados en contenedores.

## 3. Tecnologías utilizadas

| Tecnología | Función dentro del proyecto |
|---|---|
| Python | Desarrollo del backend y la lógica de acceso a datos |
| FastAPI | Exposición de la API REST |
| Apache Derby | Conector de base de datos |
| HSQLDB | Conector de base de datos |
| H2 | Conector de base de datos |
| Oracle | Base de datos y conector |
| MariaDB | Sistema central de persistencia |
| SQLite | Persistencia central y almacenamiento local de Android |
| JavaFX | Interfaz de la aplicación de escritorio |
| Android | Aplicación móvil de consulta |
| Kotlin | Lenguaje utilizado en el desarrollo Android, según los componentes implementados |
| Unity | Desarrollo del cliente interactivo |
| Docker Compose | Orquestación del backend y los servicios de bases de datos |
| Git y GitHub | Control de versiones y colaboración |

## 4. Funcionamiento del backend y la API

El backend constituye el punto central de la arquitectura. Su función es gestionar las operaciones relacionadas con los datos y proporcionar una interfaz de comunicación a través de una API REST.

La API permite que los clientes se comuniquen con el sistema mediante peticiones HTTP, sin que cada aplicación tenga que implementar por su cuenta toda la lógica del backend.

La capa de acceso a datos se encarga de adaptar las operaciones a los diferentes sistemas de bases de datos. De esta manera, la lógica común puede reutilizarse y las particularidades de cada conector quedan separadas de las operaciones de servicio.

El flujo de integración de datos definido para el reto comprende las siguientes etapas:

1. **Lectura:** obtención de información desde una base de datos de origen.
2. **Tratamiento:** preparación o transformación de los datos cuando sea necesario.
3. **Persistencia:** almacenamiento de la información en el sistema central correspondiente.
4. **Consulta:** recuperación de los datos almacenados para su utilización posterior.

Esta organización separa las responsabilidades de la API, los servicios, el acceso a datos y los sistemas de persistencia.

La documentación interactiva de la API puede consultarse en `/docs` cuando el backend está en ejecución y la documentación automática está habilitada.

## 5. Sistemas de persistencia

El proyecto trabaja con distintos sistemas de bases de datos, cada uno con una función dentro de la arquitectura.

### Bases de datos de origen

- **Apache Derby**
- **HSQLDB**
- **H2**
- **Oracle**

Estos sistemas se integran mediante sus correspondientes mecanismos de acceso a datos.

### Sistemas centrales

- **MariaDB:** sistema relacional central ejecutado como servicio de base de datos.
- **SQLite:** sistema de persistencia central basado en un archivo de base de datos.

El sistema contempla la lectura de información desde las bases de origen y su almacenamiento en los sistemas centrales. La persistencia se comprueba mediante la verificación cruzada de persistencia, incluyendo la comprobación de que los datos se conservan tras reiniciar los servicios.

### Persistencia local en Android

La aplicación móvil dispone de una base de datos SQLite propia en el dispositivo. Esta base de datos permite almacenar información consultada previamente y recuperarla desde la caché local cuando corresponda.

Este mecanismo reduce la dependencia de la conexión de red para consultar datos que ya están almacenados localmente.

## 6. Aplicaciones cliente

### 6.1. Aplicación de escritorio — JavaFX

La aplicación JavaFX proporciona una interfaz gráfica para trabajar con las bases de datos del proyecto.

Sus funciones contempladas incluyen:

- Consultar información de las bases de datos disponibles.
- Crear registros.
- Leer registros existentes.
- Actualizar información.
- Eliminar registros.

Estas operaciones corresponden a las operaciones CRUD (*Create, Read, Update, Delete*).

La aplicación se distribuye como un archivo JAR empaquetado para su ejecución. La exportación se adapta al sistema operativo de destino cuando sea necesario.

### 6.2. Aplicación móvil — Android

La aplicación Android permite consultar información mediante un identificador, como el DNI, según la funcionalidad implementada.

Sus principales características son:

- Consulta de información a través del backend.
- Almacenamiento local mediante SQLite.
- Recuperación de datos previamente consultados desde la caché.
- Recuerdo del último identificador consultado.
- Presentación de los resultados en una interfaz móvil.
- Gestión de situaciones como errores de red o identificadores inexistentes.

La disponibilidad de los datos sin conexión depende de que se hayan almacenado previamente en la base de datos local.

### 6.3. Cliente interactivo — Unity

La aplicación Unity proporciona una representación visual e interactiva de la información de los estudiantes.

Permite introducir el nombre de un estudiante, realizar una consulta y representar visualmente el Patronus asociado mediante un prefab.

El cliente separa la interfaz de usuario, la gestión de datos y la representación visual para mantener una organización clara del proyecto. También contempla mensajes ante entradas inválidas, consultas sin resultados y problemas de configuración.

## 7. Ejecución del sistema con Docker Compose

Docker Compose permite iniciar conjuntamente el backend y los servicios de bases de datos definidos en la configuración del proyecto.

Para poner en marcha los servicios, se necesita Docker y Docker Compose instalados en el equipo.

Desde la carpeta raíz del repositorio, ejecutar:

```bash
docker compose up -d --build
```

Este comando construye la imagen del backend a partir de la configuración de `./backend` y arranca los servicios definidos en el archivo Compose, descargando las imágenes necesarias si no están disponibles localmente.

La configuración establece dependencias entre el backend y las bases de datos Oracle y MariaDB, utilizando comprobaciones de estado para esperar a que estos servicios estén disponibles.

Una vez iniciado el sistema, se puede comprobar la API desde el navegador:

`http://localhost:8000/docs`

Para consultar el estado de los contenedores:

```bash
docker compose ps
```

Para consultar los registros del backend:

```bash
docker compose logs backend-api
```

Para detener los servicios sin eliminar los contenedores:

```bash
docker compose stop
```

Para detener y eliminar los contenedores y la red creada por Compose:

```bash
docker compose down
```

Los volúmenes persistentes de Oracle y MariaDB se conservan al utilizar `docker compose down` sin opciones adicionales de eliminación de volúmenes.

**Importante:** Docker Compose inicia los servicios configurados, pero no genera automáticamente los ejecutables de JavaFX, el APK de Android ni la compilación de Unity. Las aplicaciones cliente deben estar previamente preparadas y distribuidas.

## 8. Configuración y datos persistentes

El sistema utiliza variables de entorno para configurar parámetros de conexión y credenciales de las bases de datos.

Los valores de configuración se gestionan mediante el archivo `.env` y la configuración de Docker Compose. El archivo debe contener los valores necesarios para las variables utilizadas por el proyecto.

No deben incluirse contraseñas reales ni otros secretos en el repositorio público. Se recomienda distribuir un archivo de ejemplo sin credenciales y mantener el archivo `.env` real fuera del control de versiones.

La configuración de Docker Compose utiliza volúmenes con diferentes propósitos:

- **`./data:/app/data`:** permite que el backend acceda a los datos ubicados en la carpeta `data` del proyecto.
- **`oracle_data`:** conserva los datos de Oracle.
- **`mariadb_data`:** conserva los datos de MariaDB.

Estos mecanismos permiten separar los datos del ciclo de vida de los contenedores y conservar la información cuando los servicios se detienen o se recrean.

## 9. Organización y mantenimiento del proyecto

El sistema se desarrolla de forma modular, separando los componentes según su responsabilidad. Esta organización facilita localizar las partes de la solución, comprender la comunicación entre ellas y mantener cada cliente de forma diferenciada.

Git y GitHub se utilizan para el control de versiones y el trabajo colaborativo. El repositorio permite registrar la evolución del desarrollo mediante commits y ramas, facilitando el seguimiento de los cambios realizados.

La documentación del proyecto complementa el código fuente e incluye la explicación de la arquitectura, los procedimientos de instalación y uso y la documentación de la API.

## 10. Objetivo final

ETHAZI Reto 01 integra diferentes tecnologías y sistemas de bases de datos en una solución común. El backend en Python centraliza la lógica de acceso a datos, la API REST facilita la comunicación con los clientes y los sistemas de persistencia permiten conservar la información.

Las aplicaciones JavaFX, Android y Unity ofrecen distintas formas de interactuar con los datos: gestión desde escritorio, consulta desde dispositivos móviles y representación visual interactiva.

La separación por capas, la reutilización de servicios, la persistencia de datos y el control de versiones constituyen los principios principales de la solución.