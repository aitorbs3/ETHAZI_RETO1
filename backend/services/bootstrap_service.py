"""Carga inicial no destructiva de las cuatro bases históricas.

Los SQL originales se usan como fuente de datos, pero nunca se ejecutan sus
DROP TABLE. Para H2 se completan solamente los IDs ausentes; para las demás
bases se mantiene la política de no modificar tablas que ya contienen datos.
"""

import logging
import os
import re
from pathlib import Path

from connectors.derby_connector import conectar_derby
from connectors.h2_connector import obtener_conexion_h2
from connectors.hsqldb_connector import conectar_hsqldb
from connectors.oracle_connector import conectar_oracle

logger = logging.getLogger("ethazi.bootstrap")

# Dentro de Docker los SQL están en /app/data/sql, en Windows en <raiz>/data/sql.
PROJECT_ROOT = Path(__file__).resolve().parents[2]
SQL_DIR = Path(os.environ.get("ETHAZI_SQL_DIR", PROJECT_ROOT / "data" / "sql"))

SOURCES = (
    ("derby", "derby/cargar_gryffindor_derby.sql"),
    ("h2", "h2/cargar_hufflepuff_h2.sql"),
    ("hsqldb", "hsqldb/cargar_slytherin_hsqldb.sql"),
    ("oracle", "oracle/cargar_ravenclaw_oracle.sql"),
)


def leer_sentencias_sql(archivo: Path) -> list[str]:
    """Extrae CREATE/INSERT/COMMIT, omitiendo comentarios y DROP peligrosos.

    El formato de los cuatro scripts del proyecto es: una sentencia por ';',
    sin punto y coma dentro de cadenas SQL. Rechaza comandos inesperados.
    """
    contenido = archivo.read_text(encoding="utf-8-sig")
    lineas = [
        linea for linea in contenido.splitlines()
        if not linea.lstrip().startswith("--")
    ]
    sin_comentarios = "\n".join(lineas)
    sentencias = [p.strip() for p in sin_comentarios.split(";") if p.strip()]

    resultado = []
    for sentencia in sentencias:
        if re.match(r"^DROP\s+TABLE\s+IF\s+EXISTS\s+ALUMNOS\s*$", sentencia, re.I):
            continue  # Nunca vaciar tablas con datos del cliente.
        if re.match(r"^COMMIT\s*$", sentencia, re.I):
            continue  # La transacción la gestiona el código.
        if re.match(r"^CREATE\s+TABLE\s+ALUMNOS\s*\(", sentencia, re.I | re.S):
            resultado.append(sentencia)
            continue
        if re.match(r"^INSERT\s+INTO\s+ALUMNOS\s*\(", sentencia, re.I | re.S):
            resultado.append(sentencia)
            continue
        raise ValueError(f"Sentencia no permitida en {archivo.name}: {sentencia[:90]}")

    if sum(bool(re.match(r"^INSERT\s+INTO", s, re.I)) for s in resultado) == 0:
        raise ValueError(f"El script no contiene alumnos: {archivo}")
    return resultado


def existe_tabla_alumnos(conexion, motor: str) -> bool:
    """Consulta metadatos; no confunde otros errores SQL con tabla inexistente."""
    if motor == "oracle":
        cursor = conexion.cursor()
        try:
            cursor.execute("SELECT COUNT(*) FROM user_tables WHERE table_name = 'ALUMNOS'")
            return cursor.fetchone()[0] > 0
        finally:
            cursor.close()

    # JDBC almacena los nombres sin comillas como ALUMNOS (mayúsculas).
    tablas = conexion.jconn.getMetaData().getTables(None, None, "ALUMNOS", None)
    try:
        return bool(tablas.next())
    finally:
        tablas.close()


def conectar_fuente(motor: str):
    if motor == "derby":
        return conectar_derby(crear=True)
    if motor == "h2":
        return obtener_conexion_h2()
    if motor == "hsqldb":
        return conectar_hsqldb()
    if motor == "oracle":
        return conectar_oracle()
    raise ValueError(f"Motor desconocido: {motor}")


# El SQL de Hufflepuff utiliza ID como primera columna y UUID como primer valor.
# Extraemos solo ese identificador, sin partir VALUES por comas (las cadenas
# podrían contenerlas). Si cambia el esquema del SQL, fallamos sin escribir.
PATRON_ID_H2 = re.compile(
    r"^INSERT\s+INTO\s+ALUMNOS\s*\(\s*ID\s*,[^)]*\)\s*"
    r"VALUES\s*\(\s*'([0-9a-fA-F-]{36})'\s*,",
    re.IGNORECASE | re.DOTALL,
)


