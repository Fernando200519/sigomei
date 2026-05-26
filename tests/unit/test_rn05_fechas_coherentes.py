"""
RN-05: fecha_cierre >= fecha_inicio >= fecha_programada
"""

from datetime import date

import pytest
from server.exceptions.exceptions import ReglaNegocioError
from server.service.orden_service import _parse_fecha


class TestRN05FechasCoherentes:

    def test_fecha_cierre_anterior_a_fecha_inicio_lanza_excepcion(self, orden_service):
        """
        DADO   una orden en estado 'En Ejecucion' con fecha_inicio = 2026-06-05
        CUANDO se intenta finalizar con fecha_cierre = 2026-06-01 (anterior)
        ENTONCES debe lanzar ReglaNegocioError
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-020",
            "estado_orden": "En Ejecucion",
            "fecha_programada": "2026-06-01",
            "fecha_inicio": "2026-06-05",
            "id_tecnico": "TEC-002",
        }

        with pytest.raises(ReglaNegocioError):
            orden_service.finalizar_orden("OM-020", "2026-06-01", 2000.0)

    def test_fecha_inicio_anterior_a_fecha_programada_lanza_excepcion(self, orden_service):
        """
        DADO   una orden con fecha_programada = 2026-06-10
        CUANDO se intenta iniciar con fecha_inicio = 2026-06-01 (anterior)
        ENTONCES debe lanzar ReglaNegocioError
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-021",
            "estado_orden": "Programada",
            "fecha_programada": "2026-06-10",
            "id_tecnico": "TEC-002",
        }

        with pytest.raises(ReglaNegocioError):
            orden_service.iniciar_ejecucion("OM-021", "2026-06-01")

    def test_fechas_en_orden_correcto_no_lanza_excepcion(self, orden_service):
        """
        DADO   fecha_programada=2026-06-01, fecha_inicio=2026-06-05, fecha_cierre=2026-06-10
        CUANDO se finaliza la orden
        ENTONCES debe retornar True sin lanzar excepción
        """
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden": "OM-022",
            "estado_orden": "En Ejecucion",
            "fecha_programada": "2026-06-01",
            "fecha_inicio": "2026-06-05",
            "id_tecnico": "TEC-002",
        }
        orden_service._dao.actualizar_cierre.return_value = True
        orden_service._dao.actualizar_estado.return_value = True

        resultado = orden_service.finalizar_orden("OM-022", "2026-06-10", 3000.0)
        assert resultado is True

    def test_parse_fecha_con_date_retorna_mismo_objeto(self):
        fecha = date(2026, 5, 24)

        resultado = _parse_fecha(fecha)

        assert resultado == fecha