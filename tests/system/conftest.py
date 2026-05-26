import pytest
import subprocess
import time
import socket
import Pyro5
from Pyro5.api import Proxy
from server.dao.db_connection import get_connection
import sys

from Pyro5.api import register_dict_to_class
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    IntegridadReferencialError,
    EstadoInvalidoError,
    AutenticacionError,
)

# El cliente necesita el mismo mapeo que el servidor para deserializar
_EXCEPCIONES_SIGOMEI = {
    "server.exceptions.exceptions.EntidadDuplicadaError":      EntidadDuplicadaError,
    "server.exceptions.exceptions.EntidadNoEncontradaError":   EntidadNoEncontradaError,
    "server.exceptions.exceptions.ReglaNegocioError":          ReglaNegocioError,
    "server.exceptions.exceptions.IntegridadReferencialError": IntegridadReferencialError,
    "server.exceptions.exceptions.EstadoInvalidoError":        EstadoInvalidoError,
    "server.exceptions.exceptions.AutenticacionError":         AutenticacionError,
}

def _hacer_reconstructor(cls):
    def reconstructor(classname, d):
        return cls()
    return reconstructor

for _nombre, _cls in _EXCEPCIONES_SIGOMEI.items():
    register_dict_to_class(_nombre, _hacer_reconstructor(_cls))

def _esperar_puerto(host: str, puerto: int, timeout: float = 5.0):
    """Bloquea la ejecución hasta que el servidor RMI esté escuchando en el puerto."""
    tiempo_inicio = time.time()
    while True:
        try:
            with socket.create_connection((host, puerto), timeout=0.5):
                return True
        except (ConnectionRefusedError, socket.timeout):
            if time.time() - tiempo_inicio > timeout:
                raise RuntimeError(
                    f"El servidor SIGOMEI no levantó en el puerto {puerto} a tiempo."
                )
            time.sleep(0.5)


@pytest.fixture(scope="session", autouse=True)
def gestionar_servidor_sigomei():
    """
    DADO que se van a ejecutar las pruebas de sistema,
    CUANDO pytest inicia la sesión, levanta automáticamente el servidor.
    ENTONCES ejecuta los tests y al finalizar apaga el servidor por completo.
    """
    print("\n[INFO] Levantando el servidor SIGOMEI para pruebas de sistema...")

    comando = [sys.executable, 
               "-m", 
               "coverage",
               "run",
               "--parallel-mode",
               "-m",
               "server.main_server"]

    proceso_servidor = subprocess.Popen(
        comando,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )

    try:
        _esperar_puerto("localhost", 9090, timeout=7.0)
        print("[INFO] ¡Servidor SIGOMEI online y listo!")
    except RuntimeError:
        # Leer stderr para exponer la causa real del fallo
        stderr_output = proceso_servidor.stderr.read() if proceso_servidor.stderr else "sin salida"
        proceso_servidor.kill()
        raise RuntimeError(
            f"El servidor SIGOMEI no levantó en el puerto 9090.\n"
            f"--- STDERR del servidor ---\n{stderr_output}"
        )

    yield proceso_servidor

    # TEARDOWN
    print("\n[INFO] Apagando el servidor SIGOMEI...")
    proceso_servidor.terminate()

    try:
        proceso_servidor.wait(timeout=3.0)
    except subprocess.TimeoutExpired:
        print("[WARN] El servidor tardó demasiado en cerrar, forzando kill...")
        proceso_servidor.kill()

    print("[INFO] Servidor SIGOMEI cerrado limpiamente.")


@pytest.fixture(scope="session")
def rmi_registry():
    """Conexión base al servidor/registro RMI de SIGOMEI."""
    uri = "PYRO:sigomei.controller@localhost:9090"
    with Proxy(uri) as proxy:  # ← Proxy importado desde Pyro5.api
        yield proxy

@pytest.fixture(scope="function")
def db_test():
    """Limpia las tablas antes de cada test para garantizar un ambiente aislado."""
    with get_connection() as connection:
        with connection.cursor() as cursor:
            # El orden importa: primero las tablas con FK hacia otras
            cursor.execute("DELETE FROM ordenes_mantenimiento")
            cursor.execute("DELETE FROM tecnicos")
            cursor.execute("DELETE FROM equipos")
        connection.commit()
    # yield sin valor: el test no necesita la conexión, solo la limpieza
    yield