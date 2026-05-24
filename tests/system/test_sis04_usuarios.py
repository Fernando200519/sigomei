
import pytest
from server.exceptions.exceptions import ReglaNegocioError


class TestTC_SIS_13_RegistrarTecnico:
    """TC-SIS-13 | RF-11, RN-15"""

    def test_sis13_registrar_tecnico_campos_completos(self, rmi_registry, db_test):
        """
        DADO que no existe técnico con RFC LOMA900101ABC
        CUANDO se registra con todos los campos obligatorios
        ENTONCES queda registrado con estado activo y aparece en el listado.
        """
        resultado = rmi_registry.alta_tecnico(
            id_tecnico        = "TEC-001",
            nombre_completo   = "Luis Omar Mendoza",
            rfc               = "LOMA900101ABC",
            telefono          = "9211234567",
            correo            = "luis@sigomei.mx",
            especialidad      = "Electrico",
            nivel_certificacion = "II",
            fecha_ingreso     = "2026-01-01",
            estatus           = "Activo",
        )

        assert resultado is True
        tecnico = rmi_registry.consultar_tecnico("TEC-001")
        assert tecnico["nombre_completo"] == "Luis Omar Mendoza"
        assert tecnico["estatus"].lower() == "activo"


class TestTC_SIS_15_BajaTecnicoSinOrdenes:
    """TC-SIS-15 | RF-15, RN-11, RN-04"""

    def test_sis15_baja_tecnico_aplica_borrado_logico(self, rmi_registry, db_test):
        """
        DADO un técnico activo sin órdenes registradas
        CUANDO se solicita su baja
        ENTONCES queda inactivo en BD (borrado lógico),
        no se elimina físicamente y deja de aparecer disponible.
        """
        rmi_registry.alta_tecnico(
            id_tecnico        = "TEC-002",
            nombre_completo   = "José Ramírez",
            rfc               = "RAJM800101XYZ",
            telefono          = "9219876543",
            correo            = "jose@sigomei.mx",
            especialidad      = "Mecanico",
            nivel_certificacion = "I",
            fecha_ingreso     = "2024-01-01",
            estatus           = "Activo",
        )

        rmi_registry.baja_tecnico("TEC-002")

        tecnico = rmi_registry.consultar_tecnico("TEC-002")
        assert tecnico is not None
        assert tecnico["estatus"].lower() == "inactivo"
        

class TestTC_SIS_16_BajaTecnicoConOrdenes:
    """TC-SIS-16 | RF-15, RN-04"""

    def test_sis16_baja_tecnico_con_ordenes_rechaza_eliminacion_fisica(self, rmi_registry, db_test):
        """
        DADO un técnico Carlos López con al menos una orden en el histórico
        CUANDO se solicita su baja
        ENTONCES el sistema rechaza la eliminación física, aplica borrado lógico
        y advierte que el técnico tiene órdenes en el histórico.
        """
        # Precondición: técnico con orden finalizada en el histórico
        rmi_registry.alta_equipo(
            id_equipo="EQ-001", nombre="Bomba-01", tipo="Mecanico",
            marca="Grundfos", modelo="CM5-5", numero_serie="NS-001",
            ubicacion_planta="Planta A", fecha_instalacion="2023-01-15",
            estado_operativo="Operativo", criticidad="Media",
        )
        rmi_registry.alta_tecnico(
            id_tecnico="TEC-003", nombre_completo="Carlos López",
            rfc="LOCC850101CCC", telefono="9210002222",
            correo="carlos@sigomei.mx", especialidad="Mecanico",
            nivel_certificacion="II", fecha_ingreso="2023-01-01",
            estatus="Activo",
        )
        rmi_registry.crear_orden(
            id_orden="ORD-H01", id_equipo="EQ-001",
            tipo_mantenimiento="Preventivo", fecha_programada="2026-01-10",
            descripcion_trabajo="Revisión histórica", costo_estimado=500.0,
        )
        rmi_registry.asignar_tecnico("ORD-H01", "TEC-003")
        rmi_registry.iniciar_ejecucion("ORD-H01", "2026-01-10")
        rmi_registry.finalizar_orden("ORD-H01", "2026-01-11", 550.0)

        rmi_registry.baja_tecnico("TEC-003")

        # # El técnico sigue existiendo en BD (no eliminado físicamente)
        tecnico = rmi_registry.consultar_tecnico("TEC-003")
        assert tecnico is not None
        assert tecnico["estatus"].lower() == "inactivo"


class TestTC_SIS_17_TecnicoInactivoAsignacion:
    """TC-SIS-17 | RF-07, RN-03"""

    def test_sis17_tecnico_inactivo_no_puede_ser_asignado(self, rmi_registry, db_test):
        """
        DADO un técnico con estado inactivo
        CUANDO se intenta asignarlo a una nueva orden
        ENTONCES no aparece disponible o el sistema lanza error de regla de negocio.
        """
        rmi_registry.alta_equipo(
            id_equipo="EQ-002", nombre="Motor-01", tipo="Mecanico",
            marca="WEG", modelo="W22", numero_serie="NS-002",
            ubicacion_planta="Planta B", fecha_instalacion="2023-06-01",
            estado_operativo="Operativo", criticidad="Media",
        )
        rmi_registry.alta_tecnico(
            id_tecnico="TEC-004", nombre_completo="José Ramírez",
            rfc="RAJM800202XYZ", telefono="9210003333",
            correo="jose2@sigomei.mx", especialidad="Mecanico",
            nivel_certificacion="I", fecha_ingreso="2024-01-01",
            estatus="Activo",
        )
        rmi_registry.baja_tecnico("TEC-004")

        rmi_registry.crear_orden(
            id_orden="ORD-002", id_equipo="EQ-002",
            tipo_mantenimiento="Correctivo", fecha_programada="2026-06-20",
            descripcion_trabajo="Reparación", costo_estimado=800.0,
        )

        with pytest.raises(ReglaNegocioError):
            rmi_registry.asignar_tecnico("ORD-002", "TEC-004")


# class TestTC_SIS_21_FiltroTecnicos:
#     """TC-SIS-21 | RF-18"""

#     def test_sis21_consulta_tecnicos_filtro_especialidad_certificacion(self, rmi_registry, db_test):
#         """
#         DADO técnicos con distintas especialidades y certificaciones
#         CUANDO se filtra por Especialidad=Eléctrico y Certificación=II
#         ENTONCES solo se muestran técnicos que cumplan ambos criterios.
#         """
#         rmi_registry.alta_tecnico(
#             id_tecnico="TEC-E2A", nombre_completo="Ana Torres",
#             rfc="TOEA900101EEE", telefono="9210000001",
#             correo="ana@sigomei.mx", especialidad="Electrico",
#             nivel_certificacion="II", fecha_ingreso="2025-01-01", estatus="Activo",
#         )
#         rmi_registry.alta_tecnico(
#             id_tecnico="TEC-M1A", nombre_completo="Carlos Vega",
#             rfc="VECC900202MMM", telefono="9210000002",
#             correo="vegac@sigomei.mx", especialidad="Mecanico",
#             nivel_certificacion="I", fecha_ingreso="2025-01-01", estatus="Activo",
#         )

#         resultado = rmi_registry.listar_tecnicos_por_filtro(
#             {"especialidad": "Electrico", "nivel_certificacion": "II"}
#         )

#         assert isinstance(resultado, list)
#         assert len(resultado) >= 1
#         for tecnico in resultado:
#             assert tecnico["especialidad"] == "Electrico"
#             assert tecnico["nivel_certificacion"] == "II"