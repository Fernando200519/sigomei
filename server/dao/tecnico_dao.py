class TecnicoDAO:
    def insertar(self, datos_tecnico): raise NotImplementedError
    def buscar_por_id(self, id_tecnico): raise NotImplementedError
    def actualizar(self, id_tecnico, datos_actualizados): raise NotImplementedError
    def eliminar(self, id_tecnico): raise NotImplementedError
    def tiene_ordenes_activas(self, id_tecnico): raise NotImplementedError
    def existe_rfc(self, rfc): raise NotImplementedError