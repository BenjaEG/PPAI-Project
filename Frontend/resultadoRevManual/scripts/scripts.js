document.addEventListener('DOMContentLoaded', () => {

    const API_URL = 'http://localhost:5000'; // Ejemplo: 'http://localhost:3000/api/libros'


    async function fetchEventos() {
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

    
    fetchEventos(); // Carga inicial sin término de búsqueda

    function renderEventos(eventos) {
        const eventosContainer = document.getElementById('eventosContainer');
        eventosContainer.innerHTML = ''; // Limpiar el contenedor antes de renderizar
    
        if (eventos.length === 0) {
            eventosContainer.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">No se encontraron eventos.</td>
                </tr>
            `;
            return;
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
                    <button class="btn btn-danger btn-sm delete-button" data-id="${evento.Id}">Eliminar</button>
                </td>
            `;
            eventosContainer.appendChild(fila);
        });
    
        // Agregar eventos a los botones de eliminar
        const deleteButtons = document.querySelectorAll('.delete-button');
        deleteButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                const id = event.target.getAttribute('data-id');
                await deleteEvento(id);
            });
        });
    }

    async function deleteEvento(id) {
        try {
            const confirmDelete = confirm('¿Estás seguro de que deseas eliminar este Evento?'); // Mostrar advertencia
            if (!confirmDelete) {
                return; // Cancelar la eliminación si el usuario selecciona "Cancelar"
            }
    
            const response = await fetch(`${API_URL}/${id}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error('Error al eliminar el evento');
            }
            await fetchLibros(); // Recargar la lista de libros después de eliminar
        } catch (error) {
            console.error('Error al eliminar el evento:', error);
        }
    }
});