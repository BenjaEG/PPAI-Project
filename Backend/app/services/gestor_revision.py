from datetime import datetime
from app.models import Evento, Estado, db

class GestorRevisionEventos:
    def __init__(self):
        pass

    def ordenarES(self, eventos):
        return sorted(eventos, key=lambda x: x.fechaHoraOcurrencia, reverse=True)

    def buscarEventosSismicos(self):
        eventos = Evento.query.all()
        eventos = [
            evento for evento in eventos
            if evento.esPendienteDeRevision() or evento.esAutoDetectado()
        ]
        eventos = self.ordenarES(eventos)
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