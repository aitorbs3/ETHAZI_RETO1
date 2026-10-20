# Documento de Decisiones Técnicas y Arquitectura — ETHAZI_RETO1

## 1. Introducción y Principios de Diseño

El sistema **ETHAZI_RETO1** se diseña bajo los principios de **desacoplamiento**, **alta disponibilidad**, **resiliencia ante fallos de red** y **soporte multiplataforma**. Para lograrlo, la arquitectura combina bases de datos relacionales heterogéneas legadas (de solo lectura) con un núcleo moderno de persistencia local y remota, expuesto mediante una API REST unificada en **FastAPI**.

---

## 2. Estrategia de Caché y Persistencia Local (`SQLite`)

- **SQLite como Caché Principal:** SQLite actúa como el punto de entrada primario para optimizar los tiempos de respuesta y reducir la carga sobre las fuentes de datos externas y la base central. Cualquier consulta de lectura debe impactar primero en SQLite si el servicio está operativo.
- **Patrón _Cache-Aside_ (Lazy Loading):** Cuando se realiza una búsqueda y el estudiante no se encuentra en SQLite, el sistema acude a las fuentes externas. Si la búsqueda individual localiza al alumno en una fuente externa, este se **persiste de manera automática y completa en SQLite**, asegurando que las sucesivas consultas sean locales.
- **Fusión en Búsquedas Múltiples:** Para consultas que devuelven conjuntos de resultados (búsquedas parciales o listados), se realiza una combinación de los datos obtenidos de múltiples fuentes, aplicando un filtrado estricto basado en el **ID del estudiante** para eliminar duplicados de forma eficiente.

---

## 3. Política de Resiliencia y Fallback de Lectura (Modo Degradado)

La arquitectura implementa un mecanismo de tolerancia a fallos ante la caída o indisponibilidad de la base de datos principal de caché (`SQLite`).

- **Restricción en Modo Degradado:** Si SQLite está caída, el sistema pasa a un modo de operación exclusivamente de **consulta (_Read-Only_)**, bloqueando las escrituras para evitar incoherencias en la caché local.
- **Orden de Búsqueda Secuencial (Fallback):** Al no disponer de SQLite, el sistema consulta las fuentes disponibles siguiendo un orden estricto de precedencia:

$$\text{MariaDB} \rightarrow \text{Oracle} \rightarrow \text{H2} \rightarrow \text{HSQLDB} \rightarrow \text{Derby}$$

- **Aislamiento de MariaDB:** En este escenario de caída de SQLite, **MariaDB no se utiliza como caché**, sino como un repositorio de consulta directa dentro de la cadena de fallback.

---

## 4. Políticas de Lectura/Escritura por Motor de Base de Datos

Para garantizar la integridad referencial y cumplir con el diseño del sistema distribuido, las responsabilidades de cada motor están acotadas de forma rígida:

- **Motores de Solo Lectura (Read-Only):** `Oracle`, `H2`, `HSQLDB` y `Derby`. Representan las fuentes históricas de las diferentes casas de Hogwarts y no admiten modificaciones desde la aplicación.
- **Motores de Lectura y Escritura (Read-Write):** `SQLite` y `MariaDB`. Son los únicos habilitados para soportar operaciones de inserción, actualización y borrado.

---

## 5. Gestión de Escrituras y Patrón _Offline-First_ (Consistencia Eventual)

Para garantizar que los usuarios puedan operar incluso ante caídas de red o interrupciones del servidor central, se implementa el patrón _Offline-First_:

- **Flujo de Modificación:** Toda operación de escritura (`CREATE`, `UPDATE`, `DELETE`) se aplica **primero en SQLite** de forma local y atómica, garantizando una respuesta inmediata al cliente.
- **Sincronización con MariaDB:** Tras la escritura local, el cambio se intenta sincronizar inmediatamente con MariaDB.
- **Tolerancia a Caídas de MariaDB (Cola de Pendientes):** Si MariaDB se encuentra caída o inaccesible, la modificación **queda encolada en SQLite** (dentro de la tabla de operaciones pendientes). SQLite mantiene el cambio de manera persistente localmente, y la aplicación alcanza un estado de **consistencia eventual** tan pronto como se restablezca la conectividad con el servidor central.

---

## 6. Desacoplamiento de Clientes y API REST Multiplataforma

- **Independencia de la Base de Datos:** Las aplicaciones clientes **no conocen ni seleccionan la base de datos** con la que interactúan. Su única interfaz de comunicación es la **API REST**.
- **Contrato Único (DTOs JSON):** La API expone endpoints estandarizados que devuelven estructuras JSON validadas mediante esquemas Pydantic, desacoplando por completo la lógica de persistencia del backend de las tecnologías cliente (`JavaFX`, `Android` y `Unity`).

---

## 7. Adaptaciones Específicas para los Clientes Multiplataforma

El diseño contempla las necesidades particulares de cada plataforma de consumo:

- **JavaFX (Desktop):** Consume los endpoints REST directamente para la gestión de escritorio, mostrando la información unificada por el Hub.
- **Android (Móvil):** Cuenta con una **capa de caché SQLite local adicional** en el propio dispositivo móvil, optimizando el rendimiento offline extremo en entornos móviles y sincronizándose con la API central.
- **Unity (Videojuego / Experiencia Interactiva):** Consume los datos de la API utilizando campos específicos del modelo de estudiante, como el campo `patronus`, para mapearlo y representarlo visualmente mediante prefabs dentro del entorno gráfico del juego.
