from datetime import datetime
from app.models import Evento, Estado, db

class GestorRevisionEventos:
    def __init__(self):
        pass

    def buscarEventosSismicos(self, estado_nombre=None):
        eventos = Evento.query.order_by(Evento.fechaHoraOcurrencia.desc()).all()
        if estado_nombre is not None:
            if estado_nombre.strip().lower() == "pendiente revision":
                return [evento.getDatos() for evento in eventos if evento.esPendienteDeRevision()]
            elif estado_nombre.strip().lower() == "auto detectado":
                return [evento.getDatos() for evento in eventos if evento.esAutoDetectado()]
            else:
                return []
        return [evento.getDatos() for evento in eventos]
    
    def buscarEstadoRechazado(self, evento_id):
        evento = Evento.query.get(evento_id)
        if not evento:
            return None
        evento.rechazar()
        db.session.commit()
        return evento

    def buscarEstadoBloqueado(self, evento_id):
        evento = Evento.query.get(evento_id)
        if not evento:
            return None
        evento.bloquear()
        db.session.commit()
        return evento

    def buscarDatosSismicos(self, evento_id):
        evento = Evento.query.get(evento_id)
        if not evento:
            return None
        datos = evento.getDatos()
        datos["alcance"] = evento.getAlcance()
        datos["origen_de_generacion"] = evento.getOrigenDeGeneracion()
        datos["clasificacion_sismo"] = evento.clasificacionSismo()
        datos["series_temporales"] = evento.buscarDatosSeriesTemporales()
        return datos
    
    def clasificarPorEstacion(self):
        pass

    def llamarCUGenerarSismoGrama(self):
        pass

    def validarRequisitos(self):
        pass

    def finCU(self):
        pass