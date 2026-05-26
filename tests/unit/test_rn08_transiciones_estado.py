"""
RN-08: Transiciones permitidas:
         Programada → En Ejecucion → Finalizada
         Cancelada solo desde Programada o En Ejecucion.
       Cualquier otra transición debe ser rechazada.
"""

import pytest
from server.exceptions.exceptions import EntidadNoEncontradaError, EstadoInvalidoError


class TestRN08TransicionesEstado:

    def test_iniciar_orden_programada_es_valido(self, orden_service):
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-050",
            "estado_orden": "Programada",
            "fecha_programada": "2026-06-01",
            "id_tecnico": "TEC-002",
        }
        orden_service._dao.actualizar_estado.return_value = True
        orden_service._dao.actualizar_inicio.return_value = True

        resultado = orden_service.iniciar_ejecucion("OM-050", "2026-06-01")
        assert resultado is True

    def test_iniciar_orden_ya_finalizada_lanza_excepcion(self, orden_service):
        """No se puede reabrir una orden ya finalizada."""
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-051",
            "estado_orden": "Finalizada",
            "id_tecnico": "TEC-002",
        }

        with pytest.raises(EstadoInvalidoError):
            orden_service.iniciar_ejecucion("OM-051", "2026-06-15")

    def test_finalizar_orden_en_ejecucion_es_valido(self, orden_service):
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-052",
            "estado_orden": "En Ejecucion",
            "fecha_programada": "2026-06-01",
            "fecha_inicio": "2026-06-03",
            "id_tecnico": "TEC-002",
        }
        orden_service._dao.actualizar_cierre.return_value = True
        orden_service._dao.actualizar_estado.return_value = True

        resultado = orden_service.finalizar_orden("OM-052", "2026-06-10", 1800.0)
        assert resultado is True

    def test_finalizar_orden_programada_lanza_excepcion(self, orden_service):
        """No se puede finalizar una orden que no está 'En Ejecucion'."""
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-053",
            "estado_orden": "Programada",
            "fecha_programada": "2026-06-01",
            "id_tecnico": "TEC-002",
        }

        with pytest.raises(EstadoInvalidoError):
            orden_service.finalizar_orden("OM-053", "2026-06-10", 1800.0)

    def test_cancelar_orden_programada_es_valido(self, orden_service):
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-054",
            "estado_orden": "Programada",
        }
        orden_service._dao.actualizar_estado.return_value = True

        resultado = orden_service.cancelar_orden("OM-054")
        assert resultado is True

    def test_cancelar_orden_en_ejecucion_es_valido(self, orden_service):
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-055",
            "estado_orden": "En Ejecucion",
        }
        orden_service._dao.actualizar_estado.return_value = True

        resultado = orden_service.cancelar_orden("OM-055")
        assert resultado is True

    def test_cancelar_orden_finalizada_lanza_excepcion(self, orden_service):
        """No se puede cancelar una orden ya finalizada."""
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-056",
            "estado_orden": "Finalizada",
        }

        with pytest.raises(EstadoInvalidoError):
            orden_service.cancelar_orden("OM-056")
    
    def test_iniciar_ejecucion_orden_no_existente_es_invalido(
        self, 
        orden_service
    ):
        orden_service._dao.buscar_por_id.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.iniciar_ejecucion(
                "OM-001",
                "2026-05-24"
            )


    def test_finalizar_orden_no_existente_es_invalido(
        self, orden_service
    ):
        orden_service._dao.buscar_por_id.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.finalizar_orden(
                "OM-001",
                "2026-05-25",
                1500.0
            )


    def test_cancelar_orden_no_existente_es_invalido(
        self, orden_service
    ):
        orden_service._dao.buscar_por_id.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.cancelar_orden(
                "OM-001"
            )

