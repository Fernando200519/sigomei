"""
RN-07: Los equipos de criticidad 'Alta' requieren técnicos
        con nivel de certificación II o III.
"""

import pytest
from server.exceptions.exceptions import ReglaNegocioError


class TestRN07CriticidadAlta:

    def test_equipo_alta_criticidad_con_tecnico_nivel1_lanza_excepcion(
        self, orden_service, equipo_electrico_alta
    ):
        """
        DADO   una orden para un equipo con criticidad 'Alta'
        CUANDO se asigna un técnico con nivel de certificación I
        ENTONCES debe lanzar ReglaNegocioError
        """
        tecnico_nivel1 = {
            "id_tecnico_int": 10,
            "id_tecnico": "TEC-010",
            "especialidad": "Electrico",
            "nivel_certificacion": "I",
            "estatus": "Activo",
        }
        
        orden_service._dao.obtener_id_orden_int.return_value = 40
        orden_service._tecnico_dao.obtener_id_tecnico_int.return_value = 10

        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 40,
            "id_orden": "OM-040",
            "id_equipo_int": 1,  
            "estado_orden": "Programada",
            "id_tecnico_int": None,
        }
        
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_nivel1
        orden_service._dao.listar_por_filtros.return_value = []

        with pytest.raises(ReglaNegocioError):
            orden_service.asignar_tecnico("OM-040", "TEC-010")

    def test_equipo_alta_criticidad_con_tecnico_nivel2_es_valido(
        self, orden_service, equipo_electrico_alta, tecnico_activo_electricista_nivel2
    ):
        """
        DADO   una orden para un equipo con criticidad 'Alta'
        CUANDO se asigna un técnico con nivel de certificación II
        ENTONCES debe asignarse correctamente sin error
        """
        orden_service._dao.obtener_id_orden_int.return_value = 41
        orden_service._tecnico_dao.obtener_id_tecnico_int.return_value = 2

        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 41,
            "id_orden": "OM-041",
            "id_equipo_int": 1,
            "estado_orden": "Programada",
            "id_tecnico_int": None,
        }
        
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_activo_electricista_nivel2
        orden_service._dao.asignar_tecnico.return_value = True
        
        orden_service._dao.listar_por_filtros.return_value = []

        resultado = orden_service.asignar_tecnico("OM-041", "TEC-002")
        assert resultado is True

    def test_equipo_baja_criticidad_con_tecnico_nivel1_es_valido(
        self, orden_service, equipo_mecanico_baja
    ):
        """
        DADO   una orden para un equipo con criticidad 'Baja'
        CUANDO se asigna un técnico con nivel de certificación I
        ENTONCES debe ser válido (RN-07 no aplica)
        """
        tecnico_mecanico_nivel1 = {
            "id_tecnico_int": 11,
            "id_tecnico": "TEC-011",
            "especialidad": "Mecanico",
            "nivel_certificacion": "I",
            "estatus": "Activo",
        }
        
        orden_service._dao.obtener_id_orden_int.return_value = 42
        orden_service._tecnico_dao.obtener_id_tecnico_int.return_value = 11

        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 42,
            "id_orden": "OM-042",
            "id_equipo_int": 2,
            "estado_orden": "Programada",
            "id_tecnico_int": None,
        }
        
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_mecanico_baja
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_mecanico_nivel1
        orden_service._dao.asignar_tecnico.return_value = True
        
        orden_service._dao.listar_por_filtros.return_value = []

        resultado = orden_service.asignar_tecnico("OM-042", "TEC-011")
        assert resultado is True