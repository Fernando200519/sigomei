from client.proxy.sigomei_proxy import SigomeiProxy


def titulo(texto):
    linea = "═" * 60
    print(f"\n{linea}\n  {texto}\n{linea}")

def ok(msg):    print(f"  ✅  {msg}")
def fallo(msg): print(f"  ❌  {msg}")
def info(msg):  print(f"  ℹ   {msg}")
def pausa():    input("\n  [Enter para continuar…]\n")

def _msg(exc):
    texto = str(exc)
    for prefijo in ("ReglaNegocioError:", "EstadoInvalidoError:",
                    "EntidadDuplicadaError:", "EntidadNoEncontradaError:",
                    "IntegridadReferencialError:"):
        if prefijo in texto:
            return texto.split(prefijo, 1)[1].strip()
    if ":" in texto:
        return texto.split(":", 1)[1].strip()
    return texto


def main():
    proxy = SigomeiProxy()

    # CRUD Equipos
    titulo("BLOQUE 1 · CRUD Equipos  (comunicacion remota via Pyro5)")

    info("Creando equipo EQ-100…")
    try:
        proxy.alta_equipo(
            "EQ-100", "Motor Electrico Demo", "Electrico",
            "Siemens", "1LE1", "SN-DEMO-100", "Nave Demo",
            "2024-01-10", "Operativo", "Alta",
        )
        ok("alta_equipo('EQ-100') → OK")
    except Exception as e:
        fallo(f"alta_equipo: {_msg(e)}")

    pausa()

    info("Consultando equipo EQ-100…")
    try:
        eq = proxy.consultar_equipo("EQ-100")
        ok(f"consultar_equipo → {eq['nombre']} | tipo={eq['tipo']} | criticidad={eq['criticidad']}")
    except Exception as e:
        fallo(f"consultar_equipo: {_msg(e)}")

    pausa()

    info("Modificando EQ-100 → estado_operativo='En Mantenimiento'…")
    try:
        proxy.modificar_equipo("EQ-100", {"estado_operativo": "En Mantenimiento"})
        ok("modificar_equipo('EQ-100') → OK")
        eq = proxy.consultar_equipo("EQ-100")
        info(f"Estado actualizado: {eq['estado_operativo']}")
    except Exception as e:
        fallo(f"modificar_equipo: {_msg(e)}")

    pausa()

    #  CRUD Tecnicos
    titulo("BLOQUE 2 · CRUD Tecnicos")

    info("Creando TEC-100 (Electrico, nivel I) — se usara para demostrar RN-07…")
    try:
        proxy.alta_tecnico(
            "TEC-100", "Demo Tecnico Uno", "DEMO800101XYZ",
            "9990000001", "demo1@sigomei.mx",
            "Electrico", "I", "2024-03-01", "Activo",
        )
        ok("alta_tecnico('TEC-100') nivel I → OK")
    except Exception as e:
        fallo(f"alta_tecnico TEC-100: {_msg(e)}")

    info("Creando TEC-101 (Electrico, nivel II) — se usara para el exito final…")
    try:
        proxy.alta_tecnico(
            "TEC-101", "Demo Tecnico Dos", "DEMO900202XYZ",
            "9990000002", "demo2@sigomei.mx",
            "Electrico", "II", "2023-06-15", "Activo",
        )
        ok("alta_tecnico('TEC-101') nivel II → OK")
    except Exception as e:
        fallo(f"alta_tecnico TEC-101: {_msg(e)}")

    pausa()

    info("Consultando tecnico TEC-101…")
    try:
        tec = proxy.consultar_tecnico("TEC-101")
        ok(f"consultar_tecnico → {tec['nombre_completo']} | "
           f"{tec['especialidad']} nivel {tec['nivel_certificacion']}")
    except Exception as e:
        fallo(f"consultar_tecnico: {_msg(e)}")

    pausa()

    info("Modificando TEC-101 → correo actualizado…")
    try:
        proxy.modificar_tecnico("TEC-101", {"correo": "demo2_nuevo@sigomei.mx"})
        ok("modificar_tecnico('TEC-101') → OK")
    except Exception as e:
        fallo(f"modificar_tecnico: {_msg(e)}")

    pausa()

    #  CRUD ordenes
    titulo("BLOQUE 3 · CRUD ordenes de Mantenimiento")

    info("Creando orden OM-100 para EQ-100 (Electrico, criticidad Alta)…")
    try:
        proxy.crear_orden(
            "OM-100", "EQ-100", "Preventivo",
            "2026-06-01", "Revision general del motor de demostracion", 3500.0,
        )
        ok("crear_orden('OM-100') → OK  |  estado: Programada")
    except Exception as e:
        fallo(f"crear_orden: {_msg(e)}")

    pausa()

    info("Consultando orden OM-100…")
    try:
        om = proxy.consultar_orden("OM-100")
        ok(f"consultar_orden → equipo={om['id_equipo']} | "
           f"estado={om['estado_orden']} | costo_est={om['costo_estimado']}")
    except Exception as e:
        fallo(f"consultar_orden: {_msg(e)}")

    pausa()

    #  Reglas de Negocio
    titulo("BLOQUE 4 · Reglas de Negocio — el servidor como 'cerebro'")

    print("\n  ── Escenario RECHAZADO · RN-01: especialidad incorrecta ──")
    info("Asignando TEC-001 (especialidad Mecanico) a OM-100 (equipo Electrico)…")
    info("Debe ser RECHAZADO por RN-01")
    try:
        proxy.asignar_tecnico("OM-100", "TEC-001")
        fallo("Se asigno cuando NO debia ← ERROR en implementacion")
    except Exception as e:
        ok(f"Servidor rechazo → {_msg(e)}")

    pausa()

    print("\n  ── Escenario RECHAZADO · RN-07: nivel de certificacion insuficiente ──")
    info("Asignando TEC-100 (Electrico, nivel I) a OM-100 (criticidad Alta)…")
    info("Especialidad coincide PERO nivel I < II → debe ser RECHAZADO por RN-07")
    try:
        proxy.asignar_tecnico("OM-100", "TEC-100")
        fallo("Se asigno cuando NO debia ← ERROR en implementacion")
    except Exception as e:
        ok(f"Servidor rechazo → {_msg(e)}")

    pausa()

    print("\n  ── Escenario EXITOSO · RN-01 + RN-07 cumplidas ──")
    info("Asignando TEC-101 (Electrico, nivel II) a OM-100…")
    info("Especialidad coincide Y nivel II ≥ II → debe ser ACEPTADO")
    try:
        proxy.asignar_tecnico("OM-100", "TEC-101")
        ok("asignar_tecnico('OM-100', 'TEC-101') → ACEPTADO ✓")
    except Exception as e:
        fallo(f"No debio rechazarse: {_msg(e)}")

    pausa()

    #  Ciclo de vida de la Orden
    titulo("BLOQUE 5 · Ciclo de vida completo de la Orden")

    info("Iniciando ejecucion de OM-100 (fecha_inicio='2026-06-02')…")
    try:
        proxy.iniciar_ejecucion("OM-100", "2026-06-02")
        ok("iniciar_ejecucion → estado: En ejecucion")
    except Exception as e:
        fallo(f"iniciar_ejecucion: {_msg(e)}")

    info("Finalizando OM-100 (fecha_cierre='2026-06-05', costo_real=3200.0)…")
    try:
        proxy.finalizar_orden("OM-100", "2026-06-05", 3200.0)
        ok("finalizar_orden → estado: Finalizada")
        om = proxy.consultar_orden("OM-100")
        ok(f"Estado confirmado en BD: {om['estado_orden']} | costo_real={om['costo_real']}")
    except Exception as e:
        fallo(f"finalizar_orden: {_msg(e)}")

    pausa()

    #  DELETE
    titulo("BLOQUE 6 · DELETE — limpieza de datos de demo")

    info("Intentando eliminar EQ-100 (tiene ordenes vinculadas) → RECHAZADO (RN-04)…")
    try:
        proxy.baja_equipo("EQ-100")
        fallo("Se elimino cuando NO debia")
    except Exception as e:
        ok(f"RN-04 activo → {_msg(e)}")

    pausa()

    info("Eliminando TEC-100 (sin ordenes activas)…")
    try:
        proxy.baja_tecnico("TEC-100")
        ok("baja_tecnico('TEC-100') → OK")
    except Exception as e:
        fallo(f"baja_tecnico: {_msg(e)}")

    titulo("FIN DE LA DEMOSTRACIoN  —  revisa los logs del servidor")
    print()


if __name__ == "__main__":
    main()