class InterfazRRM {
    constructor(apiUrl) {
        this.apiUrl = apiUrl;
        this.eventosContainer = document.getElementById('eventosContainer');
        this.noEventosMsg = document.querySelector('#eventosListContainer p');
        this.init();
    }

    async init() {
        await this.mostrarEventos();
    }

    // Métodos de comunicación con la API
    async getEventos() {
        const response = await fetch(`${this.apiUrl}/eventos`);
        if (!response.ok) throw new Error('Error al obtener eventos');
        return await response.json();
    }

     async tomarSeleccionES(id, usuario) {
        try {
            const response = await fetch(`${this.apiUrl}/evento/${id}/seleccionar`, {
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

    async getEventoPorId(id) {
    const response = await fetch(`${this.apiUrl}/evento/${id}`);
    const text = await response.text();
    if (!response.ok) throw new Error('Evento no encontrado');
    const data = JSON.parse(text);
    return data;
}
    async tomarSeleccionOpc(id, usuario) {
        const response = await fetch(`${this.apiUrl}/evento/${id}/rechazar`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ usuario })
        });
        if (!response.ok) throw new Error('No se pudo cambiar el estado');
        return await response.json();
    }

    // Métodos de UI
    async mostrarEventos() {
        try {
            const eventos = await this.getEventos();
            this.renderTabla(eventos);
        } catch (e) {
            this.eventosContainer.innerHTML = `<tr><td colspan="6">Error al cargar eventos</td></tr>`;
        }
    }

    renderTabla(eventos) {
        if (!eventos.length) {
            this.eventosContainer.innerHTML = '';
            this.noEventosMsg.style.display = 'block';
            return;
        }
        this.noEventosMsg.style.display = 'none';
        this.eventosContainer.innerHTML = eventos.map(evento => `
            <tr>
                <td>${evento.id}</td>
                <td>${evento.valorMagnitud}</td>
                <td>${evento.fechaHoraOcurrencia}</td>
                <td>${evento.coordenadaEpicentro}</td>
                <td>${evento.coordenadaHipocentro}</td>
                <td>
                   <button class="btn btn-primary btn-sm select-button" data-id="${evento.id}">Seleccionar</button>
                </td>
            </tr>
    `).join('');
    this.addEventListeners();
    }

    addEventListeners() {
    this.eventosContainer.querySelectorAll('.select-button').forEach(button => {
        button.addEventListener('click', async (event) => {
            const usuario = sessionStorage.getItem('usuario');
            if (!usuario) {
                alert('Debe iniciar sesión para realizar esta acción.');
                window.location.href = '/index.html';
                return;
            }
            event.preventDefault();
            const id = event.target.getAttribute('data-id');
            await this.mostrarDetalle(id);
            await this.tomarSeleccionES(id, usuario);

        });
    });
}
    async mostrarDetalle(id) {
    try {
        const evento = await this.getEventoPorId(id);
        console.log("Evento obtenido:", evento);
        // Construye el HTML del detalle con botones de acción
        const detalleHtml = `
            <ul class="list-group mb-3">
                <li class="list-group-item"><strong>ID:</strong> ${evento.id}</li>
                <li class="list-group-item"><strong>Magnitud:</strong> ${evento.valorMagnitud}</li>
                <li class="list-group-item"><strong>Fecha Ocurrencia:</strong> ${evento.fechaHoraOcurrencia}</li>
                <li class="list-group-item"><strong>Coordenada Epicentro:</strong> ${evento.coordenadaEpicentro}</li>
                <li class="list-group-item"><strong>Coordenada Hipocentro:</strong> ${evento.coordenadaHipocentro}</li>
            </ul>
            <div class="d-flex justify-content-end gap-2">
                <button id="btnRechazar" class="btn btn-danger">Rechazar</button>
                <button id="solicitarRevisionBtn" class="btn btn-warning">Derivar</button>
                <button id="btnConfirmar" class="btn btn-success">Confirmar</button>
            </div>
        `;
        document.getElementById('detalleEventoBody').innerHTML = detalleHtml;

        // Asigna eventos a los botones
        document.getElementById('btnRechazar').addEventListener('click', async () => {
            const usuario = sessionStorage.getItem('usuario');
            if (!usuario) {
                alert('Debe iniciar sesión para realizar esta acción.');
                window.location.href = '/index.html';
                return;
            }
            await this.tomarSeleccionES(evento.id, usuario); // tu función personalizada

            const modal = bootstrap.Modal.getInstance(document.getElementById('detalleEventoModal'));
            modal.hide();
            await this.mostrarEventos();
        });
        document.getElementById('solicitarRevisionBtn').onclick = async () => {

            await this.mostrarEventos();
            const modal = bootstrap.Modal.getInstance(document.getElementById('detalleEventoModal'));
            modal.hide();
        };
        document.getElementById('btnConfirmar').onclick = async () => {

            await this.mostrarEventos();
            const modal = bootstrap.Modal.getInstance(document.getElementById('detalleEventoModal'));
            modal.hide();
        };

        // Muestra el modal (Bootstrap 5)
        const modal = new bootstrap.Modal(document.getElementById('detalleEventoModal'));
        modal.show();
    } catch (e) {
        alert('No se pudo cargar el detalle');
        console.error(e);
    }
}
}

// Inicialización
document.addEventListener('DOMContentLoaded', () => {
    const apiUrl = 'http://localhost:5000'; // Cambia por tu URL real
    new InterfazRRM(apiUrl);
});