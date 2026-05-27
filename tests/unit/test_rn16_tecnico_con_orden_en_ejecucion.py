import pytest

from server.exceptions.exceptions import ReglaNegocioError


def test_asignar_tecnico_con_orden_en_ejecucion_es_invalido(
    orden_service,
    equipo_electrico_alta,
    tecnico_activo_electricista_nivel2
):
    orden_service._dao.buscar_por_id.return_value = {
        "id_orden": "OM-001",
        "id_equipo": "EQ-001",
        "estado_orden": "Programada",
    }

    orden_service._equipo_dao.buscar_por_id.return_value = (
        equipo_electrico_alta
    )

    orden_service._tecnico_dao.buscar_por_id.return_value = (
        tecnico_activo_electricista_nivel2
    )

    orden_service._dao.listar_por_filtros.return_value = [
        {
            "id_orden": "OM-777",
            "estado_orden": "En ejecucion"
        }
    ]

    with pytest.raises(ReglaNegocioError):
        orden_service.asignar_tecnico(
            "OM-001",
            "TEC-001"
        )