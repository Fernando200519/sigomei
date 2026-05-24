-- =============================================================
--  SIGOMEI — Schema de base de datos
--  Ejecutar: psql -U <usuario> -d sigomei_db -f schema.sql
-- =============================================================

-- Forzar codificación UTF-8 para la sesión
SET client_encoding = 'UTF8';

-- Elimina las tablas si ya existen (orden inverso de FK)
DROP TABLE IF EXISTS ordenes_mantenimiento CASCADE;
DROP TABLE IF EXISTS tecnicos             CASCADE;
DROP TABLE IF EXISTS equipos              CASCADE;

-- -------------------------------------------------------------
--  EQUIPOS
-- -------------------------------------------------------------
CREATE TABLE equipos (
    id_equipo         VARCHAR(20)  PRIMARY KEY,
    nombre            VARCHAR(100) NOT NULL,
    tipo              VARCHAR(30)  NOT NULL
                          CHECK (tipo IN ('Electrico','Mecanico','Hidraulico','Neumatico')),
    marca             VARCHAR(60)  NOT NULL,
    modelo            VARCHAR(60)  NOT NULL,
    numero_serie      VARCHAR(60)  NOT NULL UNIQUE,
    ubicacion_planta  VARCHAR(80)  NOT NULL,
    fecha_instalacion DATE         NOT NULL,
    estado_operativo  VARCHAR(30)  NOT NULL
                          CHECK (estado_operativo IN ('Operativo','En Mantenimiento','Fuera de Servicio')),
    criticidad        VARCHAR(10)  NOT NULL
                          CHECK (criticidad IN ('Alta','Media','Baja'))
);

-- -------------------------------------------------------------
--  TECNICOS
-- -------------------------------------------------------------
CREATE TABLE tecnicos (
    id_tecnico          VARCHAR(20)  PRIMARY KEY,
    nombre_completo     VARCHAR(100) NOT NULL,
    rfc                 VARCHAR(15)  NOT NULL UNIQUE,
    telefono            VARCHAR(15),
    correo              VARCHAR(80),
    especialidad        VARCHAR(30)  NOT NULL
                            CHECK (especialidad IN ('Electrico','Mecanico','Hidraulico','Neumatico')),
    nivel_certificacion VARCHAR(5)   NOT NULL
                            CHECK (nivel_certificacion IN ('I','II','III')),
    fecha_ingreso       DATE         NOT NULL,
    estatus             VARCHAR(10)  NOT NULL
                            CHECK (estatus IN ('Activo','Inactivo'))
);

-- -------------------------------------------------------------
--  ORDENES DE MANTENIMIENTO
-- -------------------------------------------------------------
CREATE TABLE ordenes_mantenimiento (
    id_orden            VARCHAR(20)    PRIMARY KEY,
    id_equipo           VARCHAR(20)    NOT NULL
                            REFERENCES equipos(id_equipo),
    id_tecnico          VARCHAR(20)
                            REFERENCES tecnicos(id_tecnico),
    tipo_mantenimiento  VARCHAR(30)    NOT NULL,
    fecha_programada    DATE           NOT NULL,
    fecha_inicio        DATE,
    fecha_cierre        DATE,
    descripcion_trabajo TEXT           NOT NULL,
    costo_estimado      NUMERIC(12,2)  NOT NULL,
    costo_real          NUMERIC(12,2),
    estado_orden        VARCHAR(20)    NOT NULL DEFAULT 'Programada'
                            CHECK (estado_orden IN ('Programada','En Ejecucion','Finalizada','Cancelada')),

    -- Restricciones de coherencia de fechas (RN-05) a nivel BD
    CONSTRAINT chk_inicio_vs_programada
        CHECK (fecha_inicio IS NULL OR fecha_inicio >= fecha_programada),
    CONSTRAINT chk_cierre_vs_inicio
        CHECK (fecha_cierre IS NULL OR fecha_inicio IS NULL OR fecha_cierre >= fecha_inicio)
);