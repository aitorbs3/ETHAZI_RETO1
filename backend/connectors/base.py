"""Contrato común y conversión de resultados para conectores de lectura.

Este módulo define una clase base que comparten los conectores
encargados de leer datos de diferentes bases de datos.

Su objetivo es que todos los conectores devuelvan los estudiantes
utilizando el mismo modelo: Student.
"""

# ABC permite crear clases abstractas, que sirven como plantilla
# para otras clases.
# abstractmethod permite definir métodos que las clases hijas
# están obligadas a implementar.
from abc import ABC, abstractmethod

# date representa una fecha sin información de hora.
# Se utiliza para convertir las fechas devueltas por la base de datos.
from datetime import date

# Importamos el modelo Student, que representa a un estudiante
# dentro de nuestra aplicación.
from models.student import Student


class BaseConnector(ABC):
    """
    Clase base común para los conectores de bases de datos.

    Los conectores de las bases de datos históricas se utilizan
    únicamente para leer información. Las búsquedas se realizan
    por nombre.

    Al heredar de ABC, esta clase puede definir métodos abstractos
    que deberán implementar los conectores concretos.
    """

    @abstractmethod
    def _connect(self):
        """
        Establece una conexión con la base de datos.

        Es un método abstracto: cada conector debe implementar
        su propia forma de conectarse, dependiendo de la base
        de datos y del controlador utilizado.

        Por ejemplo, un conector SQLite y otro conector JDBC
        pueden necesitar implementaciones diferentes.
        """
        # La clase base no conoce ni debe depender de un controlador
        # concreto de base de datos.
        pass

    @property
    def placeholder(self) -> str:
        """
        Devuelve el marcador utilizado para los parámetros SQL.

        El valor predeterminado es '?', utilizado por muchos
        controladores de bases de datos.

        Los conectores que utilicen otro formato pueden sobrescribir
        esta propiedad en sus clases hijas.

        @property permite acceder al método como si fuera un atributo:
        connector.placeholder
        """
        # El marcador '?' es el formato predeterminado.
        return "?"

    def get_students(self) -> list[Student]:
        """
        Obtiene todos los estudiantes almacenados en la tabla alumnos.

        Devuelve una lista de objetos Student, independientemente
        del controlador concreto que utilice la base de datos.
        """

        # Solicitamos una conexión mediante el método que implementa
        # la clase hija.
        connection = self._connect()

        # Inicializamos el cursor a None para poder comprobar después
        # si se ha llegado a crear correctamente.
        cursor = None

        try:
            # El cursor permite ejecutar consultas SQL y recuperar
            # los resultados de la base de datos.
            cursor = connection.cursor()

            # Ejecutamos una consulta que obtiene todas las columnas
            # necesarias para construir los objetos Student.
            cursor.execute(
                """
                SELECT
                    id,
                    nombre,
                    casa,
                    especie,
                    genero,
                    nacimiento,
                    nacionalidad,
                    patronus,
                    imagen
                FROM alumnos
                """
            )

            # fetchall() recupera todas las filas del resultado.
            # Normalmente se reciben como tuplas o estructuras similares,
            # dependiendo del controlador utilizado.
            rows = cursor.fetchall()

            # Convertimos cada fila de la consulta en un objeto Student.
            # La comprensión de listas crea una lista con todos ellos.
            return [
                self.row_to_student(row)
                for row in rows
            ]

        finally:
            # finally se ejecuta tanto si la operación termina
            # correctamente como si se produce una excepción.
            # Así intentamos liberar los recursos utilizados.

            # Cerramos el cursor únicamente si llegó a crearse.
            if cursor is not None:
                cursor.close()

            # Cerramos la conexión con la base de datos.
            connection.close()

    def get_student(self, name: str) -> list[Student]:
        """
        Busca estudiantes cuyo nombre contenga el texto indicado.

        La búsqueda no distingue entre mayúsculas y minúsculas
        y permite coincidencias parciales.

        Devuelve una lista porque puede haber varios estudiantes
        que coincidan con el nombre buscado.
        """

        # Comprobamos que el nombre no sea una cadena vacía
        # ni contenga únicamente espacios en blanco.
        if not name or not name.strip():
            # ValueError indica que se ha recibido un valor inválido.
            raise ValueError("El nombre es obligatorio")

        # Abrimos la conexión solo después de validar el nombre,
        # evitando realizar conexiones innecesarias.
        connection = self._connect()

        # Inicializamos el cursor para poder cerrarlo de forma segura.
        cursor = None

        try:
            # Creamos el cursor que ejecutará la consulta SQL.
            cursor = connection.cursor()

            # Buscamos coincidencias parciales en la columna nombre.
            #
            # LOWER() convierte el texto a minúsculas para comparar
            # sin distinguir mayúsculas y minúsculas.
            #
            # LIKE permite realizar coincidencias mediante patrones.
            # Los símbolos % representan cualquier secuencia de
            # caracteres, incluidos cero caracteres.
            #
            # El marcador SQL se obtiene de self.placeholder para
            # permitir que cada conector utilice el formato adecuado.
            cursor.execute(
                f"""
                SELECT
                    id,
                    nombre,
                    casa,
                    especie,
                    genero,
                    nacimiento,
                    nacionalidad,
                    patronus,
                    imagen
                FROM alumnos
                WHERE LOWER(nombre) LIKE LOWER({self.placeholder})
                """,
                # Enviamos el parámetro por separado de la consulta.
                # Por ejemplo, si name es "harry", se envía "%harry%".
                #
                # strip() elimina los espacios al principio y al final.
                # La coma convierte el parámetro en una tupla de un
                # único elemento, que es el formato esperado por execute().
                (f"%{name.strip()}%",),
            )

            # Recuperamos todas las filas que coinciden con la búsqueda.
            rows = cursor.fetchall()

            # Convertimos las filas obtenidas en objetos Student.
            return [
                self.row_to_student(row)
                for row in rows
            ]

        finally:
            # Cerramos el cursor si se ha creado correctamente.
            if cursor is not None:
                cursor.close()

            # Cerramos la conexión para liberar recursos.
            connection.close()

    @staticmethod
    def row_to_student(row) -> Student:
        """
        Convierte una fila de la base de datos en un objeto Student.

        Admite dos formatos de fila:
        - Diccionario: los valores se recuperan mediante el nombre
          de cada columna.
        - Tupla: los valores se recuperan mediante su posición.

        Se espera el siguiente orden de columnas:
        id, nombre, casa, especie, genero, nacimiento,
        nacionalidad, patronus, imagen.

        @staticmethod indica que este método no necesita acceder
        a self ni al estado de una instancia de BaseConnector.
        """

        # Comprobamos si el controlador ha devuelto un diccionario.
        if isinstance(row, dict):

            # Guardamos el método get del diccionario para recuperar
            # los valores de las columnas por su nombre.
            # Si una clave no existe, get() devuelve None.
            get = row.get

            # Recuperamos la fecha de nacimiento.
            nacimiento = get("nacimiento")

            # Si la fecha existe y no es un objeto date,
            # convertimos su representación textual a una fecha.
            #
            # Por ejemplo, "2000-05-20" se convierte en date.
            # date.fromisoformat() espera una fecha ISO válida.
            if nacimiento is not None and not isinstance(
                nacimiento, date
            ):
                nacimiento = date.fromisoformat(str(nacimiento))

            # Creamos y devolvemos el objeto Student utilizando
            # los nombres de las columnas del diccionario.
            return Student(
                # Convertimos el identificador a cadena de texto.
                id=str(get("id")),

                # Recuperamos el resto de atributos por su nombre.
                nombre=get("nombre"),
                casa=get("casa"),
                especie=get("especie"),
                genero=get("genero"),
                nacimiento=nacimiento,
                nacionalidad=get("nacionalidad"),
                patronus=get("patronus"),
                imagen=get("imagen"),
            )

        # Si no es un diccionario, asumimos que la fila es una tupla
        # u otra estructura indexable con el orden esperado.

        # El nacimiento ocupa la posición 5, porque los índices
        # de Python comienzan en 0.
        nacimiento = row[5]

        # Si la fecha no es None ni es ya un objeto date,
        # la convertimos desde su representación textual.
        if nacimiento is not None and not isinstance(
            nacimiento, date
        ):
            nacimiento = date.fromisoformat(str(nacimiento))

        # Construimos el objeto Student utilizando las posiciones
        # correspondientes a las columnas del SELECT.
        return Student(
            id=str(row[0]),       # Columna id
            nombre=row[1],        # Columna nombre
            casa=row[2],          # Columna casa
            especie=row[3],       # Columna especie
            genero=row[4],        # Columna genero
            nacimiento=nacimiento,  # Columna nacimiento
            nacionalidad=row[6],  # Columna nacionalidad
            patronus=row[7],      # Columna patronus
            imagen=row[8],        # Columna imagen
        )