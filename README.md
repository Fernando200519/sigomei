# SIGOMEI — Sistema de Gestión de Órdenes de Mantenimiento de Equipos Industriales

## ¿Qué contiene este repositorio?

```
sigomei/
├── README.md
├── requirements.txt
├── server/
│   ├── auth/           ← AuthManager y SessionHandler
│   ├── controller/     ← ISigomeiController (fachada Pyro5)
│   ├── service/        ← EquipoService, TecnicoService, OrdenService
│   ├── dao/            ← EquipoDAO, TecnicoDAO, OrdenDAO
│   └── exceptions/     ← Excepciones personalizadas del dominio
├── client/
│   ├── proxy/          ← SigomeiProxy (stub del cliente)
│   └── gui/            ← MainWindow (PyQt6)
└── tests/
    ├── conftest.py
    └── services/       ← 8 archivos de prueba, uno por regla RN-01..RN-08
```

> **Estado actual:** todos los métodos del servidor lanzan `NotImplementedError`.
> Las 26 pruebas deben **fallar en rojo** — ese es el comportamiento esperado en esta entrega.

---

## Paso 1 — Clonar el repositorio

```bash
git clone https://github.com/Fernando200519/sigomei.git
cd sigomei
```

> Si recibió el proyecto como archivo `.zip`, descomprímalo y abra una terminal dentro de la carpeta resultante (`cd sigomei`).

---

## Paso 2 — Crear y activar un entorno virtual

Crear el entorno virtual dentro de la carpeta del proyecto:

```bash
python -m venv .venv
```

Activarlo según el sistema operativo:

```bash
# macOS / Linux
source .venv/bin/activate

# Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Windows (CMD)
.venv\Scripts\activate.bat
```

Debe aparecer el prefijo `(.venv)` al inicio de la línea de comandos.  
Para desactivar el entorno en cualquier momento: `deactivate`

---

## Paso 3 — Instalar las dependencias

```bash
pip install -r requirements.txt
```

El archivo instala exactamente cuatro paquetes principales:

| Paquete           | Para qué se usa                                                       |
| ----------------- | --------------------------------------------------------------------- |
| `Pyro5`           | Comunicación RMI entre cliente y servidor                             |
| `PyQt6`           | Interfaz gráfica (no se usa en las pruebas)                           |
| `psycopg2-binary` | Conector PostgreSQL (no se usa en las pruebas)                        |
| `pytest`          | Framework de pruebas unitarias ← **el más importante para esta fase** |

Verificar que pytest quedó instalado:

```bash
pytest --version
```

Salida esperada en consola: Algo como `pytest 8.x.x` o `pytest 9.x.x`.

---

## Paso 4 — Ejecutar la suite de pruebas (Fase ROJA)

Desde la raíz del proyecto (la carpeta que contiene `requirements.txt`):

```bash
pytest tests/ -v
```

La bandera `-v` (verbose) muestra el nombre de cada prueba junto a su resultado.

---

## Paso 5 — Interpretar la salida esperada

Al terminar, la consola debe mostrar **exactamente esto** al final:

```
============================== 26 failed in 0.xx s ==============================
```

Con el detalle de todos los tests en rojo:

```
FAILED tests/services/test_rn01_especialidad.py::...
FAILED tests/services/test_rn02_orden_activa_duplicada.py::...
FAILED tests/services/test_rn03_tecnico_inactivo.py::...
FAILED tests/services/test_rn04_integridad_referencial.py::...
FAILED tests/services/test_rn05_fechas_coherentes.py::...
FAILED tests/services/test_rn06_campos_estado_finalizada.py::...
FAILED tests/services/test_rn07_criticidad_alta.py::...
FAILED tests/services/test_rn08_transiciones_estado.py::...
```

Cada fallo termina con `NotImplementedError` — esto es **correcto y esperado**.  
No debe haber ningún `ERROR` de importación ni de sintaxis. Solo `FAILED`.

---

## Qué prueba cada archivo

| Archivo de prueba                       | Regla de negocio evaluada                                                                                          |
| --------------------------------------- | ------------------------------------------------------------------------------------------------------------------ |
| `test_rn01_especialidad.py`             | **RN-01** La especialidad del técnico debe coincidir con el tipo del equipo                                        |
| `test_rn02_orden_activa_duplicada.py`   | **RN-02** Un equipo no puede tener dos órdenes activas en la misma fecha                                           |
| `test_rn03_tecnico_inactivo.py`         | **RN-03** Un técnico inactivo no puede ser asignado a una orden                                                    |
| `test_rn04_integridad_referencial.py`   | **RN-04** No se permite eliminar equipos o técnicos con órdenes registradas                                        |
| `test_rn05_fechas_coherentes.py`        | **RN-05** fecha_cierre ≥ fecha_inicio ≥ fecha_programada                                                           |
| `test_rn06_campos_estado_finalizada.py` | **RN-06** Solo órdenes Finalizadas tienen costo_real y fecha_cierre                                                |
| `test_rn07_criticidad_alta.py`          | **RN-07** Equipos de criticidad Alta requieren técnico con certificación II o III                                  |
| `test_rn08_transiciones_estado.py`      | **RN-08** Transiciones válidas: Programada→En ejecución→Finalizada; Cancelada solo desde Programada o En ejecución |

---

## Comando rápido (todo en una línea)

Para ejecutar las pruebas con un resumen compacto sin el detalle de cada fallo:

```bash
pytest tests/ --tb=no -q
```

Salida esperada:

```
26 failed in 0.xx s
```
