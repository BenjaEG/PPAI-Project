import time
from datetime import datetime, timedelta
from app.models import Evento, CambioEstado
from app import db

def liberar_eventos_ocupados():
    while True:
        ahora = datetime.now()
        cinco_minutos_atras = ahora - timedelta(minutes=5)
        eventos_bloqueados = Evento.query.filter_by(estado_id=4).all()
        for evento in eventos_bloqueados:
            cambio = CambioEstado.query.filter_by(id=evento.cambio_estado_id).first()
            if cambio and cambio.fechaHoraInicio <= cinco_minutos_atras:
                nuevo_cambio = CambioEstado(
                    fechaHoraInicio=ahora,
                    estado_id=2
                )
                db.session.add(nuevo_cambio)
                db.session.commit()
                evento.estado_id = 2
                evento.cambio_estado_id = nuevo_cambio.id
                db.session.commit()
                print(f"Evento {evento.id} liberado a Pendiente Revision.")
        time.sleep(60)