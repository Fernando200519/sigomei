from datetime import datetime
import pytest
from server.exceptions.exceptions import EntidadDuplicadaError, ReglaNegocioError

EQUIPO_MECANICO = dict(
    id_equipo="EQ-701", nombre="Bomba-01", tipo="Mecanico",
    marca="Grundfos", modelo="CM5-5", numero_serie="NS-001",
    ubicacion_planta="Planta A", fecha_instalacion="2023-01-15",
    estado_operativo="Operativo", criticidad="Media",
)
EQUIPO_ELECTRICO = dict(
    id_equipo="EQ-702", nombre="Transformador-01", tipo="Electrico",
    marca="ABB", modelo="TR-100", numero_serie="NS-002",
    ubicacion_planta="Planta B", fecha_instalacion="2022-05-01",
    estado_operativo="Operativo", criticidad="Media",
)
EQUIPO_ALTA_CRITICIDAD = dict(
    id_equipo="EQ-703", nombre="Compresor-Alta", tipo="Mecanico",
    marca="Atlas", modelo="GA-55", numero_serie="NS-003",
    ubicacion_planta="Planta C", fecha_instalacion="2021-01-01",
    estado_operativo="Operativo", criticidad="Alta",
)

TECNICO_MECANICO_C1 = dict(
    id_tecnico="TEC-701", nombre_completo="Juan Perez",
    rfc="PEJA850101AAA", telefono="9210001001",
    correo="juan@sigomei.mx", especialidad="Mecanico",
    nivel_certificacion="I", fecha_ingreso="2022-01-01", estatus="Activo",
)
TECNICO_MECANICO_C2 = dict(
    id_tecnico="TEC-702", nombre_completo="Carlos Lopez",
    rfc="LOCC850101BBB", telefono="9210001002",
    correo="carlos@sigomei.mx", especialidad="Mecanico",
    nivel_certificacion="II", fecha_ingreso="2022-01-01", estatus="Activo",
)
TECNICO_ELECTRICO_C2 = dict(
    id_tecnico="TEC-703", nombre_completo="Maria Garcia",
    rfc="GAMA900101CCC", telefono="9210001003",
    correo="maria@sigomei.mx", especialidad="Electrico",
    nivel_certificacion="II", fecha_ingreso="2022-01-01", estatus="Activo",
)


class TestTC_SIS_02_TableroPorEstado:
    """TC-SIS-02 | RF-05"""

    def test_sis02_tablero_muestra_ordenes_programada_y_en_ejecucion(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)

        for i in range(1, 5):
            rmi_registry.crear_orden(
                token=token,
                id_orden=f"ORD-00{i}", id_equipo="EQ-701",
                tipo_mantenimiento="Mecanico",
                fecha_programada=f"2026-06-{10 + i:02d}",
                descripcion_trabajo=f"Revisión {i}",
                costo_estimado=1000.0,
            )
            rmi_registry.asignar_tecnico(token, f"ORD-00{i}", "TEC-702")

        rmi_registry.iniciar_ejecucion(token, "ORD-001", "2026-06-11")
        rmi_registry.iniciar_ejecucion(token, "ORD-002", "2026-06-12")

        programadas  = rmi_registry.listar_ordenes_por_filtro(token, {"estado_orden": "Programada"})
        en_ejecucion = rmi_registry.listar_ordenes_por_filtro(token, {"estado_orden": "En ejecucion"})

        assert len(programadas)  >= 2
        assert len(en_ejecucion) >= 2
        for orden in programadas + en_ejecucion:
            for campo in ("id_orden", "fecha_programada", "descripcion_trabajo",
                          "id_equipo", "id_tecnico"):
                assert campo in orden


class TestTC_SIS_03_CrearOrdenExitosa:
    """TC-SIS-03 | RF-07, RN-13"""

    def test_sis03_crear_orden_campos_completos(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)

        resultado = rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-001", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico",
            fecha_programada="2026-06-10",
            descripcion_trabajo="Revisión de sellos",
            costo_estimado=1500.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-001", "TEC-702")

        assert resultado is True
        orden = rmi_registry.consultar_orden(token, "ORD-001")
        assert orden["estado_orden"].lower() == "programada"


