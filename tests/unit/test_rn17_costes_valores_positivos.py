import pytest

from server.exceptions.exceptions import (
    ReglaNegocioError,
)


def test_crear_orden_costo_estimado_negativo_es_invalido(
    orden_service,
    equipo_electrico_alta
):
    orden_service._equipo_dao.buscar_por_id.return_value = (
        equipo_electrico_alta
    )

    with pytest.raises(ReglaNegocioError):
        orden_service.crear_orden(
            "OM-001",
            "EQ-001",
            "Preventivo",
            "2026-05-24",
            "Cambio de piezas",
            -100.0

        )