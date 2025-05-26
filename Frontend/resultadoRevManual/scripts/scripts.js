let eventoSeleccionadoId = null;

document.addEventListener('DOMContentLoaded', () => {

    const API_URL = 'http://localhost:5000';

    // Renderiza la tabla de eventos
    function renderEventos(eventos) {
        const eventosContainer = document.getElementById('eventosContainer');
        const tablaCabecera = document.getElementById('tablaCabecera');
        eventosContainer.innerHTML = '';

        if (eventos.length === 0) {
            eventosContainer.innerHTML = `
                <tr>
                    <td colspan="7" class="text-center">No se encontraron eventos.</td>
                </tr>
            `;
            if (tablaCabecera) tablaCabecera.style.display = '';
            return;
        }

        // Si hay solo uno y está seleccionado, mostrar todos los datos (sin revision)
        if (eventos.length === 1 && eventoSeleccionadoId == eventos[0].id) {
            const evento = eventos[0];
            if (tablaCabecera) tablaCabecera.style.display = 'none';
            eventosContainer.innerHTML = `
                <tr>
                    <td colspan="2" class="text-center">
                        <table class="table table-bordered w-auto mx-auto">
                            <tr><th>ID</th><td>${evento.id}</td></tr>
                            <tr><th>Magnitud</th><td>${evento.valorMagnitud}</td></tr>
                            <tr><th>Fecha Fin</th><td>${evento.fechaHoraFin}</td></tr>
                            <tr><th>Fecha Ocurrencia</th><td>${evento.fechaHoraOcurrencia}</td></tr>
                            <tr><th>Coordenada Epicentro</th><td>${evento.coordenadaEpicentro}</td></tr>
                            <tr><th>Coordenada Hipocentro</th><td>${evento.coordenadaHipocentro}</td></tr>
                            <tr><th>Alcance</th><td>${evento.alcance || evento.alcance_id}</td></tr>
                            <tr><th>Origen de Generación</th><td>${evento.origen_de_generacion || evento.origen_de_generacion_id}</td></tr>
                            <tr><th>Clasificación Sismo</th><td>${evento.clasificacion_sismo || evento.clasificacion_sismo_id}</td></tr>
                            <tr>
                                <td colspan="2" class="text-center">
                                    <button type="button" class="btn btn-primary btn-confirmar" data-id="${evento.id}">Confirmar</button>
                                    <button type="button" class="btn btn-danger btn-rechazar" data-id="${evento.id}">Rechazar</button>
                                    <button type="button" class="btn btn-warning btn-solicitar" data-id="${evento.id}">Solicitar Revision Experto</button>
                                </td>
                            </tr>
                        </table>
                    </td>
                </tr>
            `;
            // Reasignar listeners a los botones
            document.querySelector('.btn-confirmar').addEventListener('click', async (event) => {
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                await cambiarEstadoEvento(id, "Confirmado");
                eventoSeleccionadoId = null;
                await fetchEventos();
            });
            document.querySelector('.btn-rechazar').addEventListener('click', async (event) => {
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                await cambiarEstadoEvento(id, "Rechazado");
                eventoSeleccionadoId = null;
                await fetchEventos();
            });
            document.querySelector('.btn-solicitar').addEventListener('click', async (event) => {
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                await cambiarEstadoEvento(id, "Derivado");
                eventoSeleccionadoId = null;
                await fetchEventos();
            });
            return;
        } else {
            if (tablaCabecera) tablaCabecera.style.display = '';
        }

        eventos.forEach(evento => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${evento.id}</td>
                <td>${evento.valorMagnitud}</td>
                <td>${evento.fechaHoraFin}</td>
                <td>${evento.fechaHoraOcurrencia}</td>
                <td>${evento.coordenadaEpicentro}</td>
                <td>${evento.coordenadaHipocentro}</td>
                <td>
                    ${
                        eventoSeleccionadoId == evento.id
                        ? `
                            <button type="button" class="btn btn-primary btn-confirmar" data-id="${evento.id}">Confirmar</button>
                            <button type="button" class="btn btn-danger btn-rechazar" data-id="${evento.id}">Rechazar</button>
                            <button type="button" class="btn btn-warning btn-solicitar" data-id="${evento.id}">Solicitar Revision Experto</button>
                        `
                        : `<button type="button" class="btn btn-primary select-button" data-id="${evento.id}">Seleccionar</button>`
                    }
                </td>
            `;
            eventosContainer.appendChild(fila);
        });

        // Botones seleccionar
        const selectButtons = document.querySelectorAll('.select-button');
        selectButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                eventoSeleccionadoId = id;
                // Cambia el estado a "Bloqueado"
                await cambiarEstadoEvento(id, "Bloqueado");
                // Trae el evento actualizado y lo muestra
                await fetchEventoPorId(id);
            });
        });
        // Botón Confirmar (azul)
        const confirmarButtons = document.querySelectorAll('.btn-confirmar');
        confirmarButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                await cambiarEstadoEvento(id, "Confirmado");
                eventoSeleccionadoId = null; // Limpiar selección
                await fetchEventos();        // Mostrar todos
            });
        });

        // Botón Rechazar (rojo)
        const rechazarButtons = document.querySelectorAll('.btn-rechazar');
        rechazarButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                await cambiarEstadoEvento(id, "Rechazado");
                eventoSeleccionadoId = null; // Limpiar selección
                await fetchEventos();        // Mostrar todos
            });
        });

        // Botón Solicitar (amarillo)
        const solicitarButtons = document.querySelectorAll('.btn-solicitar');
        solicitarButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                event.preventDefault();
                const id = event.target.getAttribute('data-id');
                await cambiarEstadoEvento(id, "Derivado");
                eventoSeleccionadoId = null; // Limpiar selección
                await fetchEventos();        // Mostrar todos
            });
        });
    }

    // Trae todos los eventos o el seleccionado si corresponde
    async function fetchEventos() {
        if (eventoSeleccionadoId) {
            await fetchEventoPorId(eventoSeleccionadoId);
            return;
        }
        try {
            const response = await fetch(`${API_URL}/eventos?estado=Pendiente Revision`);
            if (!response.ok) {
                throw new Error('Error al obtener los eventos');
            }
            const eventos = await response.json();
            renderEventos(eventos);
        } catch (error) {
            console.error('Error al cargar los eventos:', error);
        }
    }

    // Trae un evento por ID (aunque cambie de estado)
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
    async function cambiarEstadoEvento(id, nuevoEstado) {
        try {
            const response = await fetch(`${API_URL}/evento/${id}/cambiar-estado/${encodeURIComponent(nuevoEstado)}`, {
                method: 'PUT'
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