from flask import Blueprint, request, jsonify
from .services.gestor_revision import GestorRevisionEventos, Usuario
from .models import (
    EventoSismico,
)
from . import db
from datetime import datetime

bp = Blueprint("api", __name__)

gestor = GestorRevisionEventos()

@bp.route("/eventos", methods=["GET"])
def registroRevisionManual():
    eventos = gestor.buscarEventosSismicos()
    return jsonify(eventos), 200

@bp.route("/evento/<int:evento_id>/seleccionar", methods=["PUT"])
def tomarSeleccionES(evento_id):
    data = request.get_json()
    user = data.get("usuario") if data else None
    if not user:
        return jsonify({"error": "Usuario no proporcionado"}), 400
    usuario = Usuario(user)
    Usuario.setUsuarioActual(usuario)
    evento = gestor.buscarEstadoBloqueado(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    return jsonify(evento.getDatos()), 200

@bp.route("/evento/<int:evento_id>/rechazar", methods=["PUT"])
def tomarSeleccionOpc(evento_id):
    data = request.get_json()
    user = data.get("usuario") if data else None
    if not user:
        return jsonify({"error": "Usuario no proporcionado"}), 400
    usuario = Usuario(user)
    Usuario.setUsuarioActual(usuario)
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