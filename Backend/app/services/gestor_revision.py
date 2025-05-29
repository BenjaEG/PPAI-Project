from app.models import EventoSismico, db, Estado
from datetime import datetime

class GestorRevisionEventos:
    def __init__(self):
        self.usuario = None

    def tomarSeleccionES(self, evento_id):
        return self.buscarEstadoBloqueado(evento_id)

    def tomarOpcSolicitada(self, evento_id, opcion):
        if opcion == "rechazar":
            return self.buscarEstadoRechazado(evento_id)
        elif opcion == "confirmar":
            return self.buscarEstadoConfirmado(evento_id)
        elif opcion == "solicitar revision":
            return self.buscarEstadoSolicitadoRevision(evento_id)

    def buscarEmpleadoLogueado(self):
        usuario = Sesion().conocerEmpleado()
        return usuario

    def getFechaHora(self):
        return datetime.now()

    def bloquearES(self, evento_id, usuario, estado_bloqueado_id):
        evento = EventoSismico.query.get(evento_id)
        if not evento:
            return None
        fecha_hora = self.getFechaHora()
        evento.bloquear(usuario, fecha_hora, estado_bloqueado_id)
        db.session.commit()
        return evento

    def ordenarES(self, eventos):
        return sorted(eventos, key=lambda x: x.fechaHoraOcurrencia, reverse=True)

    def buscarEventosSismicos(self):
        eventos = EventoSismico.query.all()
        eventos = [
            evento for evento in eventos
            if evento.esPendienteDeRevision() or evento.esAutoDetectado()
        ]
        eventos = self.ordenarES(eventos)
        return [evento.getDatos() for evento in eventos]
    
    def buscarEstadoConfirmado(self, evento_id):
        usuario = self.usuario
        evento = EventoSismico.query.get(evento_id)
        errores = self.validarRequisitos(evento)
        if errores:
            return {"errores": errores}
        if not evento:
            return None
        estado_confirmado_id = None
        for estado in Estado.query.all():
            estado_confirmado_id = estado.esConfirmado()
            if estado_confirmado_id:
                break
        if not estado_confirmado_id:
            return {"errores": ["No se encontró el estado 'Confirmado'"]}
        fecha_hora = self.getFechaHora()
        evento.confirmar(usuario, fecha_hora, estado_confirmado_id)
        db.session.commit()
        return evento
    
    def buscarEstadoSolicitadoRevision(self, evento_id):
        usuario = self.usuario
        evento = EventoSismico.query.get(evento_id)
        errores = self.validarRequisitos(evento)
        if errores:
            return {"errores": errores}
        if not evento:
            return None
        estado_solicitado_revision_id = None
        for estado in Estado.query.all():
            estado_solicitado_revision_id = estado.esDerivado()
            if estado_solicitado_revision_id:
                break
        if not estado_solicitado_revision_id:
            return {"errores": ["No se encontró el estado 'Solicitado Revisión'"]}
        fecha_hora = self.getFechaHora()
        evento.solicitarRevision(usuario, fecha_hora, estado_solicitado_revision_id)
        db.session.commit()
        return evento
    
    def buscarEstadoRechazado(self, evento_id):
        usuario = self.usuario
        evento = EventoSismico.query.get(evento_id)
        errores = self.validarRequisitos(evento)
        if errores:
            return {"errores": errores}
        if not evento:
            return None
        estado_rechazado_id = None
        for estado in Estado.query.all():
            estado_rechazado_id = estado.esRechazado()
            if estado_rechazado_id:
                break
        if not estado_rechazado_id:
            return {"errores": ["No se encontró el estado 'Rechazado'"]}
        fecha_hora = self.getFechaHora()
        evento.rechazar(usuario, fecha_hora, estado_rechazado_id)
        db.session.commit()
        return evento

    def buscarEstadoBloqueado(self, evento_id):
        self.usuario = self.buscarEmpleadoLogueado()
        usuario = self.usuario
        estado_bloqueado_id = None
        for estado in Estado.query.all():
            estado_bloqueado_id = estado.esBloqueado()
            if estado_bloqueado_id:
                break
        if not estado_bloqueado_id:
            return None
        self.bloquearES(evento_id, usuario, estado_bloqueado_id)
        datos = self.buscarDatosSismicos(evento_id)
        return datos

    def buscarDatosSismicos(self, evento_id):
        evento = EventoSismico.query.get(evento_id)
        if not evento:
            return None
        datos = evento.getDatos()
        datos["alcance"] = evento.getAlcance()
        datos["origen_de_generacion"] = evento.getOrigenDeGeneracion()
        datos["clasificacion_sismo"] = evento.clasificacionSismo()
        datos["series_temporales"] = evento.buscarDatosSeriesTemporales()
        # Clasificar series por estación y reemplazar en el dict
        datos["series_temporales_por_estacion"] = self.clasificarPorEstacion(datos)
        self.llamarCUGenerarSismoGrama(datos)
        return datos

    def clasificarPorEstacion(self, datos):
        if not datos or "series_temporales" not in datos:
            return {}

        series_temporales = datos["series_temporales"]
        series_por_estacion = {}

        for serie in series_temporales:
            estacion_info = serie.get("datosSismografo", {}).get("estacion")
            if estacion_info:
                clave_estacion = f'{estacion_info.get("codigoEstacion", "-")} - {estacion_info.get("nombre", "-")}'
            else:
                clave_estacion = "Sin estación"

            if clave_estacion not in series_por_estacion:
                series_por_estacion[clave_estacion] = []

            # Recorrer muestras sísmicas de la serie
            muestras = serie.get("datosMuestrasSismicas", [])
            for muestra in muestras:
                instante = muestra.get("fechaHoraMuestra")
                detalles = muestra.get("detalles", [])
                valores = {
                    "instante": instante,
                    "velocidad_onda": None,
                    "frecuencia_onda": None,
                    "longitud": None
                }
                for detalle in detalles:
                    tipo = (detalle.get("tipoDeDato") or "").strip().lower()
                    valor = detalle.get("valor")
                    # Ajusta los nombres según tus tipos de dato reales
                    if "velocidad" in tipo or "km/seg" in tipo:
                        valores["velocidad_onda"] = valor
                    elif "frecuencia" in tipo or "hz" in tipo:
                        valores["frecuencia_onda"] = valor
                    elif "longitud" in tipo or "km/ciclo" in tipo:
                        valores["longitud"] = valor
                series_por_estacion[clave_estacion].append(valores)

        return series_por_estacion

    def llamarCUGenerarSismoGrama(self, datos):
        pass

    def validarRequisitos(self, evento):
        errores = []
        if evento is None:
            errores.append("El evento no existe.")
            return errores
        if evento.valorMagnitud is None:
            errores.append("El evento no tiene magnitud.")
        if not evento.alcance_id:
            errores.append("El evento no tiene alcance.")
        if not evento.origen_de_generacion_id:
            errores.append("El evento no tiene origen de generación.")
        return errores

    def finCU(self):
        pass

class Usuario:
    usuario_actual = None

    def __init__(self, nombre):
        self.nombre = nombre

    def getNombre(self):
        return self.nombre

    @classmethod
    def setUsuarioActual(cls, usuario):
        cls.usuario_actual = usuario

    @classmethod
    def conocerEmpleado(cls):
        if cls.usuario_actual:
            return cls.usuario_actual.getNombre()
        return None
    
class Sesion:
    def __init__(self):
        pass

    def conocerEmpleado(self):
        usuario = Usuario.conocerEmpleado()
        if not usuario:
            raise ValueError("No hay un usuario conectado.")
        return usuario