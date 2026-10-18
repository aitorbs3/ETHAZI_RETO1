"""
Descripción: Se encarga de la carga inicial, segura y no destructiva de las bases de datos históricas 
(Derby para Gryffindor, H2 para Hufflepuff, HSQLDB para Slytherin y Oracle para Ravenclaw).
Implementa análisis sintáctico mediante expresiones regulares (regex) para validar scripts SQL, 
comprobaciones de metadatos multiplataforma y lógica idempotente para no sobreescribir datos existentes.
"""

import logging
import os
import re
from pathlib import Path

# Importamos las funciones de conexión específicas para cada motor JDBC/nativo del sistema
from connectors.derby_connector import conectar_derby
from connectors.h2_connector import obtener_conexion_h2
from connectors.hsqldb_connector import conectar_hsqldb
from connectors.oracle_connector import conectar_oracle

# Configuramos el registrador de eventos (logger) específico para el subsistema de bootstrap del reto
logger = logging.getLogger("ethazi.bootstrap")

# Definición de rutas robustas mediante pathlib:
# Dentro de contenedores Docker los scripts SQL se ubican en /app/data/sql; en entornos locales Windows en <raiz>/data/sql.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = Path(os.environ.get("ETHAZI_SQL_DIR", PROJECT_ROOT / "data" / "sql"))

# Tupla estática que asocia cada motor con su respectivo script SQL de carga inicial (fuentes históricas de las casas)
SOURCES = (
    ("derby", "derby/cargar_gryffindor_derby.sql"),
    ("h2", "h2/cargar_hufflepuff_h2.sql"),
    ("hsqldb", "hsqldb/cargar_slytherin_hsqldb.sql"),
    ("oracle", "oracle/cargar_ravenclaw_oracle.sql"),
)


def leer_sentencias_sql(archivo: Path) -> list[str]:
    """
    Lee un archivo de script SQL, extrae las sentencias válidas (CREATE, INSERT) 
    y descarta comentarios o comandos potencialmente peligrosos (como DROP TABLE).

    Args:
        archivo (Path): Ruta al archivo de script SQL en disco.

    Returns:
        list[str]: Lista de sentencias SQL validadas y listas para ser ejecutadas.
    """
    # Leemos el contenido completo del fichero manejando marcas de orden de bytes (utf-8-sig)
    contenido = archivo.read_text(encoding="utf-8-sig")
    
    # Filtramos línea por línea eliminando aquellos comentarios que empiezan por '--'
    lineas = [
        linea for linea in contenido.splitlines()
        if not linea.lstrip().startswith("--")
    ]
    
    sin_comentarios = "\n".join(lineas)
    
    # Fragmentamos el script utilizando el punto y coma ';' como delimitador de sentencias
    sentencias = [p.strip() for p in sin_comentarios.split(";") if p.strip()]

    resultado = []
    for sentencia in sentencias:
        # 1. Seguridad: Rechazamos explícitamente comandos de borrado masivo de esquemas para proteger los datos del cliente
        if re.match(r"^DROP\s+TABLE\s+IF\s+EXISTS\s+ALUMNOS\s*$", sentencia, re.I):
            continue  # Nunca vaciar tablas con datos históricos existentes.
            
        # 2. Control transaccional: Omitimos la orden COMMIT explícita, ya que la gestión de transacciones 
        # se centraliza y controla programáticamente desde el código Python (commit/rollback).
        if re.match(r"^COMMIT\s*$", sentencia, re.I):
            continue  
            
        # 3. Validación de estructura (DDL): Permitimos exclusivamente la creación de la tabla ALUMNOS
        if re.match(r"^CREATE\s+TABLE\s+ALUMNOS\s*\(", sentencia, re.I | re.S):
            resultado.append(sentencia)
            continue
            
        # 4. Validación de datos (DML): Permitimos únicamente inserciones sobre la tabla ALUMNOS
        if re.match(r"^INSERT\s+INTO\s+ALUMNOS\s*\(", sentencia, re.I | re.S):
            resultado.append(sentencia)
            continue
            
        # Si la sentencia no coincide con ninguna regla blanca permitida, lanzamos una excepción de seguridad
        raise ValueError(f"Sentencia no permitida en {archivo.name}: {sentencia[:90]}")

    # Comprobación final: el script debe contener obligatoriamente al menos una sentencia de inserción de alumnos
    if sum(bool(re.match(r"^INSERT\s+INTO", s, re.I)) for s in resultado) == 0:
        raise ValueError(f"El script no contiene alumnos para importar: {archivo}")
        
    return resultado


