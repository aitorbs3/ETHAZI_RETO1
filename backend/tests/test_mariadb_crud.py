"""Pruebas de creación, consulta, actualización y borrado en MariaDB."""

# Importamos date para crear fechas con año, mes y día.
from datetime import date

# Importamos Path para construir rutas y trabajar con archivos.
from pathlib import Path

# Importamos la clase del conector MariaDB y la función
# que permite establecer una conexión directa con la base de datos.
from connectors.mariadb_connector import (
    MariaDBConnector,
    conectar_mariadb,
)

# Importamos el modelo Student, que representa los datos de un alumno.
from backend.models.student import Student


def ejecutar_script_sql():
    """
    Ejecuta el script SQL para crear la tabla antes de las pruebas.
    """

    # Resolvemos la ruta absoluta de este archivo y subimos dos niveles
    # para localizar la raíz del proyecto.
    # Así no dependemos del directorio desde el que se ejecute el programa.
    base_dir = Path(__file__).resolve().parents[2]

    # Construimos la ruta completa del archivo SQL que prepara la tabla.
    sql_file = (
        base_dir
        / "data"
        / "sql"
        / "mariadb"
        / "crear_tabla_mariadb.sql"
    )

    # Comprobamos que el archivo SQL exista.
    # Si no existe, lanzamos una excepción con la ruta que se ha buscado.
    if not sql_file.exists():
        raise FileNotFoundError(
            f"No se encuentra el script SQL: {sql_file}"
        )

    # Leemos el contenido del archivo SQL utilizando la codificación UTF-8.
    sql = sql_file.read_text(encoding="utf-8")

    # Establecemos una conexión con MariaDB.
    connection = conectar_mariadb()

    # Inicializamos el cursor a None para poder comprobar después
    # si se ha creado correctamente antes de cerrarlo.
    cursor = None

    try:
        # Creamos un cursor para ejecutar la sentencia SQL.
        cursor = connection.cursor()

        # Ejecutamos el contenido del archivo SQL.
        cursor.execute(sql)

        # Confirmamos los cambios realizados en la base de datos.
        connection.commit()

        # Informamos de que la preparación de la tabla ha terminado.
        print("Tabla de MariaDB preparada correctamente.")

    except Exception:
        # Si se produce un error, intentamos deshacer la transacción.
        connection.rollback()

        # Volvemos a lanzar la excepción para que el error no quede oculto.
        raise

    finally:
        # Cerramos el cursor si llegó a crearse.
        if cursor is not None:
            cursor.close()

        # Cerramos la conexión con MariaDB.
        connection.close()


def mostrar_alumno(alumno):
    """Muestra todos los datos de un alumno."""

    # Mostramos cada atributo del objeto Student.
    # Las f-strings permiten insertar los valores dentro de los textos.
    print(f"ID:           {alumno.id}")
    print(f"Nombre:       {alumno.nombre}")
    print(f"Casa:         {alumno.casa}")
    print(f"Especie:      {alumno.especie}")
    print(f"Género:       {alumno.genero}")
    print(f"Nacimiento:   {alumno.nacimiento}")
    print(f"Nacionalidad: {alumno.nacionalidad}")
    print(f"Patronus:     {alumno.patronus}")
    print(f"Imagen:       {alumno.imagen}")


def mostrar_todos_los_alumnos(connector):
    """
    Consulta y muestra todos los alumnos de MariaDB.
    """

    # Obtenemos la lista de alumnos almacenados en la base de datos.
    alumnos = connector.get_students()

    # Mostramos el número total de alumnos recuperados.
    # len() devuelve la cantidad de elementos de la colección.
    print(f"\nTotal de alumnos: {len(alumnos)}")

    # Si la lista está vacía, mostramos un mensaje y terminamos la función.
    # return evita que se ejecute el resto del método.
    if not alumnos:
        print("No hay alumnos en la tabla.")
        return

    # Recorremos los alumnos mostrando un número para cada uno.
    # enumerate() proporciona el índice y el objeto.
    # start=1 hace que la numeración comience en uno.
    for i, alumno in enumerate(alumnos, start=1):
        print(f"\n--- Alumno {i} ---")

        # Llamamos a la función que muestra todos los atributos del alumno.
        mostrar_alumno(alumno)


