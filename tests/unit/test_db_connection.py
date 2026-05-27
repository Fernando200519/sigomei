import pytest
from unittest.mock import patch

from psycopg2.extras import RealDictCursor

from server.dao.db_connection import (
    _get_config,
    get_connection,
)


class TestDBConnection:

    def test_get_config_retorna_configuracion_valida(self):
        env = {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
            "DB_NAME": "mantenimiento",
            "DB_USER": "postgres",
            "DB_PASSWORD": "1234",
        }

        with patch.dict("os.environ", env, clear=True):
            resultado = _get_config()

        assert resultado == {
            "host": "localhost",
            "port": 5432,
            "dbname": "mantenimiento",
            "user": "postgres",
            "password": "1234",
            "options": "-c client_encoding=UTF8",
        }

    def test_get_config_faltan_variables_lanza_excepcion(self):
        env = {
            "DB_HOST": "localhost",
            "DB_PORT": "5432",
        }

        with patch.dict("os.environ", env, clear=True):
            with pytest.raises(EnvironmentError):
                _get_config()

    def test_get_connection_llama_psycopg2_connect(self):
        config_mock = {
            "host": "localhost",
            "port": 5432,
            "dbname": "mantenimiento",
            "user": "postgres",
            "password": "1234",
            "options": "-c client_encoding=UTF8",
        }

        with patch(
            "server.dao.db_connection._get_config",
            return_value=config_mock
        ):
            with patch(
                "server.dao.db_connection.psycopg2.connect"
            ) as mock_connect:

                with get_connection():
                    pass

        mock_connect.assert_called_once_with(
            **config_mock,
            cursor_factory=RealDictCursor
        )