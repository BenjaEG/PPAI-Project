from . import db
from datetime import datetime

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(20), default='auto_detectado')
    valorMagnitud = db.Column(db.Float, nullable=False)
    coordenadaEpicentro = db.Column(db.String(100), nullable=False)
    coordenadaHipocentro = db.Column(db.String(100), nullable=False)
    fechaHoraOcurrencia = db.Column(db.DateTime, default=datetime.utcnow)
    fechaHoraFin = db.Column(db.DateTime, default=datetime.utcnow)
    usuario_revision = db.Column(db.String(50))
    accion_revision = db.Column(db.String(20))
    fecha_revision = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "estado": self.estado,
            "valorMagnitud": self.valorMagnitud,
            "coordenadaEpicentro": self.coordenadaEpicentro,
            "coordenadaHipocentro": self.coordenadaHipocentro,
            "fechaHoraOcurrencia": self.fechaHoraOcurrencia.isoformat(),
            "fechaHoraFin": self.fechaHoraFin.isoformat(),
            "revision": {
                "usuario": self.usuario_revision,
                "accion": self.accion_revision,
                "fecha": self.fecha_revision.isoformat() if self.fecha_revision else None
            }
        }