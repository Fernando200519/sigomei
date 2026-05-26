class TestTC_SIS_01_Autenticacion:
    """
    TC-SIS-01: Inicio de sesión exitoso con credenciales válidas.
    RF asociado: RF-02, RF-03, RN-10
    """

    def test_sis_inicio_sesion_exitoso_credenciales_validas(self, rmi_registry, db_test):
        """
        DADO un usuario activo con correo supervisor@sigomei.mx y contraseña Test1234
        CUANDO se invoca login con esas credenciales
        ENTONCES el sistema retorna un token de sesión (str no vacío)
        y la sesión queda activa.
        """
        token = rmi_registry.login("supervisor@sigomei.mx", "Test1234")

        assert isinstance(token, str), "El token debe ser una cadena de texto"
        assert len(token) > 0, "El token no debe estar vacío"

    
