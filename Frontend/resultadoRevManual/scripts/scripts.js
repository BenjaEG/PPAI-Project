document.addEventListener('DOMContentLoaded', () => {

    const API_URL = 'http://localhost:3000/api/libros'; // Ejemplo: 'http://localhost:3000/api/libros'


    async function fetchLibros(searchTerm = '') {
        try {
            const response = await fetch(`${API_URL}?search=${encodeURIComponent(searchTerm)}`);
            if (!response.ok) {
                throw new Error('Error al obtener los libros');
            }
            const libros = await response.json();
            renderLibros(libros);
        } catch (error) {
            console.error('Error al cargar los libros:', error);
        }
    }

    
    fetchLibros(); // Carga inicial sin término de búsqueda

    function renderLibros(libros) {
        const librosContainer = document.getElementById('librosContainer');
        librosContainer.innerHTML = ''; // Limpiar el contenedor antes de renderizar
    
        if (libros.length === 0) {
            librosContainer.innerHTML = `
                <tr>
                    <td colspan="5" class="text-center">No se encontraron libros.</td>
                </tr>
            `;
            return;
        }
    
        libros.forEach(libro => {
            const fila = document.createElement('tr');
            fila.innerHTML = `
                <td>${libro.IdLibro}</td>
                <td>${libro.Titulo}</td>
                <td>${libro.Autor}</td>
                <td>${libro.AnioPublicacion}</td>
                <td>
                    <button class="btn btn-danger btn-sm delete-button" data-id="${libro.IdLibro}">Eliminar</button>
                </td>
            `;
            librosContainer.appendChild(fila);
        });
    
        // Agregar eventos a los botones de eliminar
        const deleteButtons = document.querySelectorAll('.delete-button');
        deleteButtons.forEach(button => {
            button.addEventListener('click', async (event) => {
                const id = event.target.getAttribute('data-id');
                await deleteLibro(id);
            });
        });
    }

    async function deleteLibro(id) {
        try {
            const confirmDelete = confirm('¿Estás seguro de que deseas eliminar este libro?'); // Mostrar advertencia
            if (!confirmDelete) {
                return; // Cancelar la eliminación si el usuario selecciona "Cancelar"
            }
    
            const response = await fetch(`${API_URL}/${id}`, {
                method: 'DELETE'
            });
            if (!response.ok) {
                throw new Error('Error al eliminar el libro');
            }
            await fetchLibros(); // Recargar la lista de libros después de eliminar
        } catch (error) {
            console.error('Error al eliminar el libro:', error);
        }
    }

    async function searchLibros() {
        const searchInput = document.getElementById('searchInput'); // Obtener el input de búsqueda
        const searchTerm = searchInput.value.trim(); // Obtener el valor del input
        await fetchLibros(searchTerm); // Pasar el término de búsqueda a la función de carga
    }

    // Asociar el botón de búsqueda con la función searchLibros
    const searchButton = document.getElementById('searchButton');
    searchButton.addEventListener('click', searchLibros);

    // Asociar el evento 'keydown' al input de búsqueda para detectar la tecla Enter
    const searchInput = document.getElementById('searchInput');
    searchInput.addEventListener('keydown', (event) => {
    if (event.key === 'Enter') {
        searchLibros(); // Ejecutar la búsqueda al presionar Enter
    }
    });
});