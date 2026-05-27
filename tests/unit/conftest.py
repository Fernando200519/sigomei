import pytest
from unittest.mock import MagicMock
from server.service.orden_service import OrdenService
from server.service.equipo_service import EquipoService
from server.service.tecnico_service import TecnicoService

@pytest.fixture
def orden_service():
    svc = OrdenService()
    svc._dao = MagicMock()
    svc._equipo_dao = MagicMock()
    svc._tecnico_dao = MagicMock()
    return svc


@pytest.fixture
def equipo_service():
    svc = EquipoService()
    svc._dao = MagicMock()
    return svc


@pytest.fixture
def tecnico_service():
    svc = TecnicoService()
    svc._dao = MagicMock()
    svc._usuario_dao = MagicMock()
    return svc

