
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

});

/* -------------------------------------------------------------------------- */