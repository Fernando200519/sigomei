from werkzeug.security import (
    generate_password_hash
)

from server.dao.tecnico_dao import (
    TecnicoDAO
)
from server.dao.usuario_dao import (
    UsuarioDAO
)
from server.exceptions.exceptions import (
    EntidadDuplicadaError,
    EntidadNoEncontradaError,
    ReglaNegocioError,
    IntegridadReferencialError,
)

ESPECIALIDADES_VALIDAS = {
    "Electrico",
    "Mecanico",
    "Hidraulico",
    "Neumatico"
}

NIVELES_VALIDOS = {
    "I",
    "II",
    "III"
}

ESTATUS_VALIDOS = {
    "Activo",
    "Inactivo"
}


class TecnicoService:

    ID_ROL_TECNICO = 4

    def __init__(self):
        self._dao = TecnicoDAO()
        self._usuario_dao = UsuarioDAO()


    def _validar_datos_tecnico(
        self,
        especialidad: str,
        nivel_certificacion: str,
        estatus: str
    ):

        if (
            especialidad
            not in ESPECIALIDADES_VALIDAS
        ):
            raise ReglaNegocioError(
                f"Especialidad inválida: "
                f"'{especialidad}'"
            )

        if (
            nivel_certificacion
            not in NIVELES_VALIDOS
        ):
            raise ReglaNegocioError(
                f"Nivel de certificación inválido: "
                f"'{nivel_certificacion}'"
            )

        if (
            estatus
            not in ESTATUS_VALIDOS
        ):
            raise ReglaNegocioError(
                f"Estado inválido: "
                f"'{estatus}'"
            )

    def _obtener_id_tecnico_int(
        self,
        id_tecnico: str
    ) -> int:

        id_tecnico_int = (
            self._usuario_dao
            .obtener_id_usuario_int(
                id_tecnico
            )
        )

        if not id_tecnico_int:
            raise EntidadNoEncontradaError(
                f"Técnico "
                f"'{id_tecnico}' "
                f"no encontrado"
            )

        return id_tecnico_int

    def alta_tecnico(
        self,
        id_tecnico: str,
        nombre_completo: str,
        rfc: str,
        telefono: str,
        correo: str,
        especialidad: str,
        nivel_certificacion: str,
        fecha_ingreso: str,
        estatus: str,
    ) -> bool:

        self._validar_datos_tecnico(
            especialidad,
            nivel_certificacion,
            estatus
        )

        if (
            self._usuario_dao
            .obtener_id_usuario_int(
                id_tecnico
            )
        ):
            raise (
                EntidadDuplicadaError(
                    f"Ya existe un técnico "
                    f"con id "
                    f"'{id_tecnico}'"
                )
            )

        # Validar RFC duplicado
        if self._dao.existe_rfc(rfc):
            raise (
                EntidadDuplicadaError(
                    f"Ya existe un usuario "
                    f"con RFC "
                    f"'{rfc}'"
                )
            )

        if (
            self._usuario_dao
            .existe_correo(correo)
        ):
            raise (
                EntidadDuplicadaError(
                    f"Ya existe un usuario "
                    f"con correo "
                    f"'{correo}'"
                )
            )

        hash_temporal = (
            generate_password_hash(
                "temporal123"
            )
        )

        datos_usuario = {
            "id_usuario":
                id_tecnico,

            "nombre_completo":
                nombre_completo,

            "rfc":
                rfc,

            "telefono":
                telefono,

            "correo":
                correo,

            "estado":
                estatus,

            "hash_contrasena":
                hash_temporal,

            "id_rol":
                self.ID_ROL_TECNICO,
        }

        id_usuario_int = (
            self._usuario_dao
            .insertar(
                datos_usuario
            )
        )

        datos_tecnico = {
            "id_tecnico_int":
                id_usuario_int,

            "id_tecnico":
                id_tecnico,

            "especialidad":
                especialidad,

            "nivel_certificacion":
                nivel_certificacion,

            "fecha_ingreso":
                fecha_ingreso,
        }

        return self._dao.insertar(
            datos_tecnico
        )

    def consultar_tecnico(
        self,
        id_tecnico: str
    ) -> dict:

        id_tecnico_int = (
            self._obtener_id_tecnico_int(
                id_tecnico
            )
        )

        tecnico = (
            self._dao.buscar_por_id(
                id_tecnico_int
            )
        )

        if not tecnico:
            raise (
                EntidadNoEncontradaError(
                    f"Técnico "
                    f"'{id_tecnico}' "
                    f"no encontrado"
                )
            )

        return tecnico

    def modificar_tecnico(
        self,
        id_tecnico: str,
        datos_actualizados: dict
    ) -> bool:

        id_tecnico_int = (
            self._obtener_id_tecnico_int(
                id_tecnico
            )
        )

        tecnico = (
            self._dao.buscar_por_id(
                id_tecnico_int
            )
        )

        if not tecnico:
            raise (
                EntidadNoEncontradaError(
                    f"Técnico "
                    f"'{id_tecnico}' "
                    f"no encontrado"
                )
            )

        if (
            "especialidad"
            in datos_actualizados
        ):
            if (
                datos_actualizados[
                    "especialidad"
                ]
                not in
                ESPECIALIDADES_VALIDAS
            ):
                raise (
                    ReglaNegocioError(
                        "Especialidad inválida."
                    )
                )

        if (
            "nivel_certificacion"
            in datos_actualizados
        ):
            if (
                datos_actualizados[
                    "nivel_certificacion"
                ]
                not in
                NIVELES_VALIDOS
            ):
                raise (
                    ReglaNegocioError(
                        "Nivel de certificación inválido."
                    )
                )

        # Validar estatus
        if (
            "estatus"
            in datos_actualizados
        ):
            if (
                datos_actualizados[
                    "estatus"
                ]
                not in
                ESTATUS_VALIDOS
            ):
                raise (
                    ReglaNegocioError(
                        "Estado inválido."
                    )
                )

        return self._dao.actualizar(
            id_tecnico_int,
            datos_actualizados
        )

    def baja_tecnico(
        self,
        id_tecnico: str
    ) -> bool:

        id_tecnico_int = (
            self._obtener_id_tecnico_int(
                id_tecnico
            )
        )

        if self._dao.tiene_ordenes(
            id_tecnico_int
        ):
            raise (
                IntegridadReferencialError(
                    f"RN-04: "
                    f"El técnico "
                    f"'{id_tecnico}' "
                    f"tiene órdenes "
                    f"registradas."
                )
            )

        return self._dao.actualizar(
            id_tecnico_int,
            {
                "estatus":
                    "Inactivo"
            }
        )

    def listar_tecnicos(
        self
    ) -> list:

        return (
            self._dao
            .listar_todos()
        )

    def listar_tecnicos_por_filtro(
        self,
        filtros: dict
    ) -> list:

        return (
            self._dao
            .listar_tecnicos_por_filtro(
                filtros
            )
        )