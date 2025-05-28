from app.models import EventoSismico, db

class GestorRevisionEventos:
    def __init__(self):
        pass

    def bloquearES(self, evento_id):
        evento = EventoSismico.query.get(evento_id)
        if not evento:
            return None
        evento.bloquear()
        db.session.commit()
        return evento

    def ordenarES(self, eventos):
        return sorted(eventos, key=lambda x: x.fechaHoraOcurrencia, reverse=True)

    def buscarEventosSismicos(self):
        eventos = EventoSismico.query.all()
        eventos = [
            evento for evento in eventos
            if evento.esPendienteDeRevision() or evento.esAutoDetectado()
        ]
        eventos = self.ordenarES(eventos)
        return [evento.getDatos() for evento in eventos]
    
    def buscarEstadoRechazado(self, evento_id, usuario):
        evento = EventoSismico.query.get(evento_id)
        errores = self.validarRequisitos(evento)
        if errores:
            return {"errores": errores}
        if not evento:
            return None
        evento.rechazar(usuario)
        db.session.commit()
        return evento

    def buscarEstadoBloqueado(self, evento_id):
        evento = self.bloquearES(evento_id)
        return evento

    def buscarDatosSismicos(self, evento_id):
        evento = EventoSismico.query.get(evento_id)
        if not evento:
            return None
        datos = evento.getDatos()
        datos["alcance"] = evento.getAlcance()
        datos["origen_de_generacion"] = evento.getOrigenDeGeneracion()
        datos["clasificacion_sismo"] = evento.clasificacionSismo()
        datos["series_temporales"] = evento.buscarDatosSeriesTemporales()
        # Clasificar series por estación y reemplazar en el dict
        datos["series_temporales_por_estacion"] = self.clasificarPorEstacion(datos)
        self.llamarCUGenerarSismoGrama()
        return datos

    def clasificarPorEstacion(self, datos):
        if not datos or "series_temporales" not in datos:
            return {}

        series_temporales = datos["series_temporales"]
        series_por_estacion = {}

        for serie in series_temporales:
            estacion_info = serie.get("datosSismografo", {}).get("estacion")
            if estacion_info:
                clave_estacion = f'{estacion_info.get("codigoEstacion", "-")} - {estacion_info.get("nombre", "-")}'
            else:
                clave_estacion = "Sin estación"

            if clave_estacion not in series_por_estacion:
                series_por_estacion[clave_estacion] = []

            # Recorrer muestras sísmicas de la serie
            muestras = serie.get("datosMuestrasSismicas", [])
            for muestra in muestras:
                instante = muestra.get("fechaHoraMuestra")
                detalles = muestra.get("detalles", [])
                valores = {
                    "instante": instante,
                    "velocidad_onda": None,
                    "frecuencia_onda": None,
                    "longitud": None
                }
                for detalle in detalles:
                    tipo = (detalle.get("tipoDeDato") or "").strip().lower()
                    valor = detalle.get("valor")
                    # Ajusta los nombres según tus tipos de dato reales
                    if "velocidad" in tipo or "km/seg" in tipo:
                        valores["velocidad_onda"] = valor
                    elif "frecuencia" in tipo or "hz" in tipo:
                        valores["frecuencia_onda"] = valor
                    elif "longitud" in tipo or "km/ciclo" in tipo:
                        valores["longitud"] = valor
                series_por_estacion[clave_estacion].append(valores)

        return series_por_estacion

    def llamarCUGenerarSismoGrama(self):
        pass

    def validarRequisitos(self, evento):
        errores = []
        if evento is None:
            errores.append("El evento no existe.")
            return errores
        if evento.valorMagnitud is None:
            errores.append("El evento no tiene magnitud.")
        if not evento.alcance_id:
            errores.append("El evento no tiene alcance.")
        if not evento.origen_de_generacion_id:
            errores.append("El evento no tiene origen de generación.")
        return errores

    def finCU(self):
        pass