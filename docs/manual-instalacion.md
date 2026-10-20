## ARCHIVO .ENV

Crear el archivo .env para las contraseñas del docker de tanto mariadb como oracle

    # ORACLE
    ORACLE_ADMIN_PASSWORD=
    ORACLE_HOST=localhost
    ORACLE_PORT=1521
    ORACLE_SERVICE_NAME=FREEPDB1
    ORACLE_USER=
    ORACLE_PASSWORD=

    # MARIADB
    MARIADB_ROOT_PASSWORD=
    MARIADB_HOST=
    MARIADB_PORT=
    MARIADB_DATABASE=
    MARIADB_USER=
    MARIADB_PASSWORD=

## EJECUCION .YML

Ejecutar el comando que ejecuta el archivo .yml que configura todas las bases y lanza la API:
docker compose up -d --build