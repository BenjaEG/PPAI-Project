from flask import Blueprint, request, jsonify
from .models import (
    Evento,
    Estado,
    Sismografo,
    TipoDeDato,
)
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
    eventos = query.order_by(Evento.fechaHoraOcurrencia.desc()).all()
    return jsonify([evento.getDatos() for evento in eventos]), 200

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
    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    if nuevo_estado.lower() == "bloqueado":
        evento.bloquear()
    elif nuevo_estado.lower() == "rechazado":
        evento.rechazar()
    else:
        return jsonify({"error": "Estado no encontrado"}), 400

    return jsonify(evento.getDatos()), 200

@bp.route("/evento/<int:evento_id>", methods=["GET"])
def buscarDatosSismicos(evento_id):
    evento = Evento.query.get(evento_id)
    if not evento:
        return jsonify({"error": "Evento no encontrado"}), 404

    datos = evento.getDatos()
    datos["alcance"] = evento.getAlcance()
    datos["origen_de_generacion"] = evento.getOrigenDeGeneracion()
    datos["clasificacion_sismo"] = evento.clasificacionSismo()

    # Usar la función del modelo para traer las series temporales
    datos["series_temporales"] = evento.buscarDatosSeriesTemporales()

    return jsonify(datos), 200