from backend.utils.config import obtener_variable
from backend.connectors.h2_connector import obtener_conexion_h2

def probar_conexion_y_crear_datos():
    print("=== Probando Conexión e Inicialización de H2 ===")
    
    # 1. Leer ruta desde .env
    ruta_db = obtener_variable("H2_DATABASE")
    print(f"Ruta configurada en .env: {ruta_db}")
    
    # 2. Conectar a H2 (esto generará automáticamente el archivo prueba_h2.mv.db si no existe)
    conn = obtener_conexion_h2()
    cursor = conn.cursor()
    
    # 3. Crear una tabla de prueba si no existe
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS prueba_h2 (
            id INT PRIMARY KEY AUTO_INCREMENT,
            mensaje VARCHAR(100) NOT NULL
        )
    """)
    print(" Tabla 'prueba_h2' verificada/creada correctamente.")
    
    # 4. Insertar un registro de prueba
    cursor.execute("INSERT INTO prueba_h2 (mensaje) VALUES ('Conexión H2 funcionando desde Python')")
    
    # 5. Consultar los datos insertados
    cursor.execute("SELECT * FROM prueba_h2")
    filas = cursor.fetchall()
    
    print("\nRegistros encontrados en la BD H2 de prueba:")
    for fila in filas:
        print(f"  - ID: {fila[0]} | Mensaje: {fila[1]}")
    
    # Cierre de recursos
    cursor.close()
    conn.close()
    print("\n Prueba completada con éxito.")

if __name__ == "__main__":
    probar_conexion_y_crear_datos()