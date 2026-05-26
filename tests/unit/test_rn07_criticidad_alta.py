"""
RN-07: Los equipos de criticidad 'Alta' requieren tecnicos
        con nivel de certificacion II o III.
"""

import pytest
from server.exceptions.exceptions import ReglaNegocioError


class TestRN07CriticidadAlta:

    def test_equipo_alta_criticidad_con_tecnico_nivel1_lanza_excepcion(
        self, orden_service, equipo_electrico_alta
    ):
        """
        DADO   una orden para un equipo con criticidad 'Alta'
        CUANDO se asigna un tecnico con nivel de certificacion I
        ENTONCES debe lanzar ReglaNegocioError
        """
        tecnico_nivel1 = {
            "id_tecnico": "TEC-010",
            "especialidad": "Electrico",
            "nivel_certificacion": "I",
            "estatus": "Activo",
        }
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-040",
            "id_equipo": "EQ-001",
            "estado_orden": "Programada",
            "id_tecnico": None,
        }
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_nivel1

        with pytest.raises(ReglaNegocioError):
            orden_service.asignar_tecnico("OM-040", "TEC-010")

    def test_equipo_alta_criticidad_con_tecnico_nivel2_es_valido(
        self, orden_service, equipo_electrico_alta, tecnico_activo_electricista_nivel2
    ):
        """
        DADO   una orden para un equipo con criticidad 'Alta'
        CUANDO se asigna un tecnico con nivel de certificacion II
        ENTONCES debe asignarse correctamente sin error
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-041",
            "id_equipo": "EQ-001",
            "estado_orden": "Programada",
            "id_tecnico": None,
        }
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_activo_electricista_nivel2
        orden_service._dao.asignar_tecnico.return_value = True
        orden_service._dao.listar_por_filtros.return_value = None

        resultado = orden_service.asignar_tecnico("OM-041", "TEC-002")
        assert resultado is True

    def test_equipo_baja_criticidad_con_tecnico_nivel1_es_valido(
        self, orden_service, equipo_mecanico_baja
    ):
        """
        DADO   una orden para un equipo con criticidad 'Baja'
        CUANDO se asigna un tecnico con nivel de certificacion I
        ENTONCES debe ser valido (RN-07 no aplica)
        """
        tecnico_mecanico_nivel1 = {
            "id_tecnico": "TEC-011",
            "especialidad": "Mecanico",
            "nivel_certificacion": "I",
            "estatus": "Activo",
        }
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-042",
            "id_equipo": "EQ-002",
            "estado_orden": "Programada",
            "id_tecnico": None,
        }
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_mecanico_baja
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_mecanico_nivel1
        orden_service._dao.asignar_tecnico.return_value = True
        orden_service._dao.listar_por_filtros.return_value = None

        resultado = orden_service.asignar_tecnico("OM-042", "TEC-011")
        assert resultado is True