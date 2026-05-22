# SIGOMEI — Sistema Distribuido para la Gestión de Órdenes de Mantenimiento de Equipos Industriales

## Requisitos previos

Antes de comenzar, asegúrate de tener instalado lo siguiente en tu equipo:

| Herramienta    | Versión mínima  |
| -------------- | --------------- |
| **Python**     | 3.11 o superior |
| **PostgreSQL** | 14 o superior   |
| **pip**        | 23 o superior   |

---

## 1. Clonar el repositorio y preparar el entorno

Clona el proyecto (o descomprime el archivo .zip) y navega a la raíz del directorio:

```bash
git clone https://github.com/Fernando200519/sigomei.git
cd sigomei
```

### Crear y activar el entorno virtual

```bash
# Crear el entorno virtual
python -m venv .venv

# Activar en Windows (PowerShell)
.venv\Scripts\Activate.ps1

# Activar en macOS / Linux
source .venv/bin/activate
```

_Sabrás que está activo porque verás el prefijo (.venv) en tu terminal._

### Instalar dependencias

```bash
pip install -r requirements.txt
```

---

## 2. Configurar credenciales (Archivo .env)

El proyecto **nunca** guarda contraseñas embebidas en el código. Las credenciales de red y base de datos se manejan mediante un archivo externo.

Crea tu archivo de configuración a partir de la plantilla:

```bash
cp .env.example .env
```

Abre el archivo `.env` recién creado en tu editor y configura tus datos reales:

```ini
DB_HOST=localhost
DB_PORT=5432
DB_NAME=sigomei_db
DB_USER=postgres
DB_PASSWORD=tu_contraseña_real

SERVER_HOST=localhost
SERVER_PORT=9090
SERVER_OBJECT_ID=sigomei.controller
```

> ⚠️ **Nota de seguridad:** El archivo `.env` está incluido en el `.gitignore` por lo que jamás se subirá al repositorio remoto.

---

## 3. Configurar la base de datos PostgreSQL

Asegúrate de que tu servicio de PostgreSQL esté corriendo y ejecuta los siguientes comandos en tu terminal para preparar el esquema y los datos iniciales:

### 3.1 Crear la base de datos

```bash
psql -U postgres -c "CREATE DATABASE sigomei_db;"
```

### 3.2 Crear las tablas (Esquema)

```bash
psql -U postgres -d sigomei_db -f database/schema.sql
```

### 3.3 Cargar datos de prueba iniciales (Seeding)

```bash
psql -U postgres -d sigomei_db -f database/seed.sql
```

### 3.4 Verificar la carga

```bash
psql -U postgres -d sigomei_db -c "SELECT * FROM equipos;"
```

_Si todo salió bien, la consola te mostrará una tabla con los 6 equipos de prueba iniciales._

---

## 4. Ejecutar la suite de pruebas (Ciclo TDD en VERDE)

Con el entorno virtual activo y desde la raíz del proyecto, ejecuta pytest. Como la lógica ya ha sido implementada, **todas las pruebas deben pasar exitosamente**.

```bash
pytest tests/ -v
```

> 💡 **Nota:** Las pruebas unitarias de los servicios utilizan _mocks_ (simuladores), lo que significa que puedes ejecutarlas y pasarán a verde incluso si el servidor o la base de datos están completamente apagados.

Salida esperada al final de la consola:

```text
============================== 26 passed in 0.xx s ==============================
```

---

## 5. Arrancar el servidor

Para encender el motor del sistema y exponer los objetos remotos a la red, ejecuta:

```bash
python -m server.main_server
```

**Salida esperada en consola:**

```text
2026-05-22 10:00:00  INFO      sigomei.server — Iniciando servidor SIGOMEI…
2026-05-22 10:00:00  INFO      sigomei.server — Archivo de bitácora: logs/sigomei_20260522_100000.log
2026-05-22 10:00:00  INFO      sigomei.server — Controlador registrado → PYRO:sigomei.controller@localhost:9090
2026-05-22 10:00:00  INFO      sigomei.server — Esperando peticiones en localhost:9090 …
```

