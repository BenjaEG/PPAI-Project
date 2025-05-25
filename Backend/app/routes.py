from flask import Blueprint, request, jsonify
from .models import Evento
from . import db
from datetime import datetime

bp = Blueprint("api", __name__)

@bp.route("/eventos", methods=["GET"])
def obtener_eventos():
    eventos = Evento.query.all()
    return jsonify([evento.to_dict() for evento in eventos]), 200

@bp.route("/crear-evento", methods=["POST"])
def crear_evento():
    data = request.json
    nuevo = Evento(
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