from app import create_app
from app.seeds import bulk_create_eventos
from app.task import liberar_eventos_ocupados
import threading

app = create_app()

with app.app_context():
    bulk_create_eventos()

def start_background_task():
    from flask import current_app
    with app.app_context():
        liberar_eventos_ocupados()

if __name__ == "__main__":
    # Inicia el hilo en segundo plano
    t = threading.Thread(target=start_background_task, daemon=True)
    t.start()
    app.run(debug=False, host='192.168.0.194')  # <-- Cambia aquí