from . import db
from datetime import datetime

class Estado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    ambito = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "ambito": self.ambito
        }

class CambioEstado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fechaHoraInicio = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fechaHoraFin = db.Column(db.DateTime)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "fechaHoraInicio": self.fechaHoraInicio.isoformat(),
            "fechaHoraFin": self.fechaHoraFin.isoformat() if self.fechaHoraFin else None,
            "estado_id": self.estado_id
        }

class Alcance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }

class OrigenDeGeneracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }

class ClasificacionSismo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    kmProfundidadDesde = db.Column(db.Float, nullable=False)
    kmProfundidadHasta = db.Column(db.Float, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "kmProfundidadDesde": self.kmProfundidadDesde,
            "kmProfundidadHasta": self.kmProfundidadHasta
        }

class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    cambio_estado_id = db.Column(db.Integer, db.ForeignKey('cambio_estado.id'))
    valorMagnitud = db.Column(db.Float, nullable=False)
    coordenadaEpicentro = db.Column(db.String(100), nullable=False)
    coordenadaHipocentro = db.Column(db.String(100), nullable=False)
    fechaHoraOcurrencia = db.Column(db.DateTime, default=datetime.now)
    fechaHoraFin = db.Column(db.DateTime, default=datetime.now)
    usuario_revision = db.Column(db.String(50))
    accion_revision = db.Column(db.String(20))
    fecha_revision = db.Column(db.DateTime)
    alcance_id = db.Column(db.Integer, db.ForeignKey('alcance.id'))
    origen_de_generacion_id = db.Column(db.Integer, db.ForeignKey('origen_de_generacion.id'))
    clasificacion_sismo_id = db.Column(db.Integer, db.ForeignKey('clasificacion_sismo.id'))

    def to_dict(self):
        return {
            "id": self.id,
            "estado_id": self.estado_id,
            "cambio_estado_id": self.cambio_estado_id,
            "valorMagnitud": self.valorMagnitud,
            "coordenadaEpicentro": self.coordenadaEpicentro,
            "coordenadaHipocentro": self.coordenadaHipocentro,
            "fechaHoraOcurrencia": self.fechaHoraOcurrencia.isoformat(),
            "fechaHoraFin": self.fechaHoraFin.isoformat(),
            "revision": {
                "usuario": self.usuario_revision,
                "accion": self.accion_revision,
                "fecha": self.fecha_revision.isoformat() if self.fecha_revision else None
            },
            "alcance_id": self.alcance_id,
            "origen_de_generacion_id": self.origen_de_generacion_id,
            "clasificacion_sismo_id": self.clasificacion_sismo_id
        }
    
    def bloquear(self):
        if self.cambio_estado_id:
            cambio_anterior = CambioEstado.query.get(self.cambio_estado_id)
            if cambio_anterior and not cambio_anterior.fechaHoraFin:
                cambio_anterior.fechaHoraFin = datetime.now()
                db.session.commit()
        cambio = CambioEstado(
            fechaHoraInicio=datetime.now(),
            estado_id=4
        )
        db.session.add(cambio)
        db.session.commit()
        self.estado_id = 4
        self.cambio_estado_id = cambio.id
        db.session.commit()

    def rechazar(self):
        if self.cambio_estado_id:
            cambio_anterior = CambioEstado.query.get(self.cambio_estado_id)
            if cambio_anterior and not cambio_anterior.fechaHoraFin:
                cambio_anterior.fechaHoraFin = datetime.now()
                db.session.commit()
        cambio = CambioEstado(
            fechaHoraInicio=datetime.now(),
            estado_id=3
        )
        db.session.add(cambio)
        db.session.commit()
        self.estado_id = 3
        self.cambio_estado_id = cambio.id
        db.session.commit()
    
    def getAlcance(self):
        alcance = Alcance.query.get(self.alcance_id)
        return alcance.nombre if alcance else None

    def getOrigenDeGeneracion(self):
        origen = OrigenDeGeneracion.query.get(self.origen_de_generacion_id)
        return origen.nombre if origen else None
    
    def clasificacionSismo(self):
        clasificacion = ClasificacionSismo.query.get(self.clasificacion_sismo_id)
        return clasificacion.nombre if clasificacion else None

    def getEstado(self):
        estado = Estado.query.get(self.estado_id)
        return estado.nombre if estado else None

    def getDatos(self):
        return {
            "id": self.id,
            "valorMagnitud": self.valorMagnitud,
            "coordenadaEpicentro": self.coordenadaEpicentro,
            "coordenadaHipocentro": self.coordenadaHipocentro,
            "fechaHoraOcurrencia": self.fechaHoraOcurrencia.isoformat(),
            "fechaHoraFin": self.fechaHoraFin.isoformat(),
        }
    
#    def getDatosSismicos(self):
#        return {
#            "id": self.id,
#            "estado": self.getEstado(),
#            "cambio_estado_id": self.cambio_estado_id,
#            "valorMagnitud": self.valorMagnitud,
#            "coordenadaEpicentro": self.coordenadaEpicentro,
#            "coordenadaHipocentro": self.coordenadaHipocentro,
#            "fechaHoraOcurrencia": self.fechaHoraOcurrencia.isoformat(),
#            "fechaHoraFin": self.fechaHoraFin.isoformat(),
#            "alcance": self.getAlcance(),
#            "origen_de_generacion": self.getOrigenDeGeneracion(),
#            "clasificacion_sismo": self.clasificacionSismo()
#        }
    