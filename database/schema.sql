DROP TABLE IF EXISTS historial_estados_orden CASCADE;
DROP TABLE IF EXISTS ordenes_mantenimiento   CASCADE;
DROP TABLE IF EXISTS estados_orden           CASCADE;
DROP TABLE IF EXISTS equipos                 CASCADE;
DROP TABLE IF EXISTS tecnicos                CASCADE;
DROP TABLE IF EXISTS sesiones                CASCADE;
DROP TABLE IF EXISTS usuarios                CASCADE;
DROP TABLE IF EXISTS roles                   CASCADE;

DROP TYPE IF EXISTS estado_usuario_t   CASCADE;
DROP TYPE IF EXISTS estado_operativo_t CASCADE;
DROP TYPE IF EXISTS criticidad_t       CASCADE;
DROP TYPE IF EXISTS tipo_mant_t        CASCADE;
DROP TYPE IF EXISTS tipo_especialidad  CASCADE;

CREATE TYPE estado_usuario_t   AS ENUM ('Activo', 'Inactivo', 'Suspendido');
CREATE TYPE estado_operativo_t AS ENUM ('Operativo', 'En Mantenimiento', 'Fuera de Servicio');
CREATE TYPE criticidad_t       AS ENUM ('Alta', 'Media', 'Baja');
CREATE TYPE tipo_mant_t        AS ENUM ('Electrico', 'Mecanico', 'Hidraulico', 'Neumatico');
CREATE TYPE tipo_especialidad  AS ENUM ('Electrico', 'Mecanico', 'Hidraulico', 'Neumatico');

CREATE TABLE roles (
    id_rol  SERIAL       PRIMARY KEY,
    nombre  VARCHAR(50)  NOT NULL,
    CONSTRAINT uq_rol_nombre UNIQUE (nombre)
);

CREATE TABLE usuarios (
    id_usuario_int  SERIAL              PRIMARY KEY, -- ID Interno
    id_usuario      VARCHAR(25)         NOT NULL UNIQUE, -- ID de Negocio
    nombre_completo VARCHAR(120)        NOT NULL,
    rfc             VARCHAR(13)         UNIQUE,
    telefono        VARCHAR(15),
    correo          VARCHAR(100)        NOT NULL UNIQUE,
    estado          estado_usuario_t    NOT NULL DEFAULT 'Activo',
    hash_contrasena VARCHAR(255)        NOT NULL,
    id_rol          INT                 NOT NULL REFERENCES roles(id_rol)
                                                 ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_usr_estado ON usuarios(estado);
CREATE INDEX idx_usr_rol    ON usuarios(id_rol);

CREATE TABLE sesiones (
    id_sesion          SERIAL    PRIMARY KEY,
    id_usuario_int     INT       NOT NULL REFERENCES usuarios(id_usuario_int)
                                             ON UPDATE CASCADE ON DELETE CASCADE,
    fecha_hora_inicio TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_hora_fin    TIMESTAMP
);

CREATE INDEX idx_ses_usuario ON sesiones(id_usuario_int);
CREATE INDEX idx_ses_inicio  ON sesiones(fecha_hora_inicio);

CREATE TABLE tecnicos (
    id_tecnico_int      INT          PRIMARY KEY REFERENCES usuarios(id_usuario_int)
                                                 ON UPDATE CASCADE ON DELETE CASCADE,
    id_tecnico          VARCHAR(25)  NOT NULL UNIQUE REFERENCES usuarios(id_usuario)
                                                 ON UPDATE CASCADE ON DELETE CASCADE,
    fecha_ingreso       DATE         NOT NULL,
    nivel_certificacion VARCHAR(60),
    especialidad        tipo_especialidad
);

CREATE INDEX idx_tec_especialidad ON tecnicos(especialidad);

CREATE TABLE equipos (
    id_equipo_int     SERIAL              PRIMARY KEY, -- ID Interno
    id_equipo         VARCHAR(25)         NOT NULL UNIQUE, -- ID de Negocio
    nombre            VARCHAR(100)        NOT NULL,
    tipo              VARCHAR(50),
    marca             VARCHAR(60),
    modelo            VARCHAR(60),
    numero_serie      VARCHAR(80)         UNIQUE,
    ubicacion_planta  VARCHAR(100),
    fecha_instalacion DATE,
    estado_operativo  estado_operativo_t  NOT NULL DEFAULT 'Operativo',
    criticidad        criticidad_t        NOT NULL DEFAULT 'Media',
    registrado_por_int INT                 REFERENCES usuarios(id_usuario_int) -- Se quitó NOT NULL
                                                     ON UPDATE CASCADE ON DELETE RESTRICT
);

CREATE INDEX idx_eq_estado     ON equipos(estado_operativo);
CREATE INDEX idx_eq_criticidad ON equipos(criticidad);
CREATE INDEX idx_eq_ubicacion  ON equipos(ubicacion_planta);

CREATE TABLE estados_orden (
    id_estado_orden SERIAL      PRIMARY KEY,
    nombre          VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE ordenes_mantenimiento (
    id_orden_int        SERIAL              PRIMARY KEY, -- ID Interno
    id_orden            VARCHAR(25)         NOT NULL UNIQUE, -- ID de Negocio
    id_equipo_int       INT                 NOT NULL REFERENCES equipos(id_equipo_int)
                                                     ON UPDATE CASCADE ON DELETE RESTRICT,
    id_tecnico_int      INT                 REFERENCES tecnicos(id_tecnico_int)
                                                     ON UPDATE CASCADE ON DELETE SET NULL,
    creado_por_int      INT                 REFERENCES usuarios(id_usuario_int) -- Se quitó NOT NULL
                                                     ON UPDATE CASCADE ON DELETE RESTRICT,
    descripcion_trabajo TEXT,
    tipo_mantenimiento  tipo_mant_t         NOT NULL,
    costo_estimado      NUMERIC(12,2),
    costo_real          NUMERIC(12,2),
    fecha_programada    DATE,
    fecha_inicio        TIMESTAMP,
    fecha_cierre        TIMESTAMP
);

CREATE INDEX idx_ord_equipo     ON ordenes_mantenimiento(id_equipo_int);
CREATE INDEX idx_ord_tecnico    ON ordenes_mantenimiento(id_tecnico_int);
CREATE INDEX idx_ord_tipo       ON ordenes_mantenimiento(tipo_mantenimiento);
CREATE INDEX idx_ord_fecha_prog ON ordenes_mantenimiento(fecha_programada);
CREATE INDEX idx_ord_fecha_ini  ON ordenes_mantenimiento(fecha_inicio);

CREATE TABLE historial_estados_orden (
    id_historial      SERIAL    PRIMARY KEY,
    id_orden_int      INT       NOT NULL REFERENCES ordenes_mantenimiento(id_orden_int)
                                             ON UPDATE CASCADE ON DELETE CASCADE,
    id_estado_orden   INT       NOT NULL REFERENCES estados_orden(id_estado_orden)
                                             ON UPDATE CASCADE ON DELETE RESTRICT,
    fecha_hora_inicio TIMESTAMP NOT NULL DEFAULT NOW(),
    fecha_hora_fin    TIMESTAMP
);

CREATE INDEX idx_heo_orden  ON historial_estados_orden(id_orden_int);
CREATE INDEX idx_heo_estado ON historial_estados_orden(id_estado_orden);
CREATE INDEX idx_heo_inicio ON historial_estados_orden(fecha_hora_inicio);
