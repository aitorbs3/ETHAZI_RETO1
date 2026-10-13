CREATE TABLE IF NOT EXISTS alumnos (
    id VARCHAR(50) PRIMARY KEY,
    nombre VARCHAR(150) NOT NULL,
    casa VARCHAR(50) NOT NULL,
    especie VARCHAR(100) NOT NULL,
    genero VARCHAR(30) NOT NULL,
    nacimiento DATE NULL,
    nacionalidad VARCHAR(100) NOT NULL,
    patronus VARCHAR(100) NULL,
    imagen TEXT NULL
);

CREATE TABLE IF NOT EXISTS pending_operations (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    operation VARCHAR(20) NOT NULL,
    student_id VARCHAR(50) NOT NULL,
    payload TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    attempts INTEGER NOT NULL DEFAULT 0,
    last_error TEXT
);