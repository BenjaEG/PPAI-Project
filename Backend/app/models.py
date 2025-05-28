from . import db
from datetime import datetime

class Estado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(20), nullable=False)
    ambito = db.Column(db.String(50), nullable=False)

    def getDatos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "ambito": self.ambito
        }
    
    def esAutoDetectado(self):
        return self.nombre.strip().lower().replace("_", " ") == "auto detectado"

    def esPendienteDeRevision(self):
        return self.nombre.strip().lower().replace("_", " ") == "pendiente revision"

class CambioEstado(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fechaHoraInicio = db.Column(db.DateTime, nullable=False, default=datetime.now)
    fechaHoraFin = db.Column(db.DateTime)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)

    def getDatos(self):
        return {
            "id": self.id,
            "fechaHoraInicio": self.fechaHoraInicio.isoformat(),
            "fechaHoraFin": self.fechaHoraFin.isoformat() if self.fechaHoraFin else None,
            "estado_id": self.estado_id
        }
    
    @classmethod
    def new(cls, fechaHoraInicio, estado_id):
        obj = cls(fechaHoraInicio=fechaHoraInicio, estado_id=estado_id)
        db.session.add(obj)
        db.session.commit()
        return obj

class Alcance(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)

    def getDatos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }
    
    def getNombre(self):
        return self.nombre

class OrigenDeGeneracion(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    descripcion = db.Column(db.String(200), nullable=True)

    def getDatos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "descripcion": self.descripcion
        }
    
    def getNombre(self):
        return self.nombre

class ClasificacionSismo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    kmProfundidadDesde = db.Column(db.Float, nullable=False)
    kmProfundidadHasta = db.Column(db.Float, nullable=False)

    def getDatos(self):
        return {
            "id": self.id,
            "nombre": self.nombre,
            "kmProfundidadDesde": self.kmProfundidadDesde,
            "kmProfundidadHasta": self.kmProfundidadHasta
        }
    
    def getNombre(self):
        return self.nombre

class EstacionSismologica(db.Model):
    codigoEstacion = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    documentoCertificacionAdq = db.Column(db.String(100), nullable=True)
    fechaSolicitudCertificacion = db.Column(db.DateTime, nullable=True)
    latitud = db.Column(db.Float, nullable=True)
    longitud = db.Column(db.Float, nullable=True)
    nroCertificacionAdquisicion = db.Column(db.String(50), nullable=True)

    def getCodigoEstacion(self):
        return self.codigoEstacion
    def getNombre(self):
        return self.nombre

