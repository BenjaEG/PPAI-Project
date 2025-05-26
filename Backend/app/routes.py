from flask import Blueprint, request, jsonify
from .models import Evento, Estado, CambioEstado
from . import db
from datetime import datetime

bp = Blueprint("api", __name__)

@bp.route("/eventos", methods=["GET"])
def obtener_eventos():
    estado_nombre = request.args.get("estado", type=str)
    estado_nombre_a_id = {
        "Auto Detectado": 1,
        "Pendiente Revision": 2,
        "Sin Revision": 3,
        "Bloqueado": 4,
        "Rechazado": 5,
        "Derivado": 6,
        "Confirmado": 7,
        "Auto Confirmado": 8,
        "Pendiente Cierre": 9,
        "Cerrado": 10
    }
    query = Evento.query
    if estado_nombre:
        estado_id = estado_nombre_a_id.get(estado_nombre)
        if estado_id:
            query = query.filter_by(estado_id=estado_id)
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
    if fechaHoraFin:
        try:
            fechaHoraFin = datetime.fromisoformat(fechaHoraFin)
        except Exception:
            return jsonify({"error": "fechaHoraFin debe estar en formato ISO"}), 400
    else:
        fechaHoraFin = None

    nuevo_cambio = CambioEstado(
        fechaHoraInicio=fechaHoraInicio,
        fechaHoraFin=fechaHoraFin,
        estado_id=data["estado_id"]
    )
    db.session.add(nuevo_cambio)
    db.session.commit()
    return jsonify(nuevo_cambio.to_dict()), 201

@bp.route("/evento/<int:evento_id>/cambiar-estado/<string:nuevo_estado>", methods=["PUT"])
def cambiar_estado_evento(evento_id, nuevo_estado):
    estado_nombre_a_id = {
        "Auto Detectado": 1,
        "Pendiente Revision": 2,
        "Sin Revision": 3,
        "Bloqueado": 4,
        "Rechazado": 5,
        "Derivado": 6,
        "Confirmado": 7,
        "Auto Confirmado": 8,
        "Pendiente Cierre": 9,
        "Cerrado": 10
    }
    estado_id = estado_nombre_a_id.get(nuevo_estado)
    if not estado_id:
        return jsonify({"error": "Estado no válido"}), 400

    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    # Crear un nuevo CambioEstado
    nuevo_cambio = CambioEstado(
        fechaHoraInicio=datetime.utcnow(),
        estado_id=estado_id
    )
    db.session.add(nuevo_cambio)
    db.session.commit()

    # Actualizar el evento con el nuevo estado y cambio_estado_id
    evento.estado_id = estado_id
    evento.cambio_estado_id = nuevo_cambio.id
    db.session.commit()
    return jsonify(evento.to_dict()), 200

@bp.route("/evento/<int:evento_id>", methods=["GET"])
def obtener_evento(evento_id):
    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify(evento.to_dict_nombres()), 200