def existe_tabla_alumnos(conexion, motor: str) -> bool:
    """
    Consulta los metadatos del motor de base de datos correspondiente para verificar 
    si la tabla 'ALUMNOS' ya existe físicamente, adaptándose a las particularidades de cada gestor.

    Args:
        conexion: Objeto de conexión activa a la base de datos.
        motor (str): Nombre del motor ('derby', 'h2', 'hsqldb', 'oracle').

    Returns:
        bool: True si la tabla ya existe, False en caso contrario.
    """
    # Oracle gestiona los metadatos de tablas mediante vistas del sistema (user_tables)
    if motor == "oracle":
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = 'ALUMNOS'")
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()

    # Los motores basados en JDBC (Derby, H2, HSQLDB) almacenan los nombres sin comillas 
    # en mayúsculas (ALUMNOS) y se consultan a través de DatabaseMetaData.getTables().
    tablas = conexion.jconn.getMetaData().getTables(None, None, "ALUMNOS", None)
    try:
        return bool(tablas.next())
    finally:
        tablas.close()


def conectar_fuente(motor: str):
    """
    Función factoría (Factory) que abre y devuelve una conexión activa 
    para el motor histórico indicado según los parámetros de configuración.
    """
    if motor == "derby":
        return conectar_derby(crear=True)
    if motor == "h2":
        return obtener_conexion_h2()
    if motor == "hsqldb":
        return conectar_hsqldb()
    if motor == "oracle":
        return conectar_oracle()
    raise ValueError(f"Motor de base de datos desconocido: {motor}")


# Expresión regular optimizada para extraer el ID UUID de los inserts de H2 (Hufflepuff).
# Identifica la primera columna ID y captura su valor de 36 caracteres hexadecimales con guiones.
PATRON_ID_H2 = re.compile(
    r"^INSERT\s+INTO\s+ALUMNOS\s*\(\s*ID\s*,[^)]*\)\s*"
    r"VALUES\s*\(\s*'([0-9a-fA-F-]{36})'\s*,",
    re.IGNORECASE | re.DOTALL,
)


def preparar_inserts_h2(sentencias: list[str]) -> list[tuple[str, str]]:
    """
    Extrae los pares (id, sentencia INSERT original) del script de H2 
    y detecta posibles duplicados internos antes de escribir en la base de datos.
    """
    preparados = []
    ids_script = set()
    
    for sentencia in sentencias:
        if re.match(r"^CREATE\s+TABLE", sentencia, re.IGNORECASE):
            continue
            
        coincidencia = PATRON_ID_H2.match(sentencia)
        if not coincidencia:
            raise ValueError("INSERT de H2 con formato inesperado; por seguridad no se importó nada")
            
        identificador = coincidencia.group(1).lower()
        
        # Validación de integridad: un script bien formado no puede contener IDs duplicados
        if identificador in ids_script:
            raise ValueError(f"ID duplicado detectado en el script SQL de Hufflepuff: {identificador}")
            
        ids_script.add(identificador)
        preparados.append((identificador, sentencia))
        
    return preparados


def completar_h2(conexion, cursor, sentencias: list[str], tabla_existe: bool) -> str:
    """
    Lógica específica e idempotente para H2: rellena únicamente los IDs ausentes 
    en la tabla, preservando intactos todos los registros existentes.
    """
    # Validamos y preparamos el lote completo de sentencias antes de ejecutar ninguna modificación
    preparados = preparar_inserts_h2(sentencias)

    # Si la tabla no existe en el archivo H2, ejecutamos la sentencia CREATE TABLE correspondiente
    if not tabla_existe:
        for sentencia in sentencias:
            if re.match(r"^CREATE\s+TABLE", sentencia, re.IGNORECASE):
                cursor.execute(sentencia)
                break
        else:
            raise ValueError("No se encontró ninguna sentencia CREATE TABLE válida para H2")

    # Consultamos los IDs actuales almacenados en la base de datos para garantizar idempotencia
    cursor.execute("SELECT ID FROM ALUMNOS")
    existentes = {str(fila[0]).lower() for fila in cursor.fetchall()}
    insertados = 0

    # Iteramos sobre los inserts preparados e insertamos solo aquellos cuyo ID no figure en la base de datos
    for identificador, sentencia in preparados:
        if identificador not in existentes:
            cursor.execute(sentencia)
            existentes.add(identificador)
            insertados += 1

    # Verificación de consistencia del recuento final de filas
    cursor.execute("SELECT COUNT(*) FROM ALUMNOS")
    total = int(cursor.fetchone()[0])
    if total != len(existentes):
        raise RuntimeError(
            f"Recuento H2 incoherente: se detectaron {total} filas en disco frente a {len(existentes)} IDs esperados"
        )
        
    conexion.commit()

    if insertados:
        return (f"añadidos {insertados} alumnos ausentes; "
                f"total {total} (script: {len(preparados)} IDs)")
                
    return f"la base ya contenía todos los {len(preparados)} alumnos del SQL; total {total}; sin modificaciones"


