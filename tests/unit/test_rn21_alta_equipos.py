"""
RN-21: Solo los Supervisores Operativos / Coordinadores pueden gestionar equipos


"""


import pytest
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    IntegridadReferencialError,
)


class TestRN21AltaEquipos:

    def test_dar_de_alta_equipo_es_valido(
        self,
        equipo_service,
        equipo_electrico_alta
    ):
        equipo_service._dao.obtener_id_equipo_int.return_value = None
        equipo_service._dao.buscar_por_numero_serie.return_value = None
        equipo_service._dao.insertar.return_value = True

        resultado = equipo_service.alta_equipo(
            **equipo_electrico_alta
        )

        assert resultado is True

    def test_dar_de_alta_equipo_tipo_invalido_es_invalido(
        self,
        equipo_service,
        equipo_electrico_alta
    ):
        equipo_electrico_alta["tipo"] = "Electromecanico"

        with pytest.raises(ReglaNegocioError):
            equipo_service.alta_equipo(
                **equipo_electrico_alta
            )

    def test_dar_de_alta_equipo_criticidad_invalida_es_invalido(
        self,
        equipo_service,
        equipo_electrico_alta
    ):
        equipo_electrico_alta["criticidad"] = "Urgente"

        with pytest.raises(ReglaNegocioError):
            equipo_service.alta_equipo(
                **equipo_electrico_alta
            )

    def test_dar_de_alta_equipo_estado_operativo_invalido_es_invalido(
        self,
        equipo_service,
        equipo_electrico_alta
    ):
        equipo_electrico_alta["estado_operativo"] = "Suspendido"

        with pytest.raises(ReglaNegocioError):
            equipo_service.alta_equipo(
                **equipo_electrico_alta
            )

    def test_dar_de_alta_equipo_id_duplicado_es_invalido(
        self,
        equipo_service,
        equipo_electrico_alta
    ):
        equipo_service._dao.buscar_por_id.return_value = {
            "id_equipo": "EQ-001"
        }

        with pytest.raises(EntidadDuplicadaError):
            equipo_service.alta_equipo(
                **equipo_electrico_alta
            )

    def test_dar_de_alta_equipo_numero_serie_duplicado_es_invalido(
        self,
        equipo_service,
        equipo_electrico_alta
    ):
        equipo_service._dao.buscar_por_id.return_value = None
        equipo_service._dao.buscar_por_numero_serie.return_value = {
            "numero_serie": "SER-001"
        }

        with pytest.raises(EntidadDuplicadaError):
            equipo_service.alta_equipo(
                **equipo_electrico_alta
            )

    def test_consultar_equipo_es_valido(
        self,
        equipo_service
    ):
        equipo = {
            "id_equipo": "EQ-999",
            "nombre": "Motor Industrial"
        }

        equipo_service._dao.buscar_por_id.return_value = equipo

        resultado = equipo_service.consultar_equipo(
            "EQ-999"
        )

        assert resultado == equipo

    def test_consultar_equipo_no_existente_es_invalido(
        self,
        equipo_service
    ):
        equipo_service._dao.obtener_id_equipo_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            equipo_service.consultar_equipo(
                "EQ-999"
            )

    def test_actualizar_equipo_es_valido(
        self,
        equipo_service
    ):
        equipo_service._dao.buscar_por_id.return_value = {
            "id_equipo": "EQ-999"
        }

        equipo_service._dao.actualizar.return_value = True

        resultado = equipo_service.modificar_equipo(
            "EQ-999",
            {
                "criticidad": "Alta"
            }
        )

        assert resultado is True

    def test_actualizar_equipo_no_existente_es_invalido(
        self,
        equipo_service
    ):
        equipo_service._dao.obtener_id_equipo_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            equipo_service.modificar_equipo(
                "EQ-999",
                {
                    "criticidad": "Alta"
                }
            )

    def test_actualizar_equipo_tipo_incorrecto_es_invalido(
        self,
        equipo_service
    ):
        equipo_service._dao.buscar_por_id.return_value = {
            "id_equipo": "EQ-999"
        }

        with pytest.raises(ReglaNegocioError):
            equipo_service.modificar_equipo(
                "EQ-999",
                {
                    "tipo": "Electromecanico"
                }
            )

    def test_actualizar_equipo_criticidad_incorrecta_es_invalido(
        self,
        equipo_service
    ):
        equipo_service._dao.buscar_por_id.return_value = {
            "id_equipo": "EQ-999"
        }

        with pytest.raises(ReglaNegocioError):
            equipo_service.modificar_equipo(
                "EQ-999",
                {
                    "criticidad": "Ninguna"
                }
            )

    def test_dar_de_baja_equipo_es_valido(
        self,
        equipo_service
    ):
        equipo_service._dao.buscar_por_id.return_value = {
            "id_equipo": "EQ-999"
        }

        equipo_service._dao.tiene_ordenes_vinculadas.return_value = False
        equipo_service._dao.eliminar.return_value = True

        resultado = equipo_service.baja_equipo(
            "EQ-999"
        )

        assert resultado is True

    def test_dar_de_baja_equipo_no_existente_es_invalido(
        self,
        equipo_service
    ):
        equipo_service._dao.obtener_id_equipo_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            equipo_service.baja_equipo(
                "EQ-999"
            )

    def test_dar_de_baja_equipo_con_ordenes_vinculadas_es_invalido(
        self,
        equipo_service
    ):
        equipo_service._dao.buscar_por_id.return_value = {
            "id_equipo": "EQ-999"
        }

        equipo_service._dao.tiene_ordenes_vinculadas.return_value = True

        with pytest.raises(IntegridadReferencialError):
            equipo_service.baja_equipo(
                "EQ-999"
            )