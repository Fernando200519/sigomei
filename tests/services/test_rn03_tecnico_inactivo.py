"""
RN-03: Un técnico con estatus 'Inactivo' no puede ser
        asignado a nuevas órdenes.
"""

import pytest
from server.exceptions.exceptions import ReglaNegocioError


class TestRN03TecnicoInactivo:

    def test_asignar_tecnico_inactivo_lanza_excepcion(
        self, orden_service, equipo_electrico_alta, tecnico_inactivo
    ):
        """
        DADO   un técnico con estatus 'Inactivo'
        CUANDO se intenta asignarlo a una orden en estado 'Programada'
        ENTONCES debe lanzar ReglaNegocioError
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-010",
            "id_equipo": "EQ-001",
            "estado_orden": "Programada",
            "id_tecnico": None,
        }
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_inactivo

        with pytest.raises(ReglaNegocioError):
            orden_service.asignar_tecnico("OM-010", "TEC-003")

    def test_asignar_tecnico_activo_no_lanza_excepcion(
        self, orden_service, equipo_electrico_alta, tecnico_activo_electricista_nivel2
    ):
        """
        DADO   un técnico con estatus 'Activo' y especialidad correcta
        CUANDO se intenta asignarlo
        ENTONCES no debe lanzar ReglaNegocioError
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-010",
            "id_equipo": "EQ-001",
            "estado_orden": "Programada",
            "id_tecnico": None,
        }
        orden_service._equipo_dao.buscar_por_id.return_value = equipo_electrico_alta
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_activo_electricista_nivel2
        orden_service._dao.asignar_tecnico.return_value = True

        resultado = orden_service.asignar_tecnico("OM-010", "TEC-002")
        assert resultado is True