- El servidor se quedará escuchando de forma indefinida. Generará un archivo log en tiempo real dentro de la carpeta `/logs`.
- Para detener el servidor de forma segura, presiona `Ctrl + C`.

---

## 6. Arrancar el cliente (Interfaz Gráfica PyQt6)

Abre una **nueva ventana de la terminal**, navega a la carpeta del proyecto, activa el entorno virtual (`.venv`) y arranca la interfaz:

```bash
python -m client.gui.main_window
```

> ⚠️ **Regla de arquitectura obligatoria:** El cliente se comunica exclusivamente con el servidor a través de la red usando el objeto Proxy en el puerto 9090. El cliente no tiene credenciales de la base de datos ni se conecta directamente a ella bajo ninguna circunstancia.

---

## 7. Estructura del proyecto

```
sigomei/
├── .env.example            # Plantilla de configuración (va al repositorio)
├── .env                    # Configuración con contraseñas reales (ignorado por git)
├── requirements.txt        # Lista de paquetes Python requeridos
├── database/
│   ├── schema.sql          # Script de creación de tablas DDL
│   └── seed.sql            # Script de inserción de registros de prueba
├── logs/                   # Archivos de bitácora generados por el servidor
├── server/
│   ├── main_server.py      # Punto de entrada ejecutable del servidor
│   ├── auth/               # Módulos de AuthManager y sesión
│   ├── controller/         # ISigomeiController (Fachada e interfaz remota de Pyro5)
│   ├── service/            # Capa de servicios (Donde residen las 8 reglas de negocio)
│   ├── dao/                # Capa de acceso a datos (Conexión a PostgreSQL vía psycopg2)
│   └── exceptions/         # Excepciones personalizadas del dominio
├── client/
│   ├── proxy/
│   │   └── sigomei_proxy.py # Stub intermedio que comunica al cliente con el servidor
│   └── gui/
│       └── main_window.py   # Punto de entrada de la interfaz gráfica en PyQt6
└── tests/
    └── services/            # Suite de 26 pruebas unitarias organizadas por regla (RN01..RN08)
```

---

## 8. Reglas de negocio implementadas

El servidor valida rigurosamente las siguientes directrices antes de alterar el estado del sistema:

| ID        | Regla de Negocio                                                                                            | Dónde se valida en el código                                    |
| --------- | ----------------------------------------------------------------------------------------------------------- | --------------------------------------------------------------- |
| **RN-01** | La especialidad del técnico asignado debe coincidir con el tipo del equipo.                                 | `OrdenService.asignar_tecnico()`                                |
| **RN-02** | Un equipo no puede tener más de una orden activa de forma simultánea en la misma fecha.                     | `OrdenService.crear_orden()`                                    |
| **RN-03** | Solo se puede asignar un técnico a una orden si su estatus está como 'Activo'.                              | `OrdenService.asignar_tecnico()`                                |
| **RN-04** | Integridad: No se puede dar de baja un equipo o técnico si cuenta con órdenes vigentes vinculadas.          | `EquipoService.baja_equipo()` / `TecnicoService.baja_tecnico()` |
| **RN-05** | Coherencia cronológica: La `fecha_programada` ≤ `fecha_inicio` ≤ `fecha_cierre`.                            | `OrdenService.iniciar_ejecucion()` / `finalizar_orden()`        |
| **RN-06** | Al cambiar al estado 'Finalizada', los campos `fecha_cierre` y `costo_real` pasan a ser obligatorios.       | `OrdenService.finalizar_orden()`                                |
| **RN-07** | Los equipos con nivel de criticidad Alta exigen un técnico con certificación nivel II o III.                | `OrdenService.asignar_tecnico()`                                |
| **RN-08** | El ciclo de vida de la orden solo admite transiciones válidas (ej. Programada → En ejecución → Finalizada). | `OrdenService._validar_transicion()`                            |
