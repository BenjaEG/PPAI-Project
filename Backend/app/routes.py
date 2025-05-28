from flask import Blueprint, request, jsonify
from .services.gestor_revision import GestorRevisionEventos
from .models import (
    Evento,
)
from . import db
from datetime import datetime

bp = Blueprint("api", __name__)

gestor = GestorRevisionEventos()

@bp.route("/eventos", methods=["GET"])
def registroRevisionManual():
    eventos = gestor.buscarEventosSismicos()
    return jsonify(eventos), 200

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
    evento.fecha_revision = datetime.now()

    db.session.commit()
    return jsonify(evento.to_dict()), 200

@bp.route("/evento/<int:evento_id>/seleccionar", methods=["PUT"])
def tomarSeleccionES(evento_id):
    evento = gestor.buscarEstadoBloqueado(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    return jsonify(evento.getDatos()), 200

@bp.route("/evento/<int:evento_id>/rechazar", methods=["PUT"])
def tomarSeleccionOpc(evento_id):
    evento = gestor.buscarEstadoRechazado(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    return jsonify(evento.getDatos()), 200

@bp.route("/evento/<int:evento_id>", methods=["GET"])
def datosSismicos(evento_id):
    datos = gestor.buscarDatosSismicos(evento_id)
    if not datos:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify(datos), 200