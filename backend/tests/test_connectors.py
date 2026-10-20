"""
Descripción: Script de pruebas automatizadas/manuales para verificar el funcionamiento
de la fábrica de conectores (Connector Factory) y las consultas de solo lectura
contra las bases de datos heterogéneas (Derby, H2, HSQLDB y Oracle) mediante JDBC.
"""

from connectors.connector_factory import get_connector

# =========================================================================
# GUÍA DE CONFIGURACIÓN Y EJECUCIÓN EN ENTORNO WINDOWS (POWERSHELL):
# Para ejecutar este script de pruebas correctamente, es necesario configurar
# las variables de entorno de Java (requerido por jaydebeapi y los drivers JDBC)
# y el PYTHONPATH del proyecto backend:
#
# $env:JAVA_HOME = "C:\Program Files\Java\jdk-21.0.12.1"
# $env:Path = "$env:JAVA_HOME\bin;$env:Path"
# $env:PYTHONPATH="backend"
#
# Ejemplos de ejecución individual por motor mediante consola:
# python -c "from connectors.connector_factory import get_connector; c=get_connector('derby'); print(c.get_student('Albus'))"
# python -c "from backend.connectors.connector_factory import get_connector; c=get_connector('h2'); print(c.get_student('Cedric'))"
# python -c "from connectors.connector_factory import get_connector; c=get_connector('hsqldb'); print(c.get_student('Salazar'))"
# python -c "from connectors.connector_factory import get_connector; c=get_connector('oracle'); print(c.get_student('Alannis'))"
# =========================================================================


def probar_conector(nombre: str, nombre_busqueda: str) -> None:
    """
    Prueba la conectividad, el listado masivo y la búsqueda específica de un conector histórico.

    Args:
        nombre (str): Nombre clave del conector a probar ('derby', 'h2', 'hsqldb', 'oracle').
        nombre_busqueda (str): Término o nombre del personaje a buscar de forma parcial.
    """
    # Imprimimos un separador visual formateado para estructurar claramente los logs de consola por cada motor.
    print("\n" + "=" * 60)
    print(f"PROBANDO CONECTOR: {nombre.upper()}")
    print("=" * 60)

    try:
        # Patrón Factory (Fábrica): solicitamos al conector centralizado la instancia correspondiente al motor indicado.
        # Gracias al polimorfismo, todos los conectores implementan la interfaz común 'BaseConnector', 
        # permitiendo invocar los mismos métodos independientemente de si la base es Derby, H2, HSQLDB u Oracle.
        connector = get_connector(nombre)

        print("\n--- get_students() ---")
        
        # Invocamos el método de lectura masiva para recuperar todos los registros de la base histórica origen.
        estudiantes = connector.get_students()

        print(f"Total de estudiantes encontrados: {len(estudiantes)}")
        print("Mostrando los primeros 20 alumnos:\n")

        # Iteramos y recortamos la lista a un máximo de 20 elementos para evitar saturar la salida por consola.
        for estudiante in estudiantes[:20]:
            print(
                f"ID: {estudiante.id} | "
                f"Nombre: {estudiante.nombre} | "
                f"Casa: {estudiante.casa}"
            )

        print("\n--- get_student() ---")
        print(f"Buscando: {nombre_busqueda}")

        # Probamos la búsqueda filtrada por nombre utilizando el método específico expuesto por el conector.
        encontrados = connector.get_student(nombre_busqueda)

        print(f"Resultados encontrados: {len(encontrados)}")

        for estudiante in encontrados:
            print(estudiante)

        print(f"\n✓ {nombre.upper()} FUNCIONA CORRECTAMENTE")

    except Exception as error:
        # Captura defensiva de errores: si falla la conexión JDBC del puente Java-Python, 
        # el driver o la consulta SQL, capturamos la excepción, mostramos el tipo exacto de error 
        # y el mensaje descriptivo sin interrumpir la ejecución de los demás motores.
        print(f"\n✗ ERROR EN {nombre.upper()}")
        print(f"Tipo de error: {type(error).__name__}")
        print(f"Mensaje: {error}")


if __name__ == "__main__":
    # Punto de entrada principal: ejecutamos secuencialmente las pruebas de conectividad y lectura
    # para cada una de las cuatro fuentes de datos históricas heterogéneas del sistema.
    
    probar_conector("derby", "Albus")     # Base de datos Apache Derby (Gryffindor)
    probar_conector("h2", "Cedric")       # Base de datos H2 (Hufflepuff)
    probar_conector("hsqldb", "Salazar")  # Base de datos HSQLDB (Slytherin)
    probar_conector("oracle", "Alannis")  # Base de datos Oracle (Ravenclaw)