class TestTC_SIS_04_EspecialidadIncompatible:
    """TC-SIS-04 | RF-07, RN-01"""

    def test_sis04_crear_orden_especialidad_tecnico_no_coincide(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_ELECTRICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)

        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-001", id_equipo="EQ-702",
            tipo_mantenimiento="Electrico",
            fecha_programada="2026-06-10",
            descripcion_trabajo="Revisión eléctrica",
            costo_estimado=2000.0,
        )

        with pytest.raises(ReglaNegocioError):
            rmi_registry.asignar_tecnico(token, "ORD-001", "TEC-702")


class TestTC_SIS_05_CriticidadAltaCertificacionInsuficiente:
    """TC-SIS-05 | RF-07, RN-07"""

    def test_sis05_equipo_criticidad_alta_requiere_certificacion_ii_o_iii(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_ALTA_CRITICIDAD)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C1)

        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-001", id_equipo="EQ-703",
            tipo_mantenimiento="Mecanico",
            fecha_programada="2026-06-10",
            descripcion_trabajo="Revisión compresor",
            costo_estimado=3000.0,
        )

        with pytest.raises(ReglaNegocioError):
            rmi_registry.asignar_tecnico(token, "ORD-001", "TEC-701")


class TestTC_SIS_06_OrdenDuplicadaMismaFecha:
    """TC-SIS-06 | RF-07, RN-02"""

    def test_sis06_no_crear_orden_equipo_con_orden_activa_misma_fecha(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)

        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-001", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-10",
            descripcion_trabajo="Orden existente", costo_estimado=1000.0,
        )

        with pytest.raises(EntidadDuplicadaError):
            rmi_registry.crear_orden(
                token=token,
                id_orden="ORD-002", id_equipo="EQ-701",
                tipo_mantenimiento="Mecanico", fecha_programada="2026-06-10",
                descripcion_trabajo="Orden duplicada", costo_estimado=800.0,
            )


