"""
RN-04: No se permite eliminar un Equipo o un Técnico
        que tenga órdenes registradas.
"""

import pytest
from server.exceptions.exceptions import IntegridadReferencialError


class TestRN04IntegridadReferencial:

    def test_baja_equipo_con_ordenes_lanza_excepcion(self, equipo_service):
        """
        DADO   un equipo que tiene órdenes de mantenimiento registradas
        CUANDO se intenta darlo de baja
        ENTONCES debe lanzar IntegridadReferencialError
        """
        equipo_service._dao.buscar_por_id.return_value = {"id_equipo": "EQ-001"}
        equipo_service._dao.tiene_ordenes_vinculadas.return_value = True

        with pytest.raises(IntegridadReferencialError):
            equipo_service.baja_equipo("EQ-001")

    def test_baja_equipo_sin_ordenes_es_exitosa(self, equipo_service):
        """
        DADO   un equipo sin órdenes registradas
        CUANDO se intenta darlo de baja
        ENTONCES debe retornar True sin lanzar excepción
        """
        equipo_service._dao.buscar_por_id.return_value = {"id_equipo": "EQ-999"}
        equipo_service._dao.tiene_ordenes_vinculadas.return_value = False
        equipo_service._dao.eliminar.return_value = True

        resultado = equipo_service.baja_equipo("EQ-999")
        assert resultado is True

    def test_baja_tecnico_con_ordenes_activas_lanza_excepcion(self, tecnico_service):
        """
        DADO   un técnico con órdenes en estados activos
        CUANDO se intenta darlo de baja
        ENTONCES debe lanzar IntegridadReferencialError
        """
        tecnico_service._dao.buscar_por_id.return_value = {"id_tecnico": "TEC-001"}
        tecnico_service._dao.tiene_ordenes_activas.return_value = True

        with pytest.raises(IntegridadReferencialError):
            tecnico_service.baja_tecnico("TEC-001")

    def test_baja_tecnico_sin_ordenes_activas_es_exitosa(self, tecnico_service):
        """
        DADO   un técnico sin órdenes activas
        CUANDO se intenta darlo de baja
        ENTONCES debe retornar True sin lanzar excepción
        """
        tecnico_service._dao.buscar_por_id.return_value = {"id_tecnico": "TEC-999"}
        tecnico_service._dao.tiene_ordenes_activas.return_value = False
        tecnico_service._dao.eliminar.return_value = True

        resultado = tecnico_service.baja_tecnico("TEC-999")
        assert resultado is True