INSERT INTO equipos VALUES
    ('EQ-001', 'Transformador T1',      'Electrico',  'ABB',      'TX-500',  'SN-AAA-001', 'Nave A', '2020-01-15', 'Operativo',          'Alta'),
    ('EQ-002', 'Bomba Centrifuga B2',   'Mecanico',   'Grundfos', 'CM5',     'SN-BBB-002', 'Nave B', '2021-06-10', 'Operativo',          'Baja'),
    ('EQ-003', 'Compresor C3',          'Neumatico',  'Atlas',    'GA-30',   'SN-CCC-003', 'Nave C', '2019-11-20', 'Operativo',          'Media'),
    ('EQ-004', 'Panel Electrico P4',    'Electrico',  'Schneider','XB5',     'SN-DDD-004', 'Nave A', '2022-03-05', 'En Mantenimiento',   'Alta'),
    ('EQ-005', 'Prensa Hidraulica H5',  'Hidraulico', 'Parker',   'PH-200',  'SN-EEE-005', 'Nave D', '2018-07-30', 'Operativo',          'Media'),
    ('EQ-006', 'Ventilador V6',         'Mecanico',   'Fläkt',    'VX-100',  'SN-FFF-006', 'Nave B', '2023-01-01', 'Fuera de Servicio',  'Baja');


INSERT INTO tecnicos VALUES
    ('TEC-001', 'Carlos Lopez',    'LOCA800101AAA', '9211234567', 'carlos@sigomei.mx', 'Mecanico',   'I',   '2022-03-01', 'Activo'),
    ('TEC-002', 'Ana Perez',       'PEAA900202BBB', '9219876543', 'ana@sigomei.mx',    'Electrico',  'II',  '2021-07-15', 'Activo'),
    ('TEC-003', 'Luis Ramos',      'RALU850303CCC', '9215554433', 'luis@sigomei.mx',   'Electrico',  'II',  '2019-01-10', 'Inactivo'),
    ('TEC-004', 'Maria Torres',    'TOMA950404DDD', '9213330011', 'maria@sigomei.mx',  'Neumatico',  'III', '2020-09-20', 'Activo'),
    ('TEC-005', 'Jorge Castillo',  'CAJG880505EEE', '9218887766', 'jorge@sigomei.mx',  'Hidraulico', 'II',  '2023-02-14', 'Activo');

INSERT INTO ordenes_mantenimiento
    (id_orden, id_equipo, id_tecnico, tipo_mantenimiento,
     fecha_programada, fecha_inicio, fecha_cierre,
     descripcion_trabajo, costo_estimado, costo_real, estado_orden)
VALUES
    -- Orden programada (sin tecnico aun)
    ('OM-001', 'EQ-001', NULL,      'Preventivo',
     '2025-07-01', NULL, NULL,
     'Revision semestral del transformador T1', 5000.00, NULL, 'Programada'),

    -- Orden en ejecucion
    ('OM-002', 'EQ-002', 'TEC-001', 'Correctivo',
     '2025-06-10', '2025-06-12', NULL,
     'Reemplazo de rodamientos en bomba B2',    3200.00, NULL, 'En ejecucion'),

    -- Orden finalizada
    ('OM-003', 'EQ-003', 'TEC-004', 'Preventivo',
     '2025-05-01', '2025-05-03', '2025-05-05',
     'Ajuste y lubricacion del compresor C3',   1500.00, 1650.00, 'Finalizada'),

    -- Orden cancelada
    ('OM-004', 'EQ-006', NULL,      'Correctivo',
     '2025-04-15', NULL, NULL,
     'Reparacion de aspas del ventilador V6',   800.00,  NULL, 'Cancelada'),

    -- Orden programada para equipo con criticidad Alta
    ('OM-005', 'EQ-004', NULL,      'Predictivo',
     '2025-08-10', NULL, NULL,
     'Termografia del panel electrico P4',      2200.00, NULL, 'Programada'),

    -- Orden finalizada con equipo hidraulico
    ('OM-006', 'EQ-005', 'TEC-005', 'Preventivo',
     '2025-03-01', '2025-03-02', '2025-03-04',
     'Cambio de sellos hidraulicos en prensa H5', 4100.00, 3980.00, 'Finalizada');