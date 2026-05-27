"""
RN-04: No se permite eliminar un Equipo o un Tecnico
        que tenga ordenes registradas.
"""

import pytest
from server.exceptions.exceptions import EntidadNoEncontradaError, IntegridadReferencialError


class TestRN04IntegridadReferencial:

    def test_baja_equipo_con_ordenes_lanza_excepcion(self, equipo_service):
        """
        DADO   un equipo que tiene ordenes de mantenimiento registradas
        CUANDO se intenta darlo de baja
        ENTONCES debe lanzar IntegridadReferencialError
        """
        equipo_service._dao.obtener_id_equipo_int.return_value = 1
        equipo_service._dao.tiene_ordenes_vinculadas.return_value = True

        with pytest.raises(IntegridadReferencialError):
            equipo_service.baja_equipo("EQ-001")

    def test_baja_equipo_sin_ordenes_es_exitosa(self, equipo_service):
        """
        DADO   un equipo sin ordenes registradas
        CUANDO se intenta darlo de baja
        ENTONCES debe retornar True sin lanzar excepcion
        """
        equipo_service._dao.obtener_id_equipo_int.return_value = 999
        equipo_service._dao.tiene_ordenes_vinculadas.return_value = False
        equipo_service._dao.eliminar.return_value = True

        resultado = equipo_service.baja_equipo("EQ-999")
        assert resultado is True

    def test_baja_tecnico_con_ordenes_activas_lanza_excepcion(self, tecnico_service):
        """
        DADO   un tecnico con ordenes en estados activos
        CUANDO se intenta darlo de baja
        ENTONCES debe lanzar IntegridadReferencialError
        """
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = 1
        tecnico_service._dao.buscar_por_id.return_value = {"id_tecnico_int": 1, "id_tecnico": "TEC-001"}
        tecnico_service._dao.tiene_ordenes_activas.return_value = True

        with pytest.raises(IntegridadReferencialError):
            tecnico_service.baja_tecnico("TEC-001")

    def test_baja_tecnico_sin_ordenes_activas_es_exitosa(self, tecnico_service):
        """
        DADO   un tecnico sin ordenes activas
        CUANDO se intenta darlo de baja
        ENTONCES debe retornar True sin lanzar excepcion
        """
        tecnico_service._usuario_dao.obtener_id_usuario_int.return_value = 999
        tecnico_service._dao.buscar_por_id.return_value = {"id_tecnico_int": 999, "id_tecnico": "TEC-999"}
        tecnico_service._dao.tiene_ordenes_activas.return_value = False
        tecnico_service._dao.actualizar.return_value = True

        resultado = tecnico_service.baja_tecnico("TEC-999")
        assert resultado is True

    def test_crear_orden_equipo_no_existente_es_invalido(self, orden_service):
        """
        DADO   un identificador de equipo que no existe en el sistema
        CUANDO el servicio intenta resolver su ID entero antes de la inserción
        ENTONCES debe cortar el flujo y lanzar EntidadNoEncontradaError
        """
        orden_service._equipo_dao.obtener_id_equipo_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.crear_orden(
                "OM-001",
                "EQ-001",
                "Preventivo",
                "2026-05-24",
                "Cambio de piezas",
                1000.0
            )

    def test_consultar_orden_no_existente_es_invalido(self, orden_service):
        """
        DADO   un identificador de orden que no existe en el sistema
        CUANDO el servicio intenta resolver su ID entero para buscarla
        ENTONCES debe lanzar EntidadNoEncontradaError
        """
        orden_service._dao.obtener_id_orden_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.consultar_orden("OM-001")

    def test_asignar_tecnico_orden_no_existente_es_invalido(self, orden_service):
        """
        DADO   una orden inexistente
        CUANDO se intenta invocar el proceso de asignación de personal
        ENTONCES el resolvedor inicial de la orden debe disparar EntidadNoEncontradaError
        """
        orden_service._dao.obtener_id_orden_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.asignar_tecnico("OM-001", "TEC-001")

    def test_asignar_tecnico_no_existente_es_invalido(self, orden_service):
        """
        DADO   una orden válida pero un identificador de técnico inexistente
        CUANDO el servicio intenta resolver la clave primaria del técnico
        ENTONCES debe lanzar EntidadNoEncontradaError
        """
        orden_service._dao.obtener_id_orden_int.return_value = 1
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 1,
            "id_orden": "OM-001",
            "id_equipo_int": 10
        }
        orden_service._tecnico_dao.obtener_id_tecnico_int.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.asignar_tecnico("OM-001", "TEC-001")

    def test_asignar_tecnico_equipo_vinculado_no_existente_es_invalido(
        self, orden_service, tecnico_activo_electricista_nivel2
    ):
        """
        DADO   una orden y un técnico existentes
        CUANDO la llave foránea id_equipo_int de la orden apunta a un registro huérfano o borrado
        ENTONCES la búsqueda individual del equipo debe lanzar EntidadNoEncontradaError
        """
        orden_service._dao.obtener_id_orden_int.return_value = 1
        orden_service._dao.buscar_por_id.return_value = {
            "id_orden_int": 1,
            "id_orden": "OM-001",
            "id_equipo_int": 10, 
        }

        orden_service._tecnico_dao.obtener_id_tecnico_int.return_value = 4
        orden_service._tecnico_dao.buscar_por_id.return_value = tecnico_activo_electricista_nivel2
        
        orden_service._equipo_dao.buscar_por_id.return_value = None

        with pytest.raises(EntidadNoEncontradaError):
            orden_service.asignar_tecnico("OM-001", "TEC-001")