"""
RN-06: Solo las órdenes en estado 'Finalizada' deben tener
        costo_real y fecha_cierre registrados.
        → Finalizar sin costo_real o sin fecha_cierre debe fallar.
"""

import pytest
from server.exceptions.exceptions import ReglaNegocioError


class TestRN06CamposEstadoFinalizada:

    def test_finalizar_sin_costo_real_lanza_excepcion(self, orden_service):
        """
        DADO   una orden en 'En ejecucion'
        CUANDO se intenta finalizar con costo_real = None
        ENTONCES debe lanzar ReglaNegocioError
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-030",
            "estado_orden": "En ejecucion",
            "fecha_programada": "2026-05-01",
            "fecha_inicio": "2026-05-05",
            "id_tecnico": "TEC-002",
        }

        with pytest.raises(ReglaNegocioError):
            orden_service.finalizar_orden("OM-030", "2026-05-10", None)

    def test_finalizar_sin_fecha_cierre_lanza_excepcion(self, orden_service):
        """
        DADO   una orden en 'En ejecucion'
        CUANDO se intenta finalizar con fecha_cierre = None
        ENTONCES debe lanzar ReglaNegocioError
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-031",
            "estado_orden": "En ejecucion",
            "fecha_programada": "2026-05-01",
            "fecha_inicio": "2026-05-05",
            "id_tecnico": "TEC-002",
        }

        with pytest.raises(ReglaNegocioError):
            orden_service.finalizar_orden("OM-031", None, 1500.0)

    def test_finalizar_con_todos_los_campos_es_exitoso(self, orden_service):
        """
        DADO   una orden en 'En ejecucion' con todos los datos correctos
        CUANDO se finaliza
        ENTONCES debe retornar True
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-032",
            "estado_orden": "En ejecucion",
            "fecha_programada": "2026-05-01",
            "fecha_inicio": "2026-05-05",
            "id_tecnico": "TEC-002",
        }
        orden_service._dao.actualizar_cierre.return_value = True
        orden_service._dao.actualizar_estado.return_value = True

        resultado = orden_service.finalizar_orden("OM-032", "2026-05-10", 2500.0)
        assert resultado is True