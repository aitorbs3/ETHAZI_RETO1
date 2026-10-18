
"""Fábrica de conectores de solo lectura para las bases históricas."""

# Importamos las clases de los conectores que queremos poder crear.
# El punto inicial indica que son importaciones relativas:
# buscamos los módulos dentro del mismo paquete.
from .derby_connector import DerbyConnector
from .hsqldb_connector import HSQLDBConnector
from .h2_connector import H2Connector
from .oracle_connector import OracleConnector


def get_connector(connector_name: str):
    """
    Obtiene el conector correspondiente al nombre recibido.

    Args:
        connector_name (str): Nombre del conector que se quiere utilizar.

    Returns:
        DatabaseConnector: Instancia del conector solicitado.

    Raises:
        ValueError: Si el conector indicado no está soportado.
    """

    # Creamos un diccionario que relaciona cada nombre con su clase.
    # La clave es el nombre que se utiliza para solicitar el conector.
    # El valor es la clase que permite conectarse a esa base de datos.
    connectors = {
        "derby": DerbyConnector,
        "hsqldb": HSQLDBConnector,
        "h2": H2Connector,
        "oracle": OracleConnector
    }

    # Convertimos el nombre recibido a minúsculas para que la búsqueda
    # no distinga entre mayúsculas y minúsculas.
    # Por ejemplo, "ORACLE", "Oracle" y "oracle" se tratarán igual.
    #
    # get() devuelve la clase asociada a la clave si existe.
    # Si la clave no existe, devuelve None.
    connector_class = connectors.get(
        connector_name.lower()
    )

    # Comprobamos si el nombre recibido corresponde a un conector conocido.
    # Si connector_class es None, significa que no está soportado.
    if connector_class is None:

        # Lanzamos una excepción ValueError para informar del problema.
        raise ValueError(
            f"Conector no soportado: {connector_name}"
        )

    # Creamos una instancia de la clase seleccionada usando ().
    # Por ejemplo, si se solicitó "oracle", equivale a OracleConnector().
    # Devolvemos el objeto creado para que el resto del programa lo utilice.
    return connector_class()
