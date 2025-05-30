const PantallaRegistroResultadoRevisionManual = {
    API_URL: 'http://localhost:5000',
    eventoSeleccionadoId: null,

    iniciar() {
        document.addEventListener('DOMContentLoaded', () => {
            this.mostrarEventosPendientes();
        });
    },

    async mostrarEventosPendientes() {
        try {
            const response = await fetch(`${this.API_URL}/eventos`);
            if (!response.ok) throw new Error('Error al obtener los eventos');
            const eventos = await response.json();
            this.mostrarListaEventos(eventos);
        } catch (error) {
            this.mostrarError('Error al cargar los eventos.');
        }
    },

    mostrarListaEventos(eventos) {
        const eventosContainer = document.getElementById('eventosContainer');
        const tablaCabecera = document.getElementById('tablaCabecera');
        eventosContainer.innerHTML = '';

        if (eventos.length === 0) {
            eventosContainer.innerHTML = `
                <tr>
                    <td colspan="6" class="text-center">No se encontraron eventos.</td>
                </tr>
            `;
            if (tablaCabecera) tablaCabecera.style.display = '';
            return;
        }

        if (tablaCabecera) tablaCabecera.style.display = '';

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

        document.querySelectorAll('.select-button').forEach(button => {
            button.addEventListener('click', (event) => {
                const usuario = sessionStorage.getItem('usuario');
                if (!usuario) {
                    alert('Debe iniciar sesión para realizar esta acción.');
                    window.location.href = '/index.html';
                    return;
                }
                const id = event.target.getAttribute('data-id');
                this.tomarSeleccionEvento(id, usuario);
            });
        });
    },

    async tomarSeleccionEvento(id, usuario) {
        try {
            await this.solicitarBloqueoEvento(id, usuario);
            this.eventoSeleccionadoId = id;
            await this.mostrarDatosBasicosEvento(id);
        } catch (error) {
            this.mostrarError('No se pudo seleccionar el evento.');
        }
    },

    async solicitarBloqueoEvento(id, usuario) {
        const response = await fetch(`${this.API_URL}/evento/${id}/seleccionar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario })
        });
        if (!response.ok) throw new Error('No se pudo bloquear el evento');
    },

    async mostrarDatosBasicosEvento(id) {
        try {
            const response = await fetch(`${this.API_URL}/evento/${id}`);
            if (!response.ok) throw new Error('Evento no encontrado');
            const evento = await response.json();
            this.mostrarPrimerModal(evento);
        } catch (error) {
            this.eventoSeleccionadoId = null;
            this.mostrarEventosPendientes();
        }
    },

    mostrarPrimerModal(evento) {
        const modalBody = document.getElementById('eventoModalBody');
        modalBody.innerHTML = `
            <div class="text-center">
                <p>¿Desea visualizar un mapa sísmico y las estaciones involucradas?</p>
                <button type="button" class="btn btn-primary me-2" id="siMapaBtn">Sí</button>
                <button type="button" class="btn btn-secondary" id="noMapaBtn">No</button>
            </div>
        `;
        const eventoModalEl = document.getElementById('eventoModal');
        const eventoModal = new bootstrap.Modal(eventoModalEl);
        eventoModal.show();

        document.getElementById('siMapaBtn').onclick = () => {
            // No hace nada
        };
        document.getElementById('noMapaBtn').onclick = () => {
            eventoModal.hide();
            setTimeout(() => this.mostrarSegundoModal(evento), 300);
        };
    },

    mostrarSegundoModal(evento) {
        const modalBody = document.getElementById('eventoModalBody');
        modalBody.innerHTML = `
            <div class="text-center">
                <p>¿Desea modificar los datos del evento sísmico?</p>
                <button type="button" class="btn btn-primary me-2" id="siModificarBtn">Sí</button>
                <button type="button" class="btn btn-secondary" id="noModificarBtn">No</button>
            </div>
        `;
        const eventoModalEl = document.getElementById('eventoModal');
        const eventoModal = new bootstrap.Modal(eventoModalEl);
        eventoModal.show();

        document.getElementById('siModificarBtn').onclick = () => {
            // No hace nada
        };
        document.getElementById('noModificarBtn').onclick = () => {
            eventoModal.hide();
            setTimeout(() => this.renderDatosBasicosEvento(evento), 300);
        };
    },

    renderDatosBasicosEvento(evento) {
        const modalBody = document.getElementById('eventoModalBody');
        modalBody.innerHTML = `
            <table class="table table-bordered w-auto mx-auto mb-4">
                <tr><th>ID</th><td>${evento.id}</td></tr>
                <tr><th>Magnitud</th><td>${evento.valorMagnitud}</td></tr>
                <tr><th>Fecha/Hora</th><td>${evento.fechaHoraOcurrencia}</td></tr>
                <tr><th>Localización</th><td>${evento.coordenadaEpicentro}</td></tr>
            </table>
            <div class="text-center mt-3">
                <button type="button" class="btn btn-success me-2" id="confirmarBtn">Confirmar</button>
                <button type="button" class="btn btn-danger me-2" id="rechazarBtn">Rechazar</button>
                <button type="button" class="btn btn-warning me-2" id="solicitarRevisionBtn">Solicitar Revisión</button>
            </div>
        `;

        const eventoModalEl = document.getElementById('eventoModal');
        const eventoModal = new bootstrap.Modal(eventoModalEl);
        eventoModal.show();

        document.getElementById('confirmarBtn').onclick = async () => {
            await this.tomarOpcionEvento(evento.id, "confirmar");
            eventoModal.hide();
        };
        document.getElementById('rechazarBtn').onclick = async () => {
            await this.tomarOpcionEvento(evento.id, "rechazar");
            eventoModal.hide();
        };
        document.getElementById('solicitarRevisionBtn').onclick = async () => {
            await this.tomarOpcionEvento(evento.id, "solicitar revision");
            eventoModal.hide();
        };
    },

    async tomarOpcionEvento(id, opcion) {
        const usuario = sessionStorage.getItem('usuario');
        if (!usuario) {
            alert('Debe iniciar sesión para realizar esta acción.');
            window.location.href = '/index.html';
            return;
        }
        try {
            await fetch(`${this.API_URL}/evento/${id}/opcion/${opcion}`, {
                method: 'PUT',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ usuario })
            });
            this.eventoSeleccionadoId = null;
            this.mostrarEventosPendientes();
        } catch (error) {
            this.mostrarError('No se pudo cambiar el estado del evento.');
        }
    },

    mostrarError(msg) {
        alert(msg);
    }
};

// Inicializar la pantalla
PantallaRegistroResultadoRevisionManual.iniciar();