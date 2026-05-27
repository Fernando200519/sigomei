"""
RN-08: Transiciones permitidas:
         Programada → En ejecucion → Finalizada
         Cancelada solo desde Programada o En ejecucion.
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

    def test_finalizar_con_todos_los_campos_es_exitoso(self, orden_service):
        """
        DADO   una orden en 'En ejecucion' con todos los datos correctos
        CUANDO se finaliza
        ENTONCES debe retornar True
        """
        from datetime import datetime

        orden_service._dao.obtener_id_orden_int.return_value = 32

        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 32,
            "id_orden": "OM-032",
            "estado_orden": "En ejecucion",
            "fecha_programada": "2026-05-01",
            "fecha_inicio": datetime(2026, 5, 5, 0, 0, 0),
            "id_tecnico_int": 2,
        }
        orden_service._dao.actualizar_cierre.return_value = True
        orden_service._dao.actualizar_estado.return_value = True

        resultado = orden_service.finalizar_orden("OM-032", "2026-05-10", 2500.0)
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
            "estado_orden": "En ejecucion",
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

