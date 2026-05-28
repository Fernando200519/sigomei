from server.dao.db_connection import get_connection
import psycopg2 

class TecnicoDAO:

    def insertar(self, datos: dict) -> bool:
        sql = """
            INSERT INTO tecnicos
                (id_tecnico_int, id_tecnico, especialidad,
                 nivel_certificacion, fecha_ingreso)
            VALUES
                (%(id_tecnico_int)s, %(id_tecnico)s, %(especialidad)s,
                 %(nivel_certificacion)s, %(fecha_ingreso)s)
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, datos)
        return True
    
    def obtener_id_tecnico_int(self, id_tecnico: str) -> int | None:
        """Obtiene el ID interno (entero) a partir del ID de negocio (varchar)."""
        sql = "SELECT id_tecnico_int FROM tecnicos WHERE id_tecnico = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico,))
                row = cur.fetchone()
        return dict(row)['id_tecnico_int'] if row else None
    
    def buscar_por_id(self, id_tecnico_int: int) -> dict | None:
        """Busca un técnico por su ID interno e incluye todos sus datos de usuario de forma íntegra."""
        sql = """
            SELECT t.*, 
                   u.nombre_completo, 
                   u.rfc, 
                   u.telefono, 
                   u.correo, 
                   u.estado AS estatus
            FROM tecnicos t
            JOIN usuarios u ON t.id_tecnico_int = u.id_usuario_int
            WHERE t.id_tecnico_int = %s
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico_int,))
                row = cur.fetchone()
        return dict(row) if row else None

    def actualizar(self, id_tecnico_int: int, datos: dict) -> bool:
        if not datos:
            return False

        columnas_tecnicos = {"id_tecnico", "especialidad", "nivel_certificacion", "fecha_ingreso"}
        columnas_usuarios = {"id_usuario", "nombre_completo", "rfc", "telefono", "correo", "estado", "estatus"}

        datos_tecnicos = {}
        datos_usuarios = {}

        for k, v in datos.items():
            if k in columnas_tecnicos:
                datos_tecnicos[k] = v
            elif k in columnas_usuarios:
                clave_db = "estado" if k == "estatus" else k
                datos_usuarios[clave_db] = v

        if not datos_tecnicos and not datos_usuarios:
            return False

        with get_connection() as conn:
            with conn.cursor() as cur:
                
                if datos_tecnicos:
                    campos_tec = ", ".join(f"{k} = %({k})s" for k in datos_tecnicos)
                    sql_tec = f"UPDATE tecnicos SET {campos_tec} WHERE id_tecnico_int = %(id_tecnico_int)s"
                    datos_tecnicos["id_tecnico_int"] = id_tecnico_int
                    cur.execute(sql_tec, datos_tecnicos)

                if datos_usuarios:
                    campos_usr = ", ".join(f"{k} = %({k})s" for k in datos_usuarios)
                    sql_usr = f"UPDATE usuarios SET {campos_usr} WHERE id_usuario_int = %(id_usuario_int)s"
                    datos_usuarios["id_usuario_int"] = id_tecnico_int
                    cur.execute(sql_usr, datos_usuarios)

        return True

    def eliminar(self, id_tecnico_int: int) -> bool:
        sql = "DELETE FROM tecnicos WHERE id_tecnico_int = %s"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico_int,))
        return True

    def tiene_ordenes_activas(self, id_tecnico_int: int) -> bool:
        """Valida si el técnico tiene órdenes activas buscando en el historial de estados."""
        sql = """
            SELECT 1 
            FROM ordenes_mantenimiento o
            JOIN historial_estados_orden heo 
                ON o.id_orden_int = heo.id_orden_int AND heo.fecha_hora_fin IS NULL
            JOIN estados_orden eo 
                ON heo.id_estado_orden = eo.id_estado_orden
            WHERE o.id_tecnico_int = %s
            AND eo.nombre NOT IN ('Finalizada', 'Cancelada')
            LIMIT 1
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico_int,))
                return cur.fetchone() is not None
    
    def tiene_ordenes(self, id_tecnico_int: int) -> bool:
        """Valida si el técnico tiene cualquier orden registrada en el sistema (activas o históricas)."""
        sql = "SELECT 1 FROM ordenes_mantenimiento WHERE id_tecnico_int = %s LIMIT 1"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (id_tecnico_int,))
                return cur.fetchone() is not None
            
    def existe_rfc(self, rfc: str) -> bool:
        sql = "SELECT 1 FROM usuarios WHERE rfc = %s LIMIT 1"
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, (rfc,))
                return cur.fetchone() is not None
    
    def listar_todos(self) -> list:
        """Consulta la base de datos y devuelve solo los técnicos que permanezcan activos."""
        sql = """
            SELECT t.id_tecnico_int, t.id_tecnico, u.nombre_completo, 
                   t.especialidad, t.nivel_certificacion, u.estado AS estatus 
            FROM tecnicos t
            JOIN usuarios u ON t.id_tecnico_int = u.id_usuario_int
            WHERE u.estado = 'Activo';
        """
        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql)
                registros = cur.fetchall()
                return [dict(fila) for fila in registros]
                
    def listar_tecnicos_por_filtro(self, filtros: dict) -> list:
        """Consulta técnicos aplicando filtros opcionales mapeados correctamente a sus tablas."""
        # Mapeo explícito para evitar ambigüedad de columnas en el WHERE
        mapeo_columnas = {
            "especialidad": "t.especialidad = %(especialidad)s",
            "nivel_certificacion": "t.nivel_certificacion = %(nivel_certificacion)s",
            "estatus": "u.estado = %(estatus)s"
        }
        
        # CORRECCIÓN CRÍTICA: La consulta ahora exige por defecto que el usuario esté 'Activo'
        # para que los técnicos dados de baja lógica no reaparezcan al refrescar o filtrar.
        condiciones = ["u.estado = 'Activo'"]
        parametros = {}

        for campo, valor in filtros.items():
            # Si el usuario explícitamente busca por un estatus en el combo box, sobreescribimos la condición
            if campo == "estatus" and valor and valor != "Todos":
                condiciones[0] = "u.estado = %(estatus)s"
                parametros["estatus"] = valor
            elif campo in mapeo_columnas and valor:
                condiciones.append(mapeo_columnas[campo])
                parametros[campo] = valor

        sql = """
            SELECT t.id_tecnico_int, t.id_tecnico, u.nombre_completo, 
                   t.especialidad, t.nivel_certificacion, u.estado AS estatus
            FROM tecnicos t
            JOIN usuarios u ON t.id_tecnico_int = u.id_usuario_int
        """

        # Como condiciones ya tiene al menos ["u.estado = 'Activo'"], siempre se agregará el WHERE
        sql += " WHERE " + " AND ".join(condiciones)
        sql += " ORDER BY u.nombre_completo ASC;"

        with get_connection() as conn:
            with conn.cursor() as cur:
                cur.execute(sql, parametros)
                registros = cur.fetchall()
                return [dict(fila) for fila in registros]