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


INSERT INTO roles (nombre) VALUES
    ('Administrador'),
    ('Coordinador'),
    ('Supervisor'),
    ('Técnico');

INSERT INTO usuarios (id_usuario_int, id_usuario, nombre_completo, rfc, telefono, correo, estado, hash_contrasena, id_rol) VALUES
    (1, 'ADM-001', 'Ana García López',    'GALA850312HDF', '5512345678', 'ana.garcia@empresa.mx',   'Activo', '$2b$12$hash_admin_1', 1),
    (2, 'COO-001', 'Carlos Ruiz Pérez',   'RUPC900101VER', '9211234567', 'carlos.ruiz@empresa.mx',  'Activo', '$2b$12$hash_sup_1',   2),
    (3, 'SUP-001', 'Luis Torres Mendoza', 'TOML880615OAX', '9513456789', 'luis.torres@empresa.mx',  'Activo', '$2b$12$hash_tec_1',   3),
    (4, 'TEC-001', 'María Solano Vega',   'SOVM950320TAB', '9931234567', 'maria.solano@empresa.mx', 'Activo', '$2b$12$hash_tec_2',   4),
    (5, 'TEC-002', 'Pedro Cano Díaz',     'CADP780901VER', '2295678901', 'pedro.cano@empresa.mx',   'Activo', '$2b$12$hash_cli_1',   4);

INSERT INTO sesiones (id_usuario_int, fecha_hora_inicio, fecha_hora_fin) VALUES
    (1, '2025-05-10 08:01:00', '2025-05-10 16:30:00'),
    (3, '2025-05-10 07:55:00', '2025-05-10 17:00:00'),
    (4, '2025-05-11 08:10:00', NULL);

INSERT INTO tecnicos (id_tecnico_int, id_tecnico, fecha_ingreso, nivel_certificacion, especialidad) VALUES
    (4, 'TEC-001', '2019-06-01', 'Nivel III – CMRP', 'Mecanico'),
    (5, 'TEC-002', '2021-03-15', 'Nivel II – CRL',   'Electrico');

INSERT INTO equipos (id_equipo_int, id_equipo, nombre, tipo, marca, modelo, numero_serie, ubicacion_planta, fecha_instalacion, estado_operativo, criticidad, registrado_por_int) VALUES
    (1, 'EQ-001', 'Compresor Atlas 01',      'Compresor',     'Atlas Copco', 'GA-90',      'SN-ATL-001', 'Nave A – Zona 1',  '2018-04-20', 'Operativo',        'Alta',  NULL),
    (2, 'EQ-002', 'Banda Transportadora B2', 'Transportador', 'Intralox',    'Series 400', 'SN-INT-002', 'Nave B – Línea 2', '2020-07-15', 'Operativo',        'Media', NULL),
    (3, 'EQ-003', 'Motor Eléctrico M3',      'Motor',         'WEG',         'W22 200HP',  'SN-WEG-003', 'Nave C – Zona 4',  '2021-01-10', 'En Mantenimiento', 'Alta',  NULL),
    (4, 'EQ-004', 'Bomba Hidráulica H4',     'Bomba',         'Parker',      'PVH074',     'SN-PAR-004', 'Sala de Bombas',   '2019-11-30', 'Operativo',        'Media', NULL),
    (5, 'EQ-005', 'Torno CNC T5',            'Maquinado',     'Haas',        'ST-20',      'SN-HAS-005', 'Taller Mecánico',  '2022-03-25', 'Fuera de Servicio','Alta',  NULL);

INSERT INTO estados_orden (nombre) VALUES
    ('Programada'),
    ('En ejecucion'),
    ('Finalizada'),
    ('Cancelada');

INSERT INTO ordenes_mantenimiento (id_orden_int, id_orden, id_equipo_int, id_tecnico_int, creado_por_int, descripcion_trabajo, tipo_mantenimiento, costo_estimado, costo_real, fecha_programada, fecha_inicio, fecha_cierre) VALUES
    (1, 'OM-001', 1, 4, NULL, 'Cambio de filtros y revisión de presión de aceite del compresor Atlas 01.',           'Mecanico',   1500.00, 1320.00, '2025-05-05', '2025-05-05 09:00:00', '2025-05-05 13:30:00'),
    (2, 'OM-002', 3, 5, NULL, 'Diagnóstico y reparación de variador de frecuencia en Motor WEG W22.',                'Electrico',  8000.00, NULL,    '2025-05-12', '2025-05-12 08:00:00', NULL),
    (3, 'OM-003', 5, 4, NULL, 'Mantenimiento general de Torno CNC: calibración, lubricación y revisión eléctrica.', 'Mecanico',   3500.00, NULL,    '2025-05-15', NULL,                   NULL),
    (4, 'OM-004', 2, 5, NULL, 'Inspección predictiva de banda – análisis de vibración y termografía.',               'Electrico',   900.00,  870.00, '2025-04-28', '2025-04-28 10:00:00', '2025-04-28 14:00:00'),
    (5, 'OM-005', 4, 4, NULL, 'Sustitución de sellos mecánicos y revisión de caudal de bomba Parker.',               'Hidraulico', 2200.00, NULL,    '2025-05-20', NULL,                   NULL);

INSERT INTO historial_estados_orden (id_orden_int, id_estado_orden, fecha_hora_inicio, fecha_hora_fin) VALUES
    (1, 1, '2025-05-04 16:00:00', '2025-05-05 09:00:00'),
    (1, 2, '2025-05-05 09:00:00', '2025-05-05 13:30:00'),
    (1, 3, '2025-05-05 13:30:00', NULL),
    (2, 1, '2025-05-11 10:00:00', '2025-05-12 08:00:00'),
    (2, 2, '2025-05-12 08:00:00', '2025-05-13 15:00:00'),
    (3, 1, '2025-05-10 09:00:00', NULL),
    (4, 1, '2025-04-27 14:00:00', '2025-04-28 10:00:00'),
    (4, 2, '2025-04-28 10:00:00', '2025-04-28 14:00:00'),
    (4, 3, '2025-04-28 14:00:00', NULL),
    (5, 1, '2025-05-15 08:00:00', NULL);

SELECT setval('usuarios_id_usuario_int_seq', COALESCE((SELECT MAX(id_usuario_int) FROM usuarios), 1));
SELECT setval('equipos_id_equipo_int_seq', COALESCE((SELECT MAX(id_equipo_int) FROM equipos), 1));
SELECT setval('ordenes_mantenimiento_id_orden_int_seq', COALESCE((SELECT MAX(id_orden_int) FROM ordenes_mantenimiento), 1));