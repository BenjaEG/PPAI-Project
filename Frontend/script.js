document.addEventListener('DOMContentLoaded', function() {
    const loginForm = document.getElementById('loginForm');
    const loginError = document.getElementById('loginError');

    loginForm.addEventListener('submit', function(e) {
        e.preventDefault();
        const usuario = document.getElementById('usuario').value.trim();
        if(usuario.length === 0) {
            loginError.classList.remove('d-none');
            return;
        }
        sessionStorage.setItem('usuario', usuario);
        window.location.href = 'menu/index.html';
    });
});