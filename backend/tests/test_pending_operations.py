"""Prueba de persistencia y ciclo de vida de operaciones pendientes."""

# Importar el repositorio encargado de gestionar las operaciones pendientes.
from backend.repositories.pending_operations_repository import (
    PendingOperationsRepository,
)


def probar_operaciones_pendientes():
    """Demuestra el registro, fallo y eliminación de operaciones de prueba."""

    # Crear una instancia del repositorio para gestionar las operaciones pendientes.
    repository = PendingOperationsRepository()

    # Registrar una operación de creación (CREATE) de un personaje de prueba.
    # Se guarda el tipo de operación, el nombre y los datos del personaje.
    operation_id = repository.add_pending_operation(
        operation="CREATE",
        nombre="Harry Potter Prueba",
        payload={
            # Datos que se almacenarán como contenido de la operación pendiente.
            "id": "TEST_PENDING_001",
            "nombre": "Harry Potter Prueba",
            "casa": "Gryffindor",
            "especie": "Humano",
            "genero": "Masculino",
            "nacimiento": "1980-07-31",
            "nacionalidad": "Británica",
            "patronus": "Ciervo",
            "imagen": None,
        },
    )

    # Mostrar todas las operaciones pendientes registradas en el repositorio.
    print("\n--- OPERACIONES PENDIENTES ---")
    for operation in repository.get_pending_operations():
        print(operation)

    # Simular un fallo durante el intento de sincronizar la operación.
    # Se utiliza el identificador para localizarla y guardar el mensaje de error.
    repository.mark_attempt_failed(
        operation_id,
        "Error de conexión de prueba con MariaDB",
    )

    # Consultar de nuevo las operaciones pendientes para comprobar
    # cómo ha quedado registrada la operación después del fallo.
    print("\n--- DESPUÉS DEL FALLO ---")
    for operation in repository.get_pending_operations():
        # Mostrar únicamente la operación que se acaba de probar.
        if operation["id"] == operation_id:
            print(operation)

    # Eliminar la operación de creación utilizada en la prueba.
    repository.delete_pending_operation(operation_id)

    # Mostrar las operaciones que permanecen pendientes después de eliminarla.
    print("\n--- DESPUÉS DE ELIMINAR LA PRUEBA ---")
    for operation in repository.get_pending_operations():
        print(operation)

    # Registrar una operación de actualización (UPDATE) para cambiar el nombre
    # de un personaje existente.
    update_id = repository.add_pending_operation(
        operation="UPDATE",
        nombre="Harry Potter",
        nombre_editado="Harry Potter Editado",
        payload={
            # Datos asociados a la actualización del personaje.
            "nombre": "Harry Potter Editado",
            "casa": "Gryffindor",
            "especie": "Humano",
            "genero": "Masculino",
            "nacionalidad": "Británica",
        },
    )

    # Mostrar la operación de actualización para verificar que se ha registrado
    # con el nombre original y el nuevo nombre.
    print("\n--- PRUEBA DE CAMBIO DE NOMBRE ---")
    for operation in repository.get_pending_operations():
        # Filtrar los resultados para mostrar solo la actualización de esta prueba.
        if operation["id"] == update_id:
            print(operation)

    # Eliminar la operación de actualización para dejar limpia la prueba.
    repository.delete_pending_operation(update_id)


# Comprobar si este archivo se está ejecutando directamente.
# Si es así, ejecutar la función principal de pruebas.
if __name__ == "__main__":
    probar_operaciones_pendientes()