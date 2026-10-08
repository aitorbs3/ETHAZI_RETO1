
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

    # Diccionario que relaciona el nombre utilizado por la API
    # con la clase encargada de trabajar con esa base de datos.
    connectors = {
        "derby": DerbyConnector,
        "hsqldb": HSQLDBConnector,
        "h2": H2Connector,
        "oracle": OracleConnector
    }

    # Buscamos el conector ignorando si el nombre viene
    # escrito en mayúsculas o minúsculas.
    connector_class = connectors.get(
        connector_name.lower()
    )

    # Si no existe un conector con ese nombre,
    # informamos de que no está soportado.
    if connector_class is None:
        raise ValueError(
            f"Conector no soportado: {connector_name}"
        )

    # Creamos y devolvemos una instancia del conector.
    return connector_class()