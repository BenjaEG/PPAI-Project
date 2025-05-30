let eventoSeleccionadoId = null;

document.addEventListener('DOMContentLoaded', () => {

    const API_URL = 'http://192.168.0.194:5000';

    // Renderiza la tabla de eventos o el detalle de un evento
    function renderEventos(eventos) {
        const eventosContainer = document.getElementById('eventosContainer');
        const tablaCabecera = document.getElementById('tablaCabecera');
        eventosContainer.innerHTML = '';

        if (eventos.length === 0) {
            eventosContainer.innerHTML = `
                <tr>
                    <td colspan="9" class="text-center">No se encontraron eventos.</td>
                </tr>
            `;
            if (tablaCabecera) tablaCabecera.style.display = '';
            return;
        }

        // Si hay solo uno y está seleccionado, mostrar todos los datos en detalle
        if (eventos.length === 1 && eventoSeleccionadoId == eventos[0].id) {
            const evento = eventos[0];
            if (tablaCabecera) tablaCabecera.style.display = 'none';

            // Tabla principal de datos del evento
            let html = `
                <tr>
                    <td colspan="2" class="text-center">
                        <table class="table table-bordered w-auto mx-auto mb-4">
                            <tr><th>ID</th><td>${evento.id}</td></tr>
                            <tr><th>Magnitud</th><td>${evento.valorMagnitud}</td></tr>
                            <tr><th>Fecha Fin</th><td>${evento.fechaHoraFin}</td></tr>
                            <tr><th>Fecha Ocurrencia</th><td>${evento.fechaHoraOcurrencia}</td></tr>
                            <tr><th>Coordenada Epicentro</th><td>${evento.coordenadaEpicentro}</td></tr>
                            <tr><th>Coordenada Hipocentro</th><td>${evento.coordenadaHipocentro}</td></tr>
                            <tr><th>Alcance</th><td>${evento.alcance || '-'}</td></tr>
                            <tr><th>Origen de Generación</th><td>${evento.origen_de_generacion || '-'}</td></tr>
                            <tr><th>Clasificación Sismo</th><td>${evento.clasificacion_sismo || '-'}</td></tr>
                        </table>
                        <h5 class="mb-2">Series Temporales</h5>
                        ${renderSeriesTemporales(evento.series_temporales)}
                        <h5 class="mb-2">Datos Clasificados por Estación</h5>
                        ${renderSeriesPorEstacion(evento.series_temporales_por_estacion)}
                        <div class="text-center mt-3">
                            <!-- Botones info arriba -->
                            <button type="button" class="btn btn-info me-2" id="visualizarMapaBtn">Visualizar Mapa</button>
                            <button type="button" class="btn btn-info me-2" id="modificarDatosBtn">Modificar Datos</button>
                        </div>
                        <div class="text-center mt-3">
                            <!-- Botones de acción debajo -->
                            <button type="button" class="btn btn-success me-2" id="confirmarBtn">Confirmar</button>
                            <button type="button" class="btn btn-danger me-2" id="rechazarBtn">Rechazar</button>
                            <button type="button" class="btn btn-warning me-2" id="solicitarRevisionBtn">Solicitar Revisión</button>
                        </div>
                    </td>
                </tr>
            `;
            eventosContainer.innerHTML = html;

            // Botón Confirmar
            document.getElementById('confirmarBtn').addEventListener('click', async () => {
                const usuario = sessionStorage.getItem('usuario');
                if (!usuario) {
                    alert('Debe iniciar sesión para realizar esta acción.');
                    window.location.href = '/index.html';
                    return;
                }
                await tomarSeleccionOpc(evento.id, usuario, "confirmar");
                eventoSeleccionadoId = null;
                fetchEventos();
            });

            // Botón Rechazar
            document.getElementById('rechazarBtn').addEventListener('click', async () => {
                const usuario = sessionStorage.getItem('usuario');
                if (!usuario) {
                    alert('Debe iniciar sesión para realizar esta acción.');
                    window.location.href = '/index.html';
                    return;
                }
                await tomarSeleccionOpc(evento.id, usuario, "rechazar");
                eventoSeleccionadoId = null;
                fetchEventos();
            });

            // Botón Solicitar Revisión
            document.getElementById('solicitarRevisionBtn').addEventListener('click', async () => {
                const usuario = sessionStorage.getItem('usuario');
                if (!usuario) {
                    alert('Debe iniciar sesión para realizar esta acción.');
                    window.location.href = '/index.html';
                    return;
                }
                await tomarSeleccionOpc(evento.id, usuario, "solicitar revision");
                eventoSeleccionadoId = null;
                fetchEventos();
            });

            return;
        } else {
            if (tablaCabecera) tablaCabecera.style.display = '';
        }

        // Tabla de lista de eventos
        eventos.forEach(evento => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${evento.id}</td>
                <td>${evento.valorMagnitud}</td>
                <td>${evento.fechaHoraOcurrencia}</td>
                <td>${evento.coordenadaEpicentro}</td>
                <td>${evento.coordenadaHipocentro}</td>
                <td>
                    <button type="button" class="btn btn-primary select-button w-100" data-id="${evento.id}">Seleccionar</button>
                </td>
            `;
            eventosContainer.appendChild(fila);
        });

        // Botones seleccionar
        const selectButtons = document.querySelectorAll('.select-button');
        selectButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                const usuario = sessionStorage.getItem('usuario');
                if (!usuario) {
                    alert('Debe iniciar sesión para realizar esta acción.');
                    window.location.href = '/index.html';
                    return;
                }
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                eventoSeleccionadoId = id;
                // Cambia el estado a "Bloqueado"
                await tomarSeleccionES(id, usuario);
                // Trae el evento actualizado y lo muestra
                await fetchEventoPorId(id);
            });
        });
    }

    // Renderiza las series temporales por estación
    function renderSeriesPorEstacion(seriesPorEstacion) {
        if (!seriesPorEstacion || Object.keys(seriesPorEstacion).length === 0) {
            return `<div class="text-center">No hay datos clasificados por estación.</div>`;
        }
        let html = '';
        for (const [estacion, muestras] of Object.entries(seriesPorEstacion)) {
            html += `
                <div class="mb-3 border rounded p-2">
                    <h6 class="mb-2">${estacion}</h6>
                    <table class="table table-sm table-bordered mb-0">
                        <thead>
                            <tr>
                                <th>Instante</th>
                                <th>Velocidad de onda</th>
                                <th>Frecuencia de onda</th>
                                <th>Longitud de onda</th>
                            </tr>
                        </thead>
                        <tbody>
            `;
            muestras.forEach(m => {
                html += `
                    <tr>
                        <td>${m.instante}</td>
                        <td>${m.velocidad_onda ?? '-'}</td>
                        <td>${m.frecuencia_onda ?? '-'}</td>
                        <td>${m.longitud ?? '-'}</td>
                    </tr>
                `;
            });
            html += `</tbody></table></div>`;
        }
        return html;
    }

    // Renderiza las series temporales y sus datos anidados
    function renderSeriesTemporales(series) {
        if (!series || series.length === 0) {
            return `<div class="text-center">No hay series temporales.</div>`;
        }
        let html = '';
        series.forEach((serie, idx) => {
            html += `
                <div class="mb-4 border rounded p-2">
                    <h6>Serie Temporal #${idx + 1} (ID: ${serie.id})</h6>
                    <table class="table table-sm table-bordered mb-2">
                        <tr><th>Fecha Inicio Registro</th><td>${serie.fechaHoraInicioRegistroMuestras}</td></tr>
                        <tr><th>Fecha Inicio</th><td>${serie.fechaHoraInicio}</td></tr>
                        <tr><th>Frecuencia Muestreo</th><td>${serie.frecuenciaMuestreo}</td></tr>
                        <tr><th>Sismógrafo</th><td>${serie.datosSismografo?.identificadorSismografo || '-'}</td></tr>
                        <tr><th>Estación</th><td>
                            ${serie.datosSismografo?.estacion ? 
                                `(${serie.datosSismografo.estacion.codigoEstacion}) ${serie.datosSismografo.estacion.nombre}` : '-'}
                        </td></tr>
                    </table>
                    <div>
                        <strong>Muestras Sísmicas:</strong>
                        ${renderMuestrasSismicas(serie.datosMuestrasSismicas)}
                    </div>
                </div>
            `;
        });
        return html;
    }

    // Renderiza las muestras sísmicas y sus detalles
    function renderMuestrasSismicas(muestras) {
        if (!muestras || muestras.length === 0) {
            return `<div class="text-center">No hay muestras sísmicas.</div>`;
        }
        let html = '';
        muestras.forEach((muestra, idx) => {
            html += `
                <div class="mb-2 border rounded p-2">
                    <div><strong>Muestra #${idx + 1} (ID: ${muestra.id})</strong></div>
                    <div>Fecha/Hora: ${muestra.fechaHoraMuestra}</div>
                    <div>
                        <strong>Detalles:</strong>
                        ${renderDetallesMuestra(muestra.detalles)}
                    </div>
                </div>
            `;
        });
        return html;
    }

    // Renderiza los detalles de una muestra sísmica
    function renderDetallesMuestra(detalles) {
        if (!detalles || detalles.length === 0) {
            return `<div class="text-center">No hay detalles.</div>`;
        }
        let html = `
            <table class="table table-sm table-bordered mb-0">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Nombre</th>
                        <th>Valor</th>
                        <th>Tipo de Dato</th>
                    </tr>
                </thead>
                <tbody>
        `;
        detalles.forEach(detalle => {
            html += `
                <tr>
                    <td>${detalle.id}</td>
                    <td>${detalle.nombre || '-'}</td>
                    <td>${detalle.valor}</td>
                    <td>${detalle.tipoDeDato || '-'}</td>
                </tr>
            `;
        });
        html += `</tbody></table>`;
        return html;
    }

    // Trae todos los eventos
    async function fetchEventos() {
        if (eventoSeleccionadoId) {
            await fetchEventoPorId(eventoSeleccionadoId);
            return;
        }
        try {
            const response = await fetch(`${API_URL}/eventos`);
            if (!response.ok) {
                throw new Error('Error al obtener los eventos');
            }
            const eventos = await response.json();
            renderEventos(eventos);
        } catch (error) {
            console.error('Error al cargar los eventos:', error);
        }
    }

    // Trae un evento por ID
    async function fetchEventoPorId(id) {
        try {
            const response = await fetch(`${API_URL}/evento/${id}`);
            if (!response.ok) {
                throw new Error('Evento no encontrado');
            }
            const evento = await response.json();
            renderEventos([evento]);
        } catch (error) {
            // Si no existe, limpiar selección y recargar lista normal
            eventoSeleccionadoId = null;
            fetchEventos();
        }
    }

    // Cambia el estado del evento a un nuevo estado
    async function tomarSeleccionOpc(id, usuario, opcion) {
        try {
            const response = await fetch(`${API_URL}/evento/${id}/opcion/${opcion}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ usuario })
            });
            if (!response.ok) {
                throw new Error('No se pudo cambiar el estado');
            }
        } catch (error) {
            console.error('Error al cambiar el estado:', error);
        }
    }
    
    async function tomarSeleccionES(id, usuario) {
        try {
            const response = await fetch(`${API_URL}/evento/${id}/seleccionar`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ usuario })
            });
            if (!response.ok) {
                throw new Error('No se pudo cambiar el estado');
            }
        } catch (error) {
            console.error('Error al cambiar el estado:', error);
        }
    }

    // Carga inicial
    fetchEventos();

});