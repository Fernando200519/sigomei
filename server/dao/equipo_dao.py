class EquipoDAO:
    def insertar(self, datos_equipo): raise NotImplementedError
    def buscar_por_id(self, id_equipo): raise NotImplementedError
    def actualizar(self, id_equipo, datos_actualizados): raise NotImplementedError
    def eliminar(self, id_equipo): raise NotImplementedError
    def tiene_ordenes_vinculadas(self, id_equipo): raise NotImplementedError