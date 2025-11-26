
/* -- SCRIPTS --------------------------------------------------------------- */

/** Función para el cambio de tema */
function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';

    // Aplica el nuevo tema:
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
};

const themeButton = document.getElementById('theme-toggle')
if (themeButton) {// Permite el uso del cambio de tema. 
    themeButton.addEventListener('click', toggleTheme);
};

/* -------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {

    /** Comportamiento del tema */
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);


    /** Comportamiento del SIDEBAR */
    const sidebarButton = document.getElementById('toggle-main-sidebar');
    const sidebarContainer = document.querySelector('.main-sidebar-container');

    if (sidebarButton && sidebarContainer) {
        sidebarButton.addEventListener('click', () => {
            sidebarContainer.classList.toggle('is-open');
        });
    };


    /** Comportamiento del menú de notificaciones */
    const toggleNotifications = document.getElementById('toggle-notifications');
    const notificationsMenu = document.getElementById('notifications-menu');

    toggleNotifications.addEventListener('click', (event) => {
        event.stopPropagation(); // Detiene la propagación del evento.
        notificationsMenu.style.display = notificationsMenu.style.display === 'block' ? 'none' : 'block';
    });

    // Cierre del menú (al hacer clic en cualquier parte del template.)
    document.addEventListener('click', (event) => {
        if (notificationsMenu.style.display === 'block') {
            const isClickInsideMenu = notificationsMenu.contains(event.target);

            if (!isClickInsideMenu) {
                notificationsMenu.style.display = 'none';
            }
        }
    });


    /** Comportamiento de los mensajes de DJANGO */
    const messages = document.querySelectorAll('.django-messages .message');
    const displayTime = 6000; // Seis segundos.
    const transitionTime = 500; // Medio segundo (BASE.CSS)

    messages.forEach(message => {
        message.classList.add('fade-in'); // Animación de entrada.
        setTimeout(() => {
            message.classList.remove('fade-in');
            message.classList.add('show');
        }, 10);

        setTimeout(() => { // Tiempo en pantalla.
            message.classList.remove('show');
            message.classList.add('fade-out');

            setTimeout(() => {
                message.remove();

                const container = document.querySelector('.django-messages');
                if (container && container.children.length === 0) {
                    container.style.display = 'none';
                }

            }, transitionTime); // Medio segundo.

        }, displayTime); // Seis segundos.
    });

});

/* -------------------------------------------------------------------------- */