def probar_mariadb_crud():
    """
    Prueba añadir, leer, editar y borrar alumnos en MariaDB.
    Muestra todos los alumnos después de cada operación.
    """

    # Creamos una instancia del conector MariaDB.
    # A través de ella ejecutaremos las operaciones CRUD.
    connector = MariaDBConnector()

    # Creamos el primer objeto Student con los datos del alumno de prueba.
    alumno1 = Student(
        id="TEST001",
        nombre="Harry Potter Prueba",
        casa="Gryffindor",
        especie="Humano",
        genero="Masculino",
        nacimiento=date(1980, 7, 31),
        nacionalidad="Británica",
        patronus="Ciervo",
        imagen=None,
    )

    # Creamos otro objeto Student con los datos modificados del primer alumno.
    # Conservamos el mismo ID para actualizar el registro existente.
    alumno1_editado = Student(
        id="TEST001",
        nombre="Harry Potter Editado",
        casa="Slytherin",
        especie="Humano",
        genero="Masculino",
        nacimiento=date(1980, 7, 31),
        nacionalidad="Británica",
        patronus="Ciervo",
        imagen=None,
    )

    # Creamos el segundo objeto Student para probar las operaciones
    # con un alumno diferente.
    alumno2 = Student(
        id="TEST002",
        nombre="Hermione Granger Prueba",
        casa="Gryffindor",
        especie="Humana",
        genero="Femenino",
        nacimiento=date(1979, 9, 19),
        nacionalidad="Británica",
        patronus="Nutria",
        imagen=None,
    )

    try:
        # Mostramos el encabezado de la prueba.
        print("\n========== PRUEBA CRUD MARIADB ==========")

        # Antes de comenzar, eliminamos posibles registros de ejecuciones
        # anteriores para evitar conflictos con las claves primarias.
        connector.delete_student("TEST001")
        connector.delete_student("TEST002")

        # 1. LEER ALUMNOS
        # Consultamos y mostramos los alumnos que existen inicialmente.
        print("\n1. LEER ALUMNOS")
        mostrar_todos_los_alumnos(connector)

        # 2. AÑADIR ALUMNO 1
        # Insertamos el primer alumno en la base de datos.
        print("\n2. AÑADIR ALUMNO 1")
        connector.create_student(alumno1)

        # Mostramos un mensaje de confirmación y la lista actualizada.
        print("Alumno 1 añadido correctamente.")
        mostrar_todos_los_alumnos(connector)

        # Buscamos los alumnos cuyo nombre coincide con el nombre de prueba.
        # get_student() devuelve los resultados según la implementación
        # del conector.
        encontrados = connector.get_student("Harry Potter Prueba")

        # Comprobamos que entre los resultados aparece el ID TEST001.
        # any() devuelve True si al menos un elemento cumple la condición.
        assert any(
            estudiante.id == "TEST001"
            for estudiante in encontrados
        ), "No se ha encontrado el alumno 1."

        # 3. AÑADIR ALUMNO 2
        # Insertamos el segundo alumno.
        print("\n3. AÑADIR ALUMNO 2")
        connector.create_student(alumno2)

        # Mostramos la confirmación y todos los alumnos.
        print("Alumno 2 añadido correctamente.")
        mostrar_todos_los_alumnos(connector)

        # Buscamos al segundo alumno por su nombre.
        encontrados = connector.get_student("Hermione Granger Prueba")

        # Verificamos que el resultado contiene el ID TEST002.
        assert any(
            estudiante.id == "TEST002"
            for estudiante in encontrados
        ), "No se ha encontrado el alumno 2."

        # 4. EDITAR ALUMNO 1
        # Actualizamos los datos del alumno TEST001 utilizando su ID.
        print("\n4. EDITAR ALUMNO 1")
        connector.update_student("TEST001", alumno1_editado)

        # Mostramos la confirmación y la lista actualizada.
        print("Alumno 1 editado correctamente.")
        mostrar_todos_los_alumnos(connector)

        # Buscamos al alumno por el nuevo nombre.
        actualizados = connector.get_student("Harry Potter Editado")

        # Comprobamos dos condiciones:
        # 1. Que el ID siga siendo TEST001.
        # 2. Que la casa se haya actualizado a Slytherin.
        assert any(
            estudiante.id == "TEST001"
            and estudiante.casa == "Slytherin"
            for estudiante in actualizados
        ), "Los cambios del alumno 1 no se han guardado."

        # 5. BORRAR ALUMNO 1 POR ID
        # Eliminamos al primer alumno utilizando su identificador.
        print("\n5. BORRAR ALUMNO 1 POR ID")
        eliminado = connector.delete_student("TEST001")

        # Verificamos que el método haya confirmado la eliminación.
        # Si eliminado es False, se lanza una excepción AssertionError.
        assert eliminado, "No se ha eliminado el alumno 1 por ID."

        # Mostramos la confirmación y los alumnos restantes.
        print("Alumno 1 eliminado correctamente por ID.")
        mostrar_todos_los_alumnos(connector)

        # Comprobamos que el segundo alumno continúa en la tabla.
        restantes = connector.get_students()

        assert any(
            estudiante.id == "TEST002"
            for estudiante in restantes
        ), "El alumno 2 no debería haberse eliminado."

        # 6. BORRAR ALUMNO 2 POR NOMBRE
        # Eliminamos los registros cuyo nombre coincida con el indicado.
        print("\n6. BORRAR ALUMNO 2 POR NOMBRE")
        eliminados = connector.delete_student_by_name(
            "Hermione Granger Prueba"
        )

        # Comprobamos que se haya eliminado al menos un registro.
        # El método devuelve el número de alumnos eliminados.
        assert eliminados >= 1, (
            "No se ha eliminado el alumno 2 por nombre."
        )

        # Mostramos cuántos registros se han eliminado y la lista actualizada.
        print(f"Alumnos eliminados por nombre: {eliminados}")
        mostrar_todos_los_alumnos(connector)

        # Volvemos a consultar los alumnos existentes.
        restantes = connector.get_students()

        # Comprobamos que no quede ninguno de los dos alumnos de prueba.
        # La expresión estudiante.id in (...) comprueba si el ID
        # pertenece a la tupla con los identificadores de prueba.
        # not any() será True si ninguno de los registros coincide.
        assert not any(
            estudiante.id in ("TEST001", "TEST002")
            for estudiante in restantes
        ), "Todavía queda algún alumno de prueba."

        # Si todas las comprobaciones anteriores pasan, mostramos el mensaje.
        print("\nTODAS LAS PRUEBAS CRUD HAN FINALIZADO CORRECTAMENTE.")

    finally:
        # Este bloque se ejecuta al terminar el try, incluso si se produce
        # una excepción. Intentamos eliminar los registros de prueba
        # para no dejar datos temporales en la base de datos.
        connector.delete_student("TEST001")
        connector.delete_student("TEST002")


# Comprobamos si este archivo se está ejecutando directamente.
# Si se importa desde otro módulo, estas funciones no se ejecutan
# automáticamente por esta condición.
if __name__ == "__main__":

    # Primero preparamos la tabla ejecutando el script SQL.
    ejecutar_script_sql()

    # Después ejecutamos las pruebas de creación, lectura,
    # actualización y eliminación de alumnos.
    probar_mariadb_crud()