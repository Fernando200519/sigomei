import os
from pathlib import Path

import psycopg2
from psycopg2.extras import RealDictCursor
from dotenv import load_dotenv

_ENV_PATH = Path(__file__).resolve().parents[2] / ".env"
load_dotenv(dotenv_path=_ENV_PATH)

def _get_config() -> dict:
    required = ("DB_HOST", "DB_PORT", "DB_NAME", "DB_USER", "DB_PASSWORD")
    missing = [v for v in required if not os.getenv(v)]
    if missing:
        raise EnvironmentError(
            f"Faltan variables de entorno: {', '.join(missing)}\n"
            f"Ruta buscada: {_ENV_PATH}\n"
            "Asegúrate de tener el archivo .env en la raíz del proyecto."
        )
    return {
        "host":     os.getenv("DB_HOST"),
        "port":     int(os.getenv("DB_PORT")),
        "dbname":   os.getenv("DB_NAME"),
        "user":     os.getenv("DB_USER"),
        "password": os.getenv("DB_PASSWORD"),
        "options":  "-c client_encoding=UTF8",
    }

def get_connection():
    try:
        return psycopg2.connect(**_get_config(), cursor_factory=RealDictCursor)
    except psycopg2.OperationalError as e:
        raise ConnectionError(f"No se pudo conectar a PostgreSQL: {e}") from None