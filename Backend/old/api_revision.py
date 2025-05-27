# archivo: api_revision.py
from flask import Flask, request, jsonify
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

app = Flask(__name__)

# Configuración de la base de datos SQLite
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.db'
db = SQLAlchemy(app)

# Modelo de Evento Sísmico
class Evento(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    estado = db.Column(db.String(20), default='auto_detectado')
    magnitud = db.Column(db.Float, nullable=False)
    ubicacion = db.Column(db.String(100), nullable=False)
    fecha = db.Column(db.DateTime, default=datetime.now)
    usuario_revision = db.Column(db.String(50))
    accion_revision = db.Column(db.String(20))
    fecha_revision = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "estado": self.estado,
            "magnitud": self.magnitud,
            "ubicacion": self.ubicacion,
            "fecha": self.fecha.isoformat(),
            "revision": {
                "usuario": self.usuario_revision,
                "accion": self.accion_revision,
                "fecha": self.fecha_revision.isoformat() if self.fecha_revision else None
            }
        }

# Ruta para revisar un evento
@app.route("/revisar-evento/<int:evento_id>", methods=["POST"])
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

# Ruta para cargar eventos de prueba (opcional)
@app.route("/crear-evento", methods=["POST"])
def crear_evento():
    data = request.json
    nuevo = Evento(
        magnitud=data["magnitud"],
        ubicacion=data["ubicacion"]
    )
    db.session.add(nuevo)
    db.session.commit()
    return jsonify(nuevo.to_dict()), 201

# Ruta para obtener todos los eventos
@app.route("/eventos", methods=["GET"])
def obtener_eventos():
    eventos = Evento.query.all()
    return jsonify([evento.to_dict() for evento in eventos]), 200

if __name__ == "__main__":
    with app.app_context():
        db.create_all()  # Crea las tablas si no existen
    app.run(debug=True)