def preparar_inserts_h2(sentencias: list[str]) -> list[tuple[str, str]]:
    """Extrae (id, INSERT original) y detecta duplicados antes de escribir."""
    preparados = []
    ids_script = set()
    for sentencia in sentencias:
        if re.match(r"^CREATE\s+TABLE", sentencia, re.IGNORECASE):
            continue
        coincidencia = PATRON_ID_H2.match(sentencia)
        if not coincidencia:
            raise ValueError("INSERT H2 con formato inesperado; no se importó nada")
        identificador = coincidencia.group(1).lower()
        if identificador in ids_script:
            raise ValueError(f"ID duplicado en el SQL de Hufflepuff: {identificador}")
        ids_script.add(identificador)
        preparados.append((identificador, sentencia))
    return preparados


def completar_h2(conexion, cursor, sentencias: list[str], tabla_existe: bool) -> str:
    """Rellena únicamente los IDs ausentes, preservando todos los existentes."""
    preparados = preparar_inserts_h2(sentencias)

    if not tabla_existe:
        for sentencia in sentencias:
            if re.match(r"^CREATE\s+TABLE", sentencia, re.IGNORECASE):
                cursor.execute(sentencia)
                break
        else:
            raise ValueError("No hay CREATE TABLE para H2")

    cursor.execute("SELECT ID FROM ALUMNOS")
    existentes = {str(fila[0]).lower() for fila in cursor.fetchall()}
    insertados = 0

    for identificador, sentencia in preparados:
        if identificador not in existentes:
            cursor.execute(sentencia)
            existentes.add(identificador)
            insertados += 1

    cursor.execute("SELECT COUNT(*) FROM ALUMNOS")
    total = int(cursor.fetchone()[0])
    if total != len(existentes):
        raise RuntimeError(
            f"Recuento H2 incoherente: {total} filas y {len(existentes)} IDs"
        )
    conexion.commit()

    if insertados:
        return (f"añadidos {insertados} alumnos ausentes; "
                f"total {total} (script: {len(preparados)} IDs)")
    return f"ya tenía todos los {len(preparados)} alumnos del SQL; total {total}; no se ha modificado"


def inicializar_fuente(motor: str, script: Path) -> str:
    """Inicializa una fuente si está vacía y devuelve un resumen legible."""
    # Validar todo el script ANTES de conectarse o crear tablas.
    sentencias = leer_sentencias_sql(script)
    conexion = conectar_fuente(motor)
    cursor = None
    try:
        cursor = conexion.cursor()
        tabla_existe = existe_tabla_alumnos(conexion, motor)
        if motor == "h2":
            return completar_h2(conexion, cursor, sentencias, tabla_existe)

        if tabla_existe:
            cursor.execute("SELECT COUNT(*) FROM alumnos")
            cantidad = int(cursor.fetchone()[0])
            if cantidad > 0:
                # Derby no permite cerrar una conexión con SELECT activo
                # aunque no haya habido escrituras.
                conexion.commit()
                return f"ya tenía {cantidad} alumnos; no se ha modificado"

        insertados = 0
        for sentencia in sentencias:
            if re.match(r"^CREATE\s+TABLE", sentencia, re.I):
                if not tabla_existe:
                    cursor.execute(sentencia)
                    tabla_existe = True
            else:
                cursor.execute(sentencia)
                insertados += 1

        cursor.execute("SELECT COUNT(*) FROM alumnos")
        total = int(cursor.fetchone()[0])
        if total != insertados:
            raise RuntimeError(
                f"Recuento inesperado en {motor}: {total} de {insertados} inserts"
            )
        conexion.commit()
        return f"importados {insertados} alumnos"
    except Exception:
        conexion.rollback()
        raise
    finally:
        if cursor is not None:
            cursor.close()
        conexion.close()


def inicializar_bases_historicas() -> dict[str, str]:
    """Intenta cada base por separado: si una falla las demás se inicializan."""
    estados = {}
    for motor, relativa in SOURCES:
        try:
            mensaje = inicializar_fuente(motor, SQL_DIR / relativa)
            estados[motor] = mensaje
            logger.warning("[BOOTSTRAP] %s: %s", motor, mensaje)
        except Exception as error:
            estados[motor] = f"ERROR: {error}"
            logger.exception("[BOOTSTRAP] No se pudo inicializar %s", motor)
    return estados