class TipoDeDato(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    denominacion = db.Column(db.String(50), nullable=False)
    nombreUnidadMedida = db.Column(db.String(50), nullable=True)
    valorUmbral = db.Column(db.Float, nullable=True)
    
    def getDenominacion(self):
        return self.denominacion

class DetalleMuestraSismica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nombre = db.Column(db.String(50), nullable=False)
    valor = db.Column(db.Float, nullable=False)
    tipoDeDato = db.Column(db.Integer, db.ForeignKey('tipo_de_dato.id'), nullable=False)
    muestra_sismica_id = db.Column(db.Integer, db.ForeignKey('muestra_sismica.id'), nullable=False)

    def getDatos(self):
        tipo_dato_obj = TipoDeDato.query.get(self.tipoDeDato)
        return {
            "id": self.id,
            "nombre": self.nombre,
            "valor": self.valor,
            "tipoDeDato": tipo_dato_obj.getDenominacion() if tipo_dato_obj else None,
            "muestra_sismica_id": self.muestra_sismica_id
        }

class MuestraSismica(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fechaHoraMuestra = db.Column(db.DateTime, nullable=False, default=datetime.now)
    serie_temporal_id = db.Column(db.Integer, db.ForeignKey('serie_temporal.id'), nullable=False)
    detalleMuestraSismica = db.relationship('DetalleMuestraSismica', backref='muestra_sismica', lazy=True)

    def crearDetalleMuestra(self, valor, tipo_de_dato):
        detalle = DetalleMuestraSismica.new(valor, tipo_de_dato, self.id)
        return detalle
    
    def getDatos(self):
        detalles = [detalle.getDatos() for detalle in self.detalleMuestraSismica]
        return {
            "id": self.id,
            "fechaHoraMuestra": self.fechaHoraMuestra.isoformat(),
            "detalles": detalles
        }

class Sismografo(db.Model):
    nroSerie = db.Column(db.Integer, primary_key=True)
    identificadorSismografo = db.Column(db.String(50), nullable=False)
    estacionSismologica = db.Column(db.Integer, db.ForeignKey('estacion_sismologica.codigoEstacion'), nullable=False)
    fechaAdquisicion = db.Column(db.DateTime, nullable=True, default=datetime.now)

    def getIdentificadorSismografo(self):
        return self.identificadorSismografo

    def conocerEstacion(self):
        estacion = EstacionSismologica.query.get(self.estacionSismologica)
        if estacion:
            return {
                "codigoEstacion": estacion.getCodigoEstacion(),
                "nombre": estacion.getNombre()
            }
        return None

class SerieTemporal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    fechaHoraInicioRegistroMuestras = db.Column(db.DateTime, nullable=True, default=datetime.now)
    fechaHoraInicio = db.Column(db.DateTime, nullable=True, default=datetime.now)
    frecuenciaMuestreo = db.Column(db.Float, nullable=False)
    sismografo_nroSerie = db.Column(db.Integer, db.ForeignKey('sismografo.nroSerie'), nullable=False)
    evento_id = db.Column(db.Integer, db.ForeignKey('evento_sismico.id'), nullable=False)
    coleccionMuestrasSismicas = db.relationship('MuestraSismica', backref='serie_temporal', lazy=True)

    def getDatos(self):
        return {
            "id": self.id,
            "fechaHoraInicioRegistroMuestras": self.fechaHoraInicioRegistroMuestras.isoformat(),
            "fechaHoraInicio": self.fechaHoraInicio.isoformat(),
            "frecuenciaMuestreo": self.frecuenciaMuestreo,
            "datosMuestrasSismicas": [muestra.getDatos() for muestra in self.coleccionMuestrasSismicas],
            "datosSismografo": {
                "identificadorSismografo": Sismografo.query.get(self.sismografo_nroSerie).getIdentificadorSismografo() if self.sismografo_nroSerie else None,
                "estacion": Sismografo.query.get(self.sismografo_nroSerie).conocerEstacion() if self.sismografo_nroSerie else None
            },  
        }

class EventoSismico(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estado_id = db.Column(db.Integer, db.ForeignKey('estado.id'), nullable=False)
    cambio_estado_id = db.Column(db.Integer, db.ForeignKey('cambio_estado.id'))
    valorMagnitud = db.Column(db.Float, nullable=False)
    coordenadaEpicentro = db.Column(db.String(100), nullable=False)
    coordenadaHipocentro = db.Column(db.String(100), nullable=False)
    fechaHoraOcurrencia = db.Column(db.DateTime, default=datetime.now)
    fechaHoraFin = db.Column(db.DateTime, default=datetime.now)
    alcance_id = db.Column(db.Integer, db.ForeignKey('alcance.id'))
    origen_de_generacion_id = db.Column(db.Integer, db.ForeignKey('origen_de_generacion.id'))
    clasificacion_sismo_id = db.Column(db.Integer, db.ForeignKey('clasificacion_sismo.id'))
    coleccionSeriesTemporales = db.relationship('SerieTemporal', backref='evento', lazy=True)
    fechaHoraRevision = db.Column(db.DateTime, nullable=True)
    responsableRevision = db.Column(db.String(100), nullable=True)
    
    def bloquear(self):
        if self.cambio_estado_id:
            cambio_anterior = CambioEstado.query.get(self.cambio_estado_id)
            if cambio_anterior and not cambio_anterior.fechaHoraFin:
                cambio_anterior.fechaHoraFin = datetime.now()
                db.session.commit()
        cambio = CambioEstado.new(datetime.now(), 4)
        self.estado_id = 4
        self.cambio_estado_id = cambio.id
        db.session.commit()

    def rechazar(self, usuario):
        if self.cambio_estado_id:
            cambio_anterior = CambioEstado.query.get(self.cambio_estado_id)
            if cambio_anterior and not cambio_anterior.fechaHoraFin:
                cambio_anterior.fechaHoraFin = datetime.now()
                db.session.commit()
        cambio = CambioEstado.new(datetime.now(), 3)
        self.setFechaHoraRevision()
        self.setResponsableRevision(usuario)
        self.estado_id = 3
        self.cambio_estado_id = cambio.id
        db.session.commit()
    
    def getAlcance(self):
        alcance = Alcance.query.get(self.alcance_id)
        return alcance.getNombre() if alcance else None

    def getOrigenDeGeneracion(self):
        origen = OrigenDeGeneracion.query.get(self.origen_de_generacion_id)
        return origen.getNombre() if origen else None

    def clasificacionSismo(self):
        clasificacion = ClasificacionSismo.query.get(self.clasificacion_sismo_id)
        return clasificacion.getNombre() if clasificacion else None
    
    def esPendienteDeRevision(self):
        estado = Estado.query.get(self.estado_id)
        return estado.esPendienteDeRevision() if estado else False
    
    def esAutoDetectado(self):
        estado = Estado.query.get(self.estado_id)
        return estado.esAutoDetectado() if estado else False

    def getDatos(self):
        return {
            "id": self.id,
            "valorMagnitud": self.valorMagnitud,
            "coordenadaEpicentro": self.coordenadaEpicentro,
            "coordenadaHipocentro": self.coordenadaHipocentro,
            "fechaHoraOcurrencia": self.fechaHoraOcurrencia.isoformat(),
            "fechaHoraFin": self.fechaHoraFin.isoformat(),
        }
    
    def buscarDatosSeriesTemporales(self):
        return [serie.getDatos() for serie in self.coleccionSeriesTemporales]
    
    def setResponsableRevision(self, usuario):
        self.responsableRevision = usuario
        db.session.commit()

    def setFechaHoraRevision(self):
        self.fechaHoraRevision = datetime.now()
        db.session.commit()