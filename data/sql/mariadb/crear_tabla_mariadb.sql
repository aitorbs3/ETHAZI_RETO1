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