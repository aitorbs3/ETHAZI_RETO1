from backend.repositories.pending_operations_repository import (
    PendingOperationsRepository,
)


def probar_operaciones_pendientes():
    repository = PendingOperationsRepository()

    # Registrar una operación de prueba
    operation_id = repository.add_pending_operation(
        operation="CREATE",
        nombre="Harry Potter Prueba",
        payload={
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

    print("\n--- OPERACIONES PENDIENTES ---")
    for operation in repository.get_pending_operations():
        print(operation)

    # Simular un fallo de sincronización
    repository.mark_attempt_failed(
        operation_id,
        "Error de conexión de prueba con MariaDB",
    )

    print("\n--- DESPUÉS DEL FALLO ---")
    for operation in repository.get_pending_operations():
        if operation["id"] == operation_id:
            print(operation)

    # Eliminar la operación de prueba
    repository.delete_pending_operation(operation_id)

    print("\n--- DESPUÉS DE ELIMINAR LA PRUEBA ---")
    for operation in repository.get_pending_operations():
        print(operation)


    # Probar una operación de cambio de nombre
    update_id = repository.add_pending_operation(
        operation="UPDATE",
        nombre="Harry Potter",
        nombre_editado="Harry Potter Editado",
        payload={
            "nombre": "Harry Potter Editado",
            "casa": "Gryffindor",
            "especie": "Humano",
            "genero": "Masculino",
            "nacionalidad": "Británica",
        },
    )

    print("\n--- PRUEBA DE CAMBIO DE NOMBRE ---")
    for operation in repository.get_pending_operations():
        if operation["id"] == update_id:
            print(operation)

    repository.delete_pending_operation(update_id)

if __name__ == "__main__":
    probar_operaciones_pendientes()
