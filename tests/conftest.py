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
    return svc

@pytest.fixture
def equipo_electrico_alta():
    """Equipo de tipo Eléctrico con criticidad Alta."""
    return {
        "id_equipo": "EQ-001",
        "nombre": "Transformador T1",
        "tipo": "Eléctrico",
        "marca": "ABB",
        "modelo": "TX-500",
        "numero_serie": "SN-AAA-001",
        "ubicacion_planta": "Nave A",
        "fecha_instalacion": "2020-01-15",
        "estado_operativo": "Operativo",
        "criticidad": "Alta",
    }


@pytest.fixture
def equipo_mecanico_baja():
    """Equipo de tipo Mecánico con criticidad Baja."""
    return {
        "id_equipo": "EQ-002",
        "nombre": "Bomba B2",
        "tipo": "Mecánico",
        "marca": "Grundfos",
        "modelo": "CM5",
        "numero_serie": "SN-BBB-002",
        "ubicacion_planta": "Nave B",
        "fecha_instalacion": "2021-06-10",
        "estado_operativo": "Operativo",
        "criticidad": "Baja",
    }


@pytest.fixture
def tecnico_activo_electricista_nivel1():
    return {
        "id_tecnico": "TEC-001",
        "nombre_completo": "Carlos López",
        "rfc": "LOCA800101AAA",
        "telefono": "9211234567",
        "correo": "carlos@sigomei.mx",
        "especialidad": "Mecánico",
        "nivel_certificacion": "I",
        "fecha_ingreso": "2022-03-01",
        "estatus": "Activo",
    }


@pytest.fixture
def tecnico_activo_electricista_nivel2():
    return {
        "id_tecnico": "TEC-002",
        "nombre_completo": "Ana Pérez",
        "rfc": "PEAA900202BBB",
        "telefono": "9219876543",
        "correo": "ana@sigomei.mx",
        "especialidad": "Eléctrico",
        "nivel_certificacion": "II",
        "fecha_ingreso": "2021-07-15",
        "estatus": "Activo",
    }


@pytest.fixture
def tecnico_inactivo():
    return {
        "id_tecnico": "TEC-003",
        "nombre_completo": "Luis Ramos",
        "rfc": "RALU850303CCC",
        "telefono": "9215554433",
        "correo": "luis@sigomei.mx",
        "especialidad": "Eléctrico",
        "nivel_certificacion": "II",
        "fecha_ingreso": "2019-01-10",
        "estatus": "Inactivo",
    }