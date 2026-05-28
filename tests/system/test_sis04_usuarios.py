import pytest

from server.exceptions.exceptions import IntegridadReferencialError, ReglaNegocioError

class TestTC_SIS_13_RegistrarTecnico:
    """TC-SIS-13 | RF-11, RN-15"""

    def test_sis13_registrar_tecnico_campos_completos(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")

        resultado = rmi_registry.alta_tecnico(
            token=token,
            id_tecnico="TEC-900",
            nombre_completo="Luis Omar Mendoza",
            rfc="LOMA900101ABC",
            telefono="9211234567",
            correo="luis@sigomei.mx",
            especialidad="Electrico",
            nivel_certificacion="II",
            fecha_ingreso="2026-01-01",
            estatus="Activo",
        )

        assert resultado is True

        tecnico = rmi_registry.consultar_tecnico(token, "TEC-900")

        assert tecnico["nombre_completo"] == "Luis Omar Mendoza"
        assert tecnico["estatus"].lower() == "activo"


class TestTC_SIS_15_BajaTecnicoSinOrdenes:
    """TC-SIS-15 | RF-15, RN-11, RN-04"""

    def test_sis15_baja_tecnico_aplica_borrado_logico(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")

        rmi_registry.alta_tecnico(
            token=token,
            id_tecnico="TEC-901",
            nombre_completo="Jose Ramírez",
            rfc="RAJM800101XYZ",
            telefono="9219876543",
            correo="jose@sigomei.mx",
            especialidad="Mecanico",
            nivel_certificacion="I",
            fecha_ingreso="2024-01-01",
            estatus="Activo",
        )

        rmi_registry.baja_tecnico(token, "TEC-901")

        tecnico = rmi_registry.consultar_tecnico(token, "TEC-901")

        assert tecnico is not None
        assert tecnico["estatus"].lower() == "inactivo"


class TestTC_SIS_16_BajaTecnicoConOrdenes:
    """TC-SIS-16 | RF-15, RN-04"""

    def test_sis16_baja_tecnico_con_ordenes_rechaza_eliminacion(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")

        rmi_registry.alta_equipo(
            token=token,
            id_equipo="EQ-H01",
            nombre="Bomba-01",
            tipo="Mecanico",
            marca="Grundfos",
            modelo="CM5-5",
            numero_serie="NS-H01",
            ubicacion_planta="Planta A",
            fecha_instalacion="2023-01-15",
            estado_operativo="Operativo",
            criticidad="Media",
        )

        rmi_registry.alta_tecnico(
            token=token,
            id_tecnico="TEC-902",
            nombre_completo="Carlos López",
            rfc="LOCC850101CCC",
            telefono="9210002222",
            correo="carlos@sigomei.mx",
            especialidad="Mecanico",
            nivel_certificacion="II",
            fecha_ingreso="2023-01-01",
            estatus="Activo",
        )

        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-H01",
            id_equipo="EQ-H01",
            tipo_mantenimiento="Mecanico",
            fecha_programada="2026-01-10",
            descripcion_trabajo="Revisión histórica",
            costo_estimado=500.0,
        )

        rmi_registry.asignar_tecnico(token, "ORD-H01", "TEC-902")

        rmi_registry.iniciar_ejecucion(token, "ORD-H01", "2026-01-10")

        rmi_registry.finalizar_orden(token, "ORD-H01", "2026-01-11", 550.0)

        with pytest.raises(IntegridadReferencialError):
            rmi_registry.baja_tecnico(token, "TEC-902")
        

class TestTC_SIS_17_TecnicoInactivoAsignacion:
    """TC-SIS-17 | RF-07, RN-03"""

    def test_sis17_tecnico_inactivo_no_puede_ser_asignado(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")

        rmi_registry.alta_equipo(
            token=token,
            id_equipo="EQ-902",
            nombre="Motor-01",
            tipo="Mecanico",
            marca="WEG",
            modelo="W22",
            numero_serie="NS-902",
            ubicacion_planta="Planta B",
            fecha_instalacion="2023-06-01",
            estado_operativo="Operativo",
            criticidad="Media",
        )

        rmi_registry.alta_tecnico(
            token=token,
            id_tecnico="TEC-903",
            nombre_completo="Jose Ramírez",
            rfc="RAJM800202XYZ",
            telefono="9210003333",
            correo="jose2@sigomei.mx",
            especialidad="Mecanico",
            nivel_certificacion="I",
            fecha_ingreso="2024-01-01",
            estatus="Activo",
        )

        rmi_registry.baja_tecnico(token, "TEC-903")

        rmi_registry.crear_orden(
            token=token,
            id_orden="ORD-902",
            id_equipo="EQ-902",
            tipo_mantenimiento="Electrico",
            fecha_programada="2026-06-20",
            descripcion_trabajo="Reparación",
            costo_estimado=800.0,
        )

        with pytest.raises(ReglaNegocioError):
            rmi_registry.asignar_tecnico(token, "ORD-902", "TEC-903")
            

class TestTC_SIS_21_FiltroTecnicos:
    """TC-SIS-21 | RF-18"""

    def test_sis21_consulta_tecnicos_filtro(self, rmi_registry, db_test):
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")

        rmi_registry.alta_tecnico(
            token=token,
            id_tecnico="TEC-E2A",
            nombre_completo="Ana Torres",
            rfc="TOEA900101EEE",
            telefono="9210000001",
            correo="ana@sigomei.mx",
            especialidad="Electrico",
            nivel_certificacion="II",
            fecha_ingreso="2025-01-01",
            estatus="Activo",
        )

        rmi_registry.alta_tecnico(
            token=token,
            id_tecnico="TEC-M1A",
            nombre_completo="Carlos Vega",
            rfc="VECC900202MMM",
            telefono="9210000002",
            correo="vegac@sigomei.mx",
            especialidad="Mecanico",
            nivel_certificacion="I",
            fecha_ingreso="2025-01-01",
            estatus="Activo",
        )

        resultado = rmi_registry.listar_tecnicos_por_filtro(
            token, 
            {
                "especialidad": "Electrico",
                "nivel_certificacion": "II"
            }
        )

        assert isinstance(resultado, list)
        assert len(resultado) >= 1

        for tecnico in resultado:
            assert tecnico["especialidad"] == "Electrico"
            assert tecnico["nivel_certificacion"] == "II"

class TestTC_SIS_09_SolicitarCierre:
    """TC-SIS-09 | Técnico solicita cierre de orden en ejecución (RF-09)"""

    def test_sis09_tecnico_solicita_cierre_orden_en_ejecucion(self, rmi_registry, db_test):
        """
        DADA una orden 'ORD-003' en estado 'En ejecucion' asignada al Técnico María Solano
        CUANDO la Técnico solicita el cierre de la orden
        ENTONCES el estado de la orden cambia exitosamente a 'Pendiente de cierre'.
        """
        token_sup = rmi_registry.login("luis.torres@empresa.mx", "Test1234")
        
        equipo_test = dict(
            id_equipo="EQ-799", nombre="Compresor RMI", tipo="Mecanico",
            marca="Atlas", modelo="GA-90", numero_serie="NS-799",
            ubicacion_planta="Planta A", fecha_instalacion="2023-01-15",
            estado_operativo="Operativo", criticidad="Media"
        )
        rmi_registry.alta_equipo(token_sup, **equipo_test)

        rmi_registry.crear_orden(
            token=token_sup,
            id_orden="ORD-003", id_equipo="EQ-799",
            tipo_mantenimiento="Mecanico", fecha_programada="2026-06-10",
            descripcion_trabajo="Mantenimiento preventivo de válvulas", costo_estimado=1200.0,
        )
        
        rmi_registry.asignar_tecnico(token_sup, "ORD-003", "TEC-001")
        rmi_registry.iniciar_ejecucion(token_sup, "ORD-003", "2026-06-10")

        token_tec = rmi_registry.login("maria.solano@empresa.mx", "temporal123")

        resultado = rmi_registry.solicitar_cierre(token_tec, "ORD-003")

        assert resultado is True
        
        orden = rmi_registry.consultar_orden(token_tec, "ORD-003")
        assert orden["estado_orden"].lower() == "pendiente de cierre"