def inicializar_fuente(motor: str, script: Path) -> str:
    """
    Inicializa una fuente de datos histórica individual si se encuentra vacía,
    devolviendo un resumen textual legible del estado de la operación.
    """
    # 1. Validación previa: analizamos y validamos todo el script SQL ANTES de abrir conexiones o modificar tablas
    sentencias = leer_sentencias_sql(script)
    
    # 2. Apertura de conexión específica para el motor
    conexion = conectar_fuente(motor)
    cursor = None
    
    try:
        cursor = conexion.cursor()
        tabla_existe = existe_tabla_alumnos(conexion, motor)
        
        # El motor H2 utiliza una estrategia especializada de completado idempotente por ID
        if motor == "h2":
            return completar_h2(conexion, cursor, sentencias, tabla_existe)

        # Para los demás motores (Derby, HSQLDB, Oracle), si la tabla ya existe y contiene registros, no se modifica
        if tabla_existe:
            cursor.execute("SELECT COUNT(*) FROM alumnos")
            cantidad = int(cursor.fetchone()[0])
            if cantidad > 0:
                # Nota técnica: Apache Derby requiere cerrar la conexión con commit explícito 
                # si hubo un SELECT previo, aunque no se hayan ejecutado escrituras DML.
                conexion.commit()
                return f"la base ya contenía {cantidad} alumnos; no se ha modificado"

        # Si la tabla no existía o estaba vacía, procedemos a ejecutar el DDL (creación) y el DML (inserciones)
        insertados = 0
        for sentencia in sentencias:
            if re.match(r"^CREATE\s+TABLE", sentencia, re.I):
                if not tabla_existe:
                    cursor.execute(sentencia)
                    tabla_existe = True
            else:
                cursor.execute(sentencia)
                insertados += 1

        # Verificación de integridad post-inserción
        cursor.execute("SELECT COUNT(*) FROM alumnos")
        total = int(cursor.fetchone()[0])
        if total != insertados:
            raise RuntimeError(
                f"Recuento inesperado en {motor}: se esperaban {insertados} registros pero la BD reporta {total}"
            )
            
        conexion.commit()
        return f"importados {insertados} alumnos correctamente"
        
    except Exception:
        # En caso de cualquier fallo durante el proceso, revertimos la transacción atómica (Rollback)
        conexion.rollback()
        raise
        
    finally:
        # Bloque de liberación segura de recursos de base de datos
        if cursor is not None:
            cursor.close()
        conexion.close()


def inicializar_bases_historicas() -> dict[str, str]:
    """
    Orquesta la inicialización de todas las bases de datos históricas de forma aislada e independiente.
    Aplica tolerancia a fallos: si una fuente histórica falla al arrancar, las demás continúan inicializándose.

    Returns:
        dict[str, str]: Diccionario que mapea cada motor con el resultado o mensaje de error obtenido.
    """
    estados = {}
    
    for motor, relativa in SOURCES:
        try:
            mensaje = inicializar_fuente(motor, SQL_DIR / relativa)
            estados[motor] = mensaje
            logger.warning("[BOOTSTRAP] %s: %s", motor, mensaje)
            
        except Exception as error:
            # Captura defensiva por motor: un fallo en Derby o Oracle no tumba el arranque general de la API
            estados[motor] = f"ERROR: {error}"
            logger.exception("[BOOTSTRAP] No se pudo inicializar la fuente histórica para %s", motor)
            
    return estados