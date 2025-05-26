from . import db
from .models import Estado, CambioEstado, Evento, Alcance, OrigenDeGeneracion, ClasificacionSismo
from datetime import datetime

def bulk_create_eventos():
    if Estado.query.first() is not None:
        print("La base ya contiene datos. Seed cancelado.")
        return

    print("Insertando datos iniciales...")

    estados = [
        Estado(nombre=e["nombre"], ambito=e["ambito"])
        for e in [
            {"nombre": "Auto Detectado", "ambito": "eventoSismo"},
            {"nombre": "Pendiente Revision", "ambito": "eventoSismo"},
            {"nombre": "Sin Revision", "ambito": "eventoSismo"},
            {"nombre": "Bloqueado", "ambito": "eventoSismo"},
            {"nombre": "Rechazado", "ambito": "eventoSismo"},
            {"nombre": "Derivado", "ambito": "eventoSismo"},
            {"nombre": "Confirmado", "ambito": "eventoSismo"},
            {"nombre": "Auto Confirmado", "ambito": "eventoSismo"},
            {"nombre": "Pendiente Cierre", "ambito": "eventoSismo"},
            {"nombre": "Cerrado", "ambito": "eventoSismo"},
        ]
    ]
    db.session.bulk_save_objects(estados)
    db.session.commit()

    cambios = [
        CambioEstado(
            fechaHoraInicio=datetime.fromisoformat(c["fechaHoraInicio"].replace("Z", "+00:00")),
            estado_id=c["estado_id"]
        )
        for c in [
            {"fechaHoraInicio": "2023-01-01T00:00:00Z", "estado_id": 2},
            {"fechaHoraInicio": "2023-02-01T00:00:00Z", "estado_id": 2},
            {"fechaHoraInicio": "2023-03-01T00:00:00Z", "estado_id": 2},
            {"fechaHoraInicio": "2023-04-01T00:00:00Z", "estado_id": 2},
            {"fechaHoraInicio": "2023-05-01T00:00:00Z", "estado_id": 2},
            {"fechaHoraInicio": "2023-06-01T00:00:00Z", "estado_id": 3},
            {"fechaHoraInicio": "2023-07-01T00:00:00Z", "estado_id": 4},
            {"fechaHoraInicio": "2023-08-01T00:00:00Z", "estado_id": 5},
            {"fechaHoraInicio": "2023-09-01T00:00:00Z", "estado_id": 6},
            {"fechaHoraInicio": "2023-10-01T00:00:00Z", "estado_id": 7},
            {"fechaHoraInicio": "2023-11-01T00:00:00Z", "estado_id": 8},
            {"fechaHoraInicio": "2023-12-01T00:00:00Z", "estado_id": 9},
            {"fechaHoraInicio": "2024-01-01T00:00:00Z", "estado_id": 10},
            {"fechaHoraInicio": "2024-02-01T00:00:00Z", "estado_id": 1},
            {"fechaHoraInicio": "2024-03-01T00:00:00Z", "estado_id": 1},
            {"fechaHoraInicio": "2024-04-01T00:00:00Z", "estado_id": 1}
        ]
    ]
    db.session.bulk_save_objects(cambios)
    db.session.commit()

    alcances = [
        Alcance(nombre="sismos locales", descripcion="hasta 100km"),
        Alcance(nombre="sismos regionales", descripcion="hasta 1000km"),
        Alcance(nombre="tele sismos", descripcion="mas de 1000km")
    ]
    db.session.bulk_save_objects(alcances)
    db.session.commit()

    origenes = [
        OrigenDeGeneracion(nombre="sismo interplaca", descripcion="Sismo generado por el movimiento entre placas tectónicas."),
        OrigenDeGeneracion(nombre="sismo volcánico", descripcion="Sismo asociado a la actividad volcánica y movimientos magmáticos."),
        OrigenDeGeneracion(nombre="sismo provocado por explosiones de minas", descripcion="Sismo causado por actividades humanas como explosiones en minas.")
    ]
    db.session.bulk_save_objects(origenes)
    db.session.commit()

    clasificaciones = [
        ClasificacionSismo(nombre="sismo superficial", kmProfundidadDesde=0, kmProfundidadHasta=60),
        ClasificacionSismo(nombre="sismo intermedio", kmProfundidadDesde=61, kmProfundidadHasta=300),
        ClasificacionSismo(nombre="sismo profundo", kmProfundidadDesde=301, kmProfundidadHasta=650)
    ]
    db.session.bulk_save_objects(clasificaciones)
    db.session.commit()

    eventos = [
        Evento(
            estado_id=e["estado_id"],
            cambio_estado_id=e["cambio_estado_id"],
            valorMagnitud=e["valorMagnitud"],
            coordenadaEpicentro=e["coordenadaEpicentro"],
            coordenadaHipocentro=e["coordenadaHipocentro"],
            fechaHoraOcurrencia=datetime.fromisoformat(e["fechaHoraOcurrencia"].replace("Z", "+00:00")),
            fechaHoraFin=datetime.fromisoformat(e["fechaHoraFin"].replace("Z", "+00:00")),
            alcance_id=(i % 3) + 1,
            origen_de_generacion_id=(i % 3) + 1,
            clasificacion_sismo_id=(i % 3) + 1
        )
        for i, e in enumerate([
            {"estado_id": 2, "cambio_estado_id": 1, "valorMagnitud": 5.0, "coordenadaEpicentro": "10.0, 20.0", "coordenadaHipocentro": "10.0, 20.0", "fechaHoraOcurrencia": "2023-01-01T00:00:00Z", "fechaHoraFin": "2023-01-01T01:00:00Z"},
            {"estado_id": 2, "cambio_estado_id": 2, "valorMagnitud": 4.5, "coordenadaEpicentro": "15.0, 25.0", "coordenadaHipocentro": "15.0, 25.0", "fechaHoraOcurrencia": "2023-02-01T00:00:00Z", "fechaHoraFin": "2023-02-01T01:00:00Z"},
            {"estado_id": 2, "cambio_estado_id": 3, "valorMagnitud": 6.0, "coordenadaEpicentro": "20.0, 30.0", "coordenadaHipocentro": "20.0, 30.0", "fechaHoraOcurrencia": "2023-03-01T00:00:00Z", "fechaHoraFin": "2023-03-01T01:00:00Z"},
            {"estado_id": 2, "cambio_estado_id": 4, "valorMagnitud": 5.5, "coordenadaEpicentro": "25.0, 35.0", "coordenadaHipocentro": "25.0, 35.0", "fechaHoraOcurrencia": "2023-04-01T00:00:00Z", "fechaHoraFin": "2023-04-01T01:00:00Z"},
            {"estado_id": 2, "cambio_estado_id": 5, "valorMagnitud": 4.0, "coordenadaEpicentro": "30.0, 40.0", "coordenadaHipocentro": "30.0, 40.0", "fechaHoraOcurrencia": "2023-05-01T00:00:00Z", "fechaHoraFin": "2023-05-01T01:00:00Z"},
            {"estado_id": 3, "cambio_estado_id": 6, "valorMagnitud": 5.2, "coordenadaEpicentro": "35.0, 45.0", "coordenadaHipocentro": "35.0, 45.0", "fechaHoraOcurrencia": "2023-06-01T00:00:00Z", "fechaHoraFin": "2023-06-01T01:00:00Z"},
            {"estado_id": 4, "cambio_estado_id": 7, "valorMagnitud": 6.3, "coordenadaEpicentro": "40.0, 50.0", "coordenadaHipocentro": "40.0, 50.0", "fechaHoraOcurrencia": "2023-07-01T00:00:00Z", "fechaHoraFin": "2023-07-01T01:00:00Z"},
            {"estado_id": 5, "cambio_estado_id": 8, "valorMagnitud": 4.8, "coordenadaEpicentro": "45.0, 55.0", "coordenadaHipocentro": "45.0, 55.0", "fechaHoraOcurrencia": "2023-08-01T00:00:00Z", "fechaHoraFin": "2023-08-01T01:00:00Z"},
            {"estado_id": 6, "cambio_estado_id": 9, "valorMagnitud": 5.1, "coordenadaEpicentro": "50.0, 60.0", "coordenadaHipocentro": "50.0, 60.0", "fechaHoraOcurrencia": "2023-09-01T00:00:00Z", "fechaHoraFin": "2023-09-01T01:00:00Z"},
            {"estado_id": 7, "cambio_estado_id": 10, "valorMagnitud": 6.1, "coordenadaEpicentro": "55.0, 65.0", "coordenadaHipocentro": "55.0, 65.0", "fechaHoraOcurrencia": "2023-10-01T00:00:00Z", "fechaHoraFin": "2023-10-01T01:00:00Z"},
            {"estado_id": 8, "cambio_estado_id": 11, "valorMagnitud": 4.9, "coordenadaEpicentro": "60.0, 70.0", "coordenadaHipocentro": "60.0, 70.0", "fechaHoraOcurrencia": "2023-11-01T00:00:00Z", "fechaHoraFin": "2023-11-01T01:00:00Z"},
            {"estado_id": 9, "cambio_estado_id": 12, "valorMagnitud": 5.4, "coordenadaEpicentro": "65.0, 75.0", "coordenadaHipocentro": "65.0, 75.0", "fechaHoraOcurrencia": "2023-12-01T00:00:00Z", "fechaHoraFin": "2023-12-01T01:00:00Z"},
            {"estado_id": 10, "cambio_estado_id": 13, "valorMagnitud": 6.4, "coordenadaEpicentro": "70.0, 80.0", "coordenadaHipocentro": "70.0, 80.0", "fechaHoraOcurrencia": "2024-01-01T00:00:00Z", "fechaHoraFin": "2024-01-01T01:00:00Z"},
            {"estado_id": 1, "cambio_estado_id": 14, "valorMagnitud": 5.3, "coordenadaEpicentro": "75.0, 85.0", "coordenadaHipocentro": "75.0, 85.0", "fechaHoraOcurrencia": "2024-02-01T00:00:00Z", "fechaHoraFin": "2024-02-01T01:00:00Z"},
            {"estado_id": 1, "cambio_estado_id": 15, "valorMagnitud": 4.7, "coordenadaEpicentro": "80.0, 90.0", "coordenadaHipocentro": "80.0, 90.0", "fechaHoraOcurrencia": "2024-03-01T00:00:00Z", "fechaHoraFin": "2024-03-01T01:00:00Z"},
            {"estado_id": 1, "cambio_estado_id": 16, "valorMagnitud": 5.6, "coordenadaEpicentro": "85.0, 95.0", "coordenadaHipocentro": "85.0, 95.0", "fechaHoraOcurrencia": "2024-04-01T00:00:00Z", "fechaHoraFin": "2024-04-01T01:00:00Z"}
        ])
    ]
    db.session.bulk_save_objects(eventos)
    db.session.commit()

    print("Datos iniciales insertados correctamente.")