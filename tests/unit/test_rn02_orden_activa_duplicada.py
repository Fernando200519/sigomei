"""
RN-02: Un equipo no puede tener dos órdenes activas
        (Programada o En ejecucion) en la misma fecha.
"""

import pytest
from server.exceptions.exceptions import EntidadDuplicadaError


class TestRN02OrdenActivaDuplicada:

    def test_crear_orden_mismo_equipo_misma_fecha_lanza_excepcion(self, orden_service):
        """
        DADO   que ya existe una orden activa para el equipo EQ-001 en la fecha 2026-06-01
        CUANDO se intenta crear otra orden para el mismo equipo en la misma fecha
        ENTONCES debe lanzar ReglaNegocioError
        """
        # Simulamos que ya hay una orden activa en esa fecha
        orden_service._equipo_dao.buscar_por_id.return_value = {"id_equipo": "EQ-001", "tipo": "Electrico"}
        orden_service._dao.listar_por_filtros.return_value = [
            {"id_orden": "OM-001", "estado_orden": "Programada", "fecha_programada": "2026-06-01"}
        ]

        with pytest.raises(EntidadDuplicadaError):
            orden_service.crear_orden(
                "OM-002", "EQ-001", "Preventivo",
                "2026-06-01", "Revisión general", 1500.0
            )

    def test_crear_orden_mismo_equipo_diferente_fecha_es_valida(self, orden_service):
        """
        DADO   que hay una orden activa para EQ-001 en 2026-06-01
        CUANDO se crea una orden para EQ-001 en una fecha diferente (2026-07-15)
        ENTONCES debe crearse sin error
        """
        orden_service._equipo_dao.buscar_por_id.return_value = {"id_equipo": "EQ-001", "tipo": "Electrico"}
        orden_service._dao.listar_por_filtros.return_value = []
        orden_service._dao.buscar_por_id.return_value = None
        orden_service._dao.insertar.return_value = True

        resultado = orden_service.crear_orden(
            "OM-003", "EQ-001", "Correctivo",
            "2026-07-15", "Cambio de fusibles", 800.0
        )
        assert resultado is True

    def test_crear_orden_equipo_con_orden_activa_misma_fecha_es_invalido(
        self, 
        orden_service,
        equipo_electrico_alta):
        orden_service._equipo_dao.buscar_por_id.return_value = (
            equipo_electrico_alta
        )

        orden_service._dao.listar_por_filtros.return_value = [
            {
                "id_orden": "OM-999",
                "estado_orden": "Programada",
                "fecha_programada": "2026-05-24"
            }
        ]

        with pytest.raises(EntidadDuplicadaError):
            orden_service.crear_orden(
                "OM-001",
                "EQ-001",
                "Preventivo",
                "2026-05-24",
                "Cambio de piezas",
                1000.0
            )

    def test_consultar_orden_es_valido(
        self, 
        orden_service
    ):
        orden = {
            "id_orden": "OM-001",
            "estado_orden": "Programada"
        }

        orden_service._dao.buscar_por_id.return_value = orden

        resultado = orden_service.consultar_orden(
            "OM-001"
        )

        assert resultado == orden

