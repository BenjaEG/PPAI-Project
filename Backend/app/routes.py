from flask import Blueprint, request, jsonify
from .services.gestor_revision import GestorRevisionEventos
from .models import (
    Evento,
)
from . import db
from datetime import datetime

bp = Blueprint("api", __name__)


@bp.route("/eventos", methods=["GET"])
def obtener_eventos():
    estado_nombre = request.args.get("estado", type=str)
    gestor = GestorRevisionEventos()
    eventos = gestor.buscarEventosSismicos(estado_nombre)
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

@bp.route("/evento/<int:evento_id>/cambiar-estado/<string:nuevo_estado>", methods=["PUT"])
def cambiar_estado_evento(evento_id, nuevo_estado):
    gestor = GestorRevisionEventos()
    if nuevo_estado.lower() == "bloqueado":
        evento = gestor.buscarEstadoBloqueado(evento_id)
    elif nuevo_estado.lower() == "rechazado":
        evento = gestor.buscarEstadoRechazado(evento_id)
    else:
        return jsonify({"error": "Estado no encontrado"}), 400

    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    return jsonify(evento.getDatos()), 200

@bp.route("/evento/<int:evento_id>", methods=["GET"])
def buscarDatosSismicos(evento_id):
    gestor = GestorRevisionEventos()
    datos = gestor.buscarDatosSismicos(evento_id)
    if not datos:
        return jsonify({"error": "Evento no encontrado"}), 404
    return jsonify(datos), 200