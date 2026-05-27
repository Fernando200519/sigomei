"""
RN-01: La especialidad del técnico asignado debe coincidir
       con el tipo del equipo de la orden.
"""

import pytest
from server.exceptions.exceptions import ReglaNegocioError


class TestRN01EspecialidadTecnico:

    def test_asignar_tecnico_especialidad_incorrecta_lanza_excepcion(
        self, orden_service, equipo_electrico_alta, tecnico_activo_electricista_nivel1
    ):
        """
        DADO   una orden vinculada a un equipo de tipo 'Eléctrico'
        CUANDO se intenta asignar un técnico con especialidad 'Mecanico'
        ENTONCES debe lanzar ReglaNegocioError
        """
        # 1. Simular las resoluciones de IDs de negocio a enteros internos
        orden_service._dao.obtener_id_orden_int.return_value = 1
        orden_service._tecnico_dao.obtener_id_tecnico_int.return_value = 4

        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 1,
            "id_orden": "OM-001",
            "id_equipo_int": 10,
            "estado_orden": "Programada",
            "id_tecnico_int": None,
        }
        
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_activo_electricista_nivel1

        orden_service._dao.listar_por_filtros.return_value = []

        with pytest.raises(ReglaNegocioError):
            orden_service.asignar_tecnico("OM-001", "TEC-001")

    def test_asignar_tecnico_especialidad_correcta_no_lanza_excepcion(
        self, orden_service, equipo_electrico_alta, tecnico_activo_electricista_nivel2
    ):
        """
        DADO   una orden vinculada a un equipo de tipo 'Eléctrico'
        CUANDO se asigna un técnico con especialidad 'Eléctrico' y certificación II
        ENTONCES NO debe lanzar ReglaNegocioError
        """
        orden_service._dao.obtener_id_orden_int.return_value = 1
        orden_service._tecnico_dao.obtener_id_tecnico_int.return_value = 5

        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 1,
            "id_orden": "OM-001",
            "id_equipo_int": 10,
            "estado_orden": "Programada",
            "id_tecnico_int": None,
        }
        
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_activo_electricista_nivel2
        orden_service._dao.asignar_tecnico.return_value = True
        
        orden_service._dao.listar_por_filtros.return_value = []

        resultado = orden_service.asignar_tecnico("OM-001", "TEC-002")
        assert resultado is True