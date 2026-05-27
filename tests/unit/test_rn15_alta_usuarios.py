import pytest

from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    IntegridadReferencialError,
)


class TestRN15AltaTecnicos:

    def test_dar_de_alta_tecnico_es_valido(
        self,
        tecnico_service,
        tecnico_activo_electricista_nivel2
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = None
        tecnico_service._dao.existe_rfc.return_value = False
        tecnico_service._usuario_dao.insertar.return_value = 4
        tecnico_service._dao.insertar.return_value = True

        resultado = tecnico_service.alta_tecnico(
            **tecnico_activo_electricista_nivel2
        )

        assert resultado is True

    def test_no_permitir_especialidad_invalida(
        self,
        tecnico_service,
        tecnico_activo_electricista_nivel2
    ):
        tecnico_activo_electricista_nivel2["especialidad"] = "Robotico"

        with pytest.raises(ReglaNegocioError):
            tecnico_service.alta_tecnico(
                **tecnico_activo_electricista_nivel2
            )

    def test_no_permitir_nivel_certificacion_invalido(
        self,
        tecnico_service,
        tecnico_activo_electricista_nivel2
    ):
        tecnico_activo_electricista_nivel2["nivel_certificacion"] = "IV"

        with pytest.raises(ReglaNegocioError):
            tecnico_service.alta_tecnico(
                **tecnico_activo_electricista_nivel2
            )

    def test_no_permitir_estatus_invalido(
        self,
        tecnico_service,
        tecnico_activo_electricista_nivel2
    ):
        tecnico_activo_electricista_nivel2["estatus"] = "Fuera de servicio"

        with pytest.raises(ReglaNegocioError):
            tecnico_service.alta_tecnico(
                **tecnico_activo_electricista_nivel2
            )

    def test_no_permitir_id_tecnico_duplicado(
        self,
        tecnico_service,
        tecnico_activo_electricista_nivel2
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = 4

        with pytest.raises(EntidadDuplicadaError):
            tecnico_service.alta_tecnico(
                **tecnico_activo_electricista_nivel2
            )

    def test_no_permitir_rfc_duplicado(
        self,
        tecnico_service,
        tecnico_activo_electricista_nivel2
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = None
        tecnico_service._dao.existe_rfc.return_value = True

        with pytest.raises(EntidadDuplicadaError):
            tecnico_service.alta_tecnico(
                **tecnico_activo_electricista_nivel2
            )


class TestConsultarTecnico:

    def test_consultar_tecnico_existente(
        self,
        tecnico_service
    ):
        tecnico = {
            "id_tecnico_int": 1,
            "id_tecnico": "TEC001",
            "nombre_completo": "Juan Pérez"
        }

        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = 1
        tecnico_service._dao.buscar_por_id.return_value = tecnico

        resultado = tecnico_service.consultar_tecnico("TEC001")

        assert resultado == tecnico

    def test_consultar_tecnico_inexistente(
        self,
        tecnico_service
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            tecnico_service.consultar_tecnico("TEC999")


class TestModificarTecnico:

    def test_modificar_tecnico_existente(
        self,
        tecnico_service
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = 1
        tecnico_service._dao.buscar_por_id.return_value = {
            "id_tecnico_int": 1,
            "id_tecnico": "TEC001"
        }
        tecnico_service._dao.actualizar.return_value = True

        datos_actualizados = {
            "telefono": "9211111111"
        }

        resultado = tecnico_service.modificar_tecnico(
            "TEC001",
            datos_actualizados
        )

        assert resultado is True

        tecnico_service._dao.actualizar.assert_called_once_with(
            1,
            datos_actualizados
        )

    def test_no_modificar_tecnico_inexistente(
        self,
        tecnico_service
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            tecnico_service.modificar_tecnico(
                "TEC999",
                {"telefono": "1234567890"}
            )


class TestBajaTecnico:

    def test_no_dar_baja_tecnico_inexistente(
        self,
        tecnico_service
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            tecnico_service.baja_tecnico("TEC999")

    def test_no_dar_baja_tecnico_con_ordenes_activas(
        self,
        tecnico_service
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = 1
        tecnico_service._dao.buscar_por_id.return_value = {
            "id_tecnico_int": 1,
            "id_tecnico": "TEC001"
            }
        tecnico_service._dao.tiene_ordenes_activas.return_value = True

        with pytest.raises(IntegridadReferencialError):
            tecnico_service.baja_tecnico("TEC001")

    def test_dar_baja_tecnico_exitosamente(
        self,
        tecnico_service
    ):
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = 1
        tecnico_service._dao.buscar_por_id.return_value = {
            "id_tecnico_int": 1,
            "id_tecnico": "TEC001"
        }
        tecnico_service._dao.tiene_ordenes_activas.return_value = False
        tecnico_service._dao.actualizar.return_value = True

        resultado = tecnico_service.baja_tecnico("TEC001")

        assert resultado is True

        tecnico_service._dao.actualizar.assert_called_once_with(
            1,
            {"estatus": "Inactivo"}
        )