class TestTC_SIS_07_TransicionProgramadaEnEjecucionSupervisor:
    """TC-SIS-07 | RF-08, RN-14"""

    def test_sis07_supervisor_cambia_orden_a_en_ejecucion(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-001", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-10",
            descripcion_trabajo="Revisión de sellos", costo_estimado=1500.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-001", "TEC-702")

        resultado = rmi_registry.iniciar_ejecucion(token, "ORD-001", "2026-06-10")

        assert resultado is True
        orden = rmi_registry.consultar_orden(token, "ORD-001")
        assert orden["estado_orden"].lower() == "en ejecucion"


class TestTC_SIS_08_TransicionProgramadaEnEjecucionTecnico:
    """TC-SIS-08 | RF-08, RN-14"""

    def test_sis08_tecnico_cambia_orden_a_en_ejecucion(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-002", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-11",
            descripcion_trabajo="Cambio de rodamientos", costo_estimado=900.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-002", "TEC-702")

        resultado = rmi_registry.iniciar_ejecucion(token, "ORD-002", "2026-06-11")

        assert resultado is True
        orden = rmi_registry.consultar_orden(token, "ORD-002")
        assert orden["estado_orden"].lower() == "en ejecucion"


class TestTC_SIS_10_SupervisorCierraOrden:
    """TC-SIS-10 | RF-10, RN-06"""

    def test_sis10_supervisor_finaliza_orden_con_costo_real(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-003", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-12",
            descripcion_trabajo="Revisión de válvulas", costo_estimado=1500.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-003", "TEC-702")
        rmi_registry.iniciar_ejecucion(token, "ORD-003", "2026-06-12")

        resultado = rmi_registry.finalizar_orden(token, "ORD-003", "2026-06-13", 1750.0)

        assert resultado is True
        orden = rmi_registry.consultar_orden(token, "ORD-003")
        dt_object = datetime.fromisoformat(orden["fecha_cierre"])

        assert orden["estado_orden"].lower() == "finalizada"
        assert float(orden["costo_real"]) == 1750.0
        assert str(dt_object.date()) == "2026-06-13"


class TestTC_SIS_11_CierreOrdenSinCostoReal:
    """TC-SIS-11 | RF-10, RN-06"""

    def test_sis11_supervisor_intenta_cerrar_sin_costo_real(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-004", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-13",
            descripcion_trabajo="Reparación de bomba", costo_estimado=2000.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-004", "TEC-702")
        rmi_registry.iniciar_ejecucion(token, "ORD-004", "2026-06-13")

        # CORREGIDO: Espera ReglaNegocioError directamente
        with pytest.raises(ReglaNegocioError):
            rmi_registry.finalizar_orden(token, "ORD-004", "2026-06-14", None)

        orden = rmi_registry.consultar_orden(token, "ORD-004")
        assert orden["estado_orden"].lower() == "en ejecucion"


class TestTC_SIS_12_CancelarOrdenProgramada:
    """TC-SIS-12 | RN-08"""

    def test_sis12_cancelar_orden_desde_estado_programada(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-005", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-15",
            descripcion_trabajo="Revisión preventiva", costo_estimado=1000.0,
        )

        resultado = rmi_registry.cancelar_orden(token, "ORD-005")

        assert resultado is True
        orden = rmi_registry.consultar_orden(token, "ORD-005")
        assert orden["estado_orden"].lower() == "cancelada"


class TestTC_SIS_18_TecnicoConOrdenActivaAsignacion:
    """TC-SIS-18 | RF-07, RN-16"""

    def test_sis18_tecnico_con_orden_en_ejecucion_no_puede_asignarse(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_ELECTRICO)
        rmi_registry.alta_tecnico(token, **TECNICO_ELECTRICO_C2)

        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-ACT", id_equipo="EQ-702",
            tipo_mantenimiento="Electrico", fecha_programada="2026-06-10",
            descripcion_trabajo="Falla eléctrica", costo_estimado=1500.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-ACT", "TEC-703")
        rmi_registry.iniciar_ejecucion(token, "ORD-ACT", "2026-06-10")

        rmi_registry.alta_equipo(
            token,
            id_equipo="EQ-704", nombre="Panel-01", tipo="Electrico",
            marca="Siemens", modelo="S7-300", numero_serie="NS-004",
            ubicacion_planta="Planta D", fecha_instalacion="2024-01-01",
            estado_operativo="Operativo", criticidad="Baja",
        )
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-NEW", id_equipo="EQ-704",
            tipo_mantenimiento="Electrico", fecha_programada="2026-06-20",
            descripcion_trabajo="Revisión panel", costo_estimado=700.0,
        )

        # CORREGIDO: Espera ReglaNegocioError directamente
        with pytest.raises(ReglaNegocioError):
            rmi_registry.asignar_tecnico(token, "ORD-NEW", "TEC-703")


class TestTC_SIS_19_HistoricoFiltroEquipo:
    """TC-SIS-19 | RF-17"""

    def test_sis19_historico_filtrado_por_equipo(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_equipo(token, **EQUIPO_ELECTRICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)
        rmi_registry.alta_tecnico(token, **TECNICO_ELECTRICO_C2)

        for i, (eq, tec) in enumerate(
            [("EQ-701", "TEC-702"), ("EQ-701", "TEC-702"), ("EQ-702", "TEC-703")], 1
        ):
            rmi_registry.crear_orden(
                token=token,
                id_orden=f"ORD-H0{i}", id_equipo=eq,
                tipo_mantenimiento="Electrico",
                fecha_programada=f"2026-01-{i:02d}",
                descripcion_trabajo="Histórico", costo_estimado=500.0,
            )
            rmi_registry.asignar_tecnico(token, f"ORD-H0{i}", tec)
            rmi_registry.iniciar_ejecucion(token, f"ORD-H0{i}", f"2026-01-{i:02d}")
            rmi_registry.finalizar_orden(token, f"ORD-H0{i}", f"2026-01-{i + 1:02d}", 550.0)

        resultado = rmi_registry.listar_ordenes_por_filtro(
            token, {"estado_orden": "Finalizada", "id_equipo": "EQ-701"}
        )

        assert len(resultado) >= 2
        for orden in resultado:
            assert orden["id_equipo"] == "EQ-701"


class TestTC_SIS_20_HistoricoFiltroFechas:
    """TC-SIS-20 | RF-17"""

    def test_sis20_historico_filtrado_por_rango_de_fechas(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)

        ordenes = [
            ("ORD-R01", "2026-01-15", "2026-01-16"),
            ("ORD-R02", "2026-03-20", "2026-03-21"),
            ("ORD-R03", "2026-05-10", "2026-05-11"),
        ]
        for id_orden, f_prog, f_cierre in ordenes:
            rmi_registry.crear_orden(
                token=token,
                id_orden=id_orden, id_equipo="EQ-701",
                tipo_mantenimiento="Electrico", fecha_programada=f_prog,
                descripcion_trabajo="Revisión", costo_estimado=500.0,
            )
            rmi_registry.asignar_tecnico(token, id_orden, "TEC-702")
            rmi_registry.iniciar_ejecucion(token, id_orden, f_prog)
            rmi_registry.finalizar_orden(token, id_orden, f_cierre, 550.0)

        resultado = rmi_registry.listar_ordenes_por_filtro(token, {
            "fecha_desde": "2026-01-01",
            "fecha_hasta": "2026-03-31",
        })

        assert len(resultado) == 2
        for orden in resultado:
            assert orden["fecha_programada"] <= "2026-03-31"


class TestTC_SIS_22_CostoEstimadoNegativo:
    """TC-SIS-22 | RF-07, RN-17"""

    def test_sis22_costo_estimado_negativo_rechazado(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)

        # CORREGIDO: Espera ReglaNegocioError directamente
        with pytest.raises(ReglaNegocioError):
            rmi_registry.crear_orden(
                token=token,
                id_orden="ORD-NEG", id_equipo="EQ-701",
                tipo_mantenimiento="Electrico",
                fecha_programada="2026-06-20",
                descripcion_trabajo="Revisión",
                costo_estimado=-500.0,
            )


class TestTC_SIS_23_FechaCierreAnteriorFechaInicio:
    """TC-SIS-23 | RF-10, RN-05"""

    def test_sis23_fecha_cierre_anterior_a_fecha_inicio_rechazada(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-006", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-05-10",
            descripcion_trabajo="Revisión de sellos", costo_estimado=800.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-006", "TEC-702")
        rmi_registry.iniciar_ejecucion(token, "ORD-006", "2026-05-10")

        with pytest.raises(ReglaNegocioError):
            rmi_registry.finalizar_orden(token, "ORD-006", "2026-05-09", 800.0)


class TestTC_SIS_24_ReasignacionTecnico:
    """TC-SIS-24 | RF-07, RN-19"""

    def test_sis24_reasignar_tecnico_en_orden_programada(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")
        
        rmi_registry.alta_equipo(token, **EQUIPO_MECANICO)
        rmi_registry.alta_tecnico(token, **TECNICO_MECANICO_C2)
        rmi_registry.alta_tecnico(
            token,
            id_tecnico="TEC-PED", nombre_completo="Pedro Sánchez",
            rfc="SAPE900101DDD", telefono="9210005555",
            correo="pedro@sigomei.mx", especialidad="Mecanico",
            nivel_certificacion="II", fecha_ingreso="2023-06-01", estatus="Activo",
        )
        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-007", id_equipo="EQ-701",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-25",
            descripcion_trabajo="Mantenimiento mensual", costo_estimado=1300.0,
        )
        rmi_registry.asignar_tecnico(token, "ORD-007", "TEC-702")

        resultado = rmi_registry.asignar_tecnico(token, "ORD-007", "TEC-PED")

        assert resultado is True
        orden = rmi_registry.consultar_orden(token, "ORD-007")
        assert orden["id_tecnico"] == "TEC-PED"