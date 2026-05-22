import os
import logging
from pathlib import Path
from datetime import datetime

import Pyro5.server
from dotenv import load_dotenv

_ROOT = Path(__file__).resolve().parents[1]
load_dotenv(dotenv_path=_ROOT / ".env")

HOST      = os.getenv("SERVER_HOST")
PORT      = int(os.getenv("SERVER_PORT"))
OBJECT_ID = "sigomei.controller"

_LOGS_DIR = _ROOT / "logs"
_LOGS_DIR.mkdir(exist_ok=True)

_log_filename = _LOGS_DIR / f"sigomei_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(name)s — %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
    handlers=[
        logging.FileHandler(_log_filename, encoding="utf-8"),
        logging.StreamHandler(),
    ],
)

log = logging.getLogger("sigomei.server")

from server.controller.isigomei_controller import ISigomeiController   # noqa: E402


def main():
    log.info("Iniciando servidor SIGOMEI…")
    log.info("Archivo de bitácora: %s", _log_filename)

    daemon = Pyro5.server.Daemon(host=HOST, port=PORT)

    controller = ISigomeiController()
    uri = daemon.register(controller, objectId=OBJECT_ID)

    log.info("Controlador registrado → %s", uri)
    log.info("Esperando peticiones en %s:%s …", HOST, PORT)

    try:
        daemon.requestLoop()
    except KeyboardInterrupt:
        log.info("Servidor detenido por el usuario.")
    finally:
        daemon.close()
        log.info("Daemon cerrado. Hasta luego.")


if __name__ == "__main__":
    main()