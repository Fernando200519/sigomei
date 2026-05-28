import pytest
from server.exceptions.exceptions import EntidadDuplicadaError

EQUIPO_BASE = {
    "id_equipo":         "EQ-009",
    "nombre":            "Bomba-01",
    "tipo":              "Mecanico",
    "marca":             "Grundfos",
    "modelo":            "CM5-5",
    "numero_serie":      "NS-001",
    "ubicacion_planta":  "Planta A",
    "fecha_instalacion": "2023-01-15",
    "estado_operativo":  "Operativo",
    "criticidad":        "Media",
}

class TestTC_SIS_14_Equipos:
    """
    TC-SIS-14: Registrar nuevo equipo con numero de serie duplicado.
    RF asociado: RF-13, RN-18
    """

    def test_sis_alta_equipo_numero_serie_duplicado(self, rmi_registry, db_test):
        """
        DADO un equipo ya registrado con numero de serie NS-001
        CUANDO se intenta registrar otro equipo con el mismo numero de serie
        ENTONCES el sistema rechaza el registro y lanza EntidadDuplicadaError.
        """
        token = rmi_registry.login("carlos.ruiz@empresa.mx", "Test1234")

        rmi_registry.alta_equipo(token, **EQUIPO_BASE)

        with pytest.raises(EntidadDuplicadaError):
            rmi_registry.alta_equipo(
                token,
                id_equipo         = "EQ-010",   
                nombre            = "Bomba-02",  
                tipo              = "Mecanico",
                marca             = "Grundfos",
                modelo            = "CM5-5",
                numero_serie      = "NS-001",    # duplicado
                ubicacion_planta  = "Planta B",
                fecha_instalacion = "2024-03-01",
                estado_operativo  = "Operativo",
                criticidad        = "Baja",
            )

