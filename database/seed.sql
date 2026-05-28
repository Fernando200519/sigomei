INSERT INTO roles (nombre) VALUES
    ('Administrador'),
    ('Coordinador'),
    ('Supervisor'),
    ('Técnico');

INSERT INTO usuarios (id_usuario_int, id_usuario, nombre_completo, rfc, telefono, correo, estado, hash_contrasena, id_rol) VALUES
    (1, 'ADM-001', 'Ana García López',    'GALA850312HDF', '5512345678', 'ana.garcia@empresa.mx',   'Activo', 'scrypt:32768:8:1$48Axvx43Nkd9PWhg$a9a314227203375b7d26a623d3716b3de26eaad35c789839e72be8c33f89576117cbef04823350e81f0cf05e97efe2d83a62685ff54f779a91f60f6612dde83d', 1),
    (2, 'COO-001', 'Carlos Ruiz Pérez',   'RUPC900101VER', '9211234567', 'carlos.ruiz@empresa.mx',  'Activo', 'scrypt:32768:8:1$miVy6XubkBXp5yxq$082bf4179ed5fe90802aea64ced2c240ac312abb3ca41db3478196b4a0cfe78c3ed6cc58436b25d1708d644febba1dede32e64ccdea706f8b8016324584b24d5', 2),
    (3, 'SUP-001', 'Luis Torres Mendoza', 'TOML880615OAX', '9513456789', 'luis.torres@empresa.mx',  'Activo', 'scrypt:32768:8:1$kl1dDsegYDcRcFkU$374e623f56f5add6497eac5d9c3f8644e6aa2da78de37f5a3df7a1c2b17f0494c3dd5909e51b437d4b93c5338d9862dbf5a62c95068d155c1b1f2111fa81c244', 3),
    (4, 'TEC-001', 'María Solano Vega',   'SOVM950320TAB', '9931234567', 'maria.solano@empresa.mx', 'Activo', 'scrypt:32768:8:1$L1rq5ir6a3ADbcyM$7f0a0edd2a5746d8fe2b904bb68c4b6be63fd5d34248fc11b89bd78feeed42dc884b52290e99b64659bc39a7225ea24e9b77b3357dcf65a6187a35271628e0b2', 4),
    (5, 'TEC-002', 'Pedro Cano Díaz',     'CADP780901VER', '2295678901', 'pedro.cano@empresa.mx',   'Activo', 'scrypt:32768:8:1$xqRFrl4gzWz77llC$dc799a4e85fdf53b16ca25d10e1b7264a43303b2bf71d4d1969b48f32bc0ca9f61d6f6c5e27e0bfccd4701821fae44a7d4defb0827f87a6f80388ce98e9e72fc', 4);

INSERT INTO sesiones (id_usuario_int, fecha_hora_inicio, fecha_hora_fin) VALUES
    (1, '2025-05-10 08:01:00', '2025-05-10 16:30:00'),
    (3, '2025-05-10 07:55:00', '2025-05-10 17:00:00'),
    (4, '2025-05-11 08:10:00', NULL);

INSERT INTO tecnicos (id_tecnico_int, id_tecnico, fecha_ingreso, nivel_certificacion, especialidad) VALUES
    (4, 'TEC-001', '2019-06-01', 'Nivel III – CMRP', 'Mecanico'),
    (5, 'TEC-002', '2021-03-15', 'Nivel II – CRL',   'Electrico');

INSERT INTO equipos (id_equipo_int, id_equipo, nombre, tipo, marca, modelo, numero_serie, ubicacion_planta, fecha_instalacion, estado_operativo, criticidad, registrado_por_int) VALUES
    (1, 'EQ-001', 'Compresor Atlas 01',      'Compresor',     'Atlas Copco', 'GA-90',       'SN-ATL-001', 'Nave A – Zona 1',  '2018-04-20', 'Operativo',        'Alta',  NULL),
    (2, 'EQ-002', 'Banda Transportadora B2', 'Transportador', 'Intralox',    'Series 400',  'SN-INT-002', 'Nave B – Línea 2', '2020-07-15', 'Operativo',        'Media', NULL),
    (3, 'EQ-003', 'Motor Eléctrico M3',       'Motor',         'WEG',         'W22 200HP',   'SN-WEG-003', 'Nave C – Zona 4',  '2021-01-10', 'En Mantenimiento', 'Alta',  NULL),
    (4, 'EQ-004', 'Bomba Hidráulica H4',     'Bomba',         'Parker',      'PVH074',      'SN-PAR-004', 'Sala de Bombas',   '2019-11-30', 'Operativo',        'Media', NULL),
    (5, 'EQ-005', 'Torno CNC T5',            'Maquinado',     'Haas',        'ST-20',       'SN-HAS-005', 'Taller Mecánico',  '2022-03-25', 'Fuera de Servicio','Alta',  NULL);

INSERT INTO estados_orden (nombre) VALUES
    ('Programada'),
    ('En ejecucion'),
    ('Pendiente de cierre'),
    ('Finalizada'),
    ('Cancelada');

INSERT INTO ordenes_mantenimiento (id_orden_int, id_orden, id_equipo_int, id_tecnico_int, creado_por_int, descripcion_trabajo, tipo_mantenimiento, costo_estimado, costo_real, fecha_programada, fecha_inicio, fecha_cierre) VALUES
    (1, 'OM-001', 1, 4, NULL, 'Cambio de filtros y revisión de presión de aceite del compresor Atlas 01.',           'Mecanico',   1500.00, 1320.00, '2025-05-05', '2025-05-05 09:00:00', '2025-05-05 13:30:00'),
    (2, 'OM-002', 3, 5, NULL, 'Diagnóstico y reparación de variador de frecuencia en Motor WEG W22.',                'Electrico',  8000.00, NULL,    '2025-05-12', '2025-05-12 08:00:00', NULL),
    (3, 'OM-003', 5, 4, NULL, 'Mantenimiento general de Torno CNC: calibración, lubricación y revisión eléctrica.', 'Mecanico',   3500.00, NULL,    '2025-05-15', NULL,                  NULL),
    (4, 'OM-004', 2, 5, NULL, 'Inspección predictiva de banda – análisis de vibración y termografía.',               'Electrico',   900.00,  870.00, '2025-04-28', '2025-04-28 10:00:00', '2025-04-28 14:00:00'),
    (5, 'OM-005', 4, 4, NULL, 'Sustitución de sellos mecánicos y revisión de caudal de bomba Parker.',               'Hidraulico', 2200.00, NULL,    '2025-05-20', NULL,                  NULL);

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