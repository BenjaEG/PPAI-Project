from flask import Blueprint, request, jsonify
from .models import Evento, Estado, CambioEstado
from . import db
from datetime import datetime

bp = Blueprint("api", __name__)

@bp.route("/eventos", methods=["GET"])
def obtener_eventos():
    estado_nombre = request.args.get("estado", type=str)
    query = Evento.query
    if estado_nombre:
        estado = Estado.query.filter_by(nombre=estado_nombre).first()
        if estado:
            query = query.filter_by(estado_id=estado.id)
        else:
            return jsonify([]), 200
    eventos = query.all()
    return jsonify([evento.to_dict() for evento in eventos]), 200

@bp.route("/crear-evento", methods=["POST"])
def crear_evento():
    data = request.json
    nuevo = Evento(
        estado_id=data["estado_id"],
        cambio_estado_id=data["cambio_estado_id"],
        valorMagnitud=data["valorMagnitud"],
        coordenadaEpicentro=data["coordenadaEpicentro"],
        coordenadaHipocentro=data["coordenadaHipocentro"],
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201



@bp.route("/revisar-evento/<int:evento_id>", methods=["POST"])
def revisar_evento(evento_id):
    data = request.json
    accion = data.get("accion")
    usuario = data.get("usuario")

    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    if evento.estado != "auto_detectado":
        return jsonify({"error": "Evento ya revisado"}), 400

    if accion not in ["confirmar", "rechazar", "derivar"]:
        return jsonify({"error": "Acción inválida"}), 400

    if accion == "confirmar":
        evento.estado = "confirmado"
    elif accion == "rechazar":
        evento.estado = "rechazado"
    else:
        evento.estado = "derivado"

    evento.usuario_revision = usuario
    evento.accion_revision = accion
    evento.fecha_revision = datetime.utcnow()

    db.session.commit()
    return jsonify(evento.to_dict()), 200

@bp.route("/cambio-estado", methods=["POST"])
def crear_cambio_estado():
    data = request.json

    fechaHoraInicio = data.get("fechaHoraInicio")
    if fechaHoraInicio:
        try:
            fechaHoraInicio = datetime.fromisoformat(fechaHoraInicio)
        except Exception:
            return jsonify({"error": "fechaHoraInicio debe estar en formato ISO"}), 400
    else:
        fechaHoraInicio = datetime.utcnow()

    fechaHoraFin = data.get("fechaHoraFin")

    nuevo_cambio = CambioEstado(
        fechaHoraInicio=fechaHoraInicio,
        estado_id=data["estado_id"]
    )
    db.session.add(nuevo_cambio)
    db.session.commit()
    return jsonify(nuevo_cambio.to_dict()), 201

@bp.route("/evento/<int:evento_id>/cambiar-estado/<string:nuevo_estado>", methods=["PUT"])
def cambiar_estado_evento(evento_id, nuevo_estado):
    # Buscar el estado por nombre en la base de datos
    estado = Estado.query.filter_by(nombre=nuevo_estado).first()
    if not estado:
        return jsonify({"error": "Estado no válido"}), 400

    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    # Actualizar fechaHoraFin del CambioEstado actual
    if evento.cambio_estado_id:
        cambio_actual = CambioEstado.query.get(evento.cambio_estado_id)
        if cambio_actual and not cambio_actual.fechaHoraFin:
            cambio_actual.fechaHoraFin = datetime.utcnow()
            db.session.commit()

    # Crear un nuevo CambioEstado
    nuevo_cambio = CambioEstado(
        fechaHoraInicio=datetime.utcnow(),
        estado_id=estado.id
    )
    db.session.add(nuevo_cambio)
    db.session.commit()

    # Actualizar el evento con el nuevo estado y cambio_estado_id
    evento.estado_id = estado.id
    evento.cambio_estado_id = nuevo_cambio.id
    db.session.commit()
    return jsonify(evento.to_dict()), 200

@bp.route("/evento/<int:evento_id>", methods=["GET"])
def obtener_evento(evento_id):
    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify(evento.to_dict_nombres()), 200