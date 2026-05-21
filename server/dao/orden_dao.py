class OrdenDAO:
    def insertar(self, datos_orden): raise NotImplementedError
    def buscar_por_id(self, id_orden): raise NotImplementedError
    def actualizar_estado(self, id_orden, nuevo_estado): raise NotImplementedError
    def asignar_tecnico(self, id_orden, id_tecnico): raise NotImplementedError
    def actualizar_cierre(self, id_orden, fecha_cierre, costo_real): raise NotImplementedError
    def listar_por_filtros(self, filtros): raise NotImplementedError
    def actualizar_inicio(self, id_orden, fecha_inicio): raise NotImplementedError