
/* -- SCRIPTS --------------------------------------------------------------- */

function toggleTheme() {
    const currentTheme = localStorage.getItem('theme') || 'light';
    const newTheme = currentTheme === 'light' ? 'dark' : 'light';
    document.documentElement.setAttribute('data-theme', newTheme);
    localStorage.setItem('theme', newTheme);
};

const themeButton = document.getElementById('theme-toggle')
if (themeButton) {
    themeButton.addEventListener('click', toggleTheme);
};

/* -------------------------------------------------------------------------- */

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme') || 'light';
    document.documentElement.setAttribute('data-theme', savedTheme);
    const supervisorIdElement = document.querySelector('[data-supervisor-id]');
    if (supervisorIdElement) {
        localStorage.setItem('supervisor_id', supervisorIdElement.getAttribute('data-supervisor-id'));
    }
    const sidebarButton = document.getElementById('toggle-main-sidebar');
    const sidebarContainer = document.querySelector('.main-sidebar-container');

    if (sidebarButton && sidebarContainer) {
        sidebarButton.addEventListener('click', () => {
            sidebarContainer.classList.toggle('is-open');
        });
    };
    const toggleNotifications = document.getElementById('toggle-notifications');
    const notificationsMenu = document.getElementById('notifications-menu');
    const alertsList = document.getElementById('alerts-list');
    const notificationBadge = document.getElementById('notification-badge');
    toggleNotifications.addEventListener('click', (event) => {
        event.stopPropagation();
        notificationsMenu.style.display = notificationsMenu.style.display === 'block' ? 'none' : 'block';
        if (notificationsMenu.style.display === 'block') {
            loadSupervisorAlerts();
        }
    });
    loadSupervisorAlerts();
    async function loadSupervisorAlerts() {
        const supervisorId = getSupervisorId();
        if (!supervisorId) return;

        try {
            const apiBaseUrl = document.body.getAttribute('data-api-url') || 'http://127.0.0.1:8000/api';
            const apiUrl = `${apiBaseUrl}/supervisors/${supervisorId}/alerts/?limit=3`;
            const response = await fetch(apiUrl, {
                method: 'GET',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': getCookie('csrftoken')
                },
                credentials: 'include'
            });

            if (!response.ok) throw new Error('Error al cargar alertas');

            const data = await response.json();
            
            if (data.success && data.alerts && data.alerts.length > 0) {
                displayAlerts(data.alerts);
                updateNotificationBadge(data.alerts_count);
            } else {
                alertsList.innerHTML = '<li class="no-alerts">Sin alertas pendientes</li>';
                updateNotificationBadge(0);
            }
        } catch (error) {
            console.error('Error:', error);
            alertsList.innerHTML = '<li class="error">Error al cargar alertas</li>';
        }
    }
    function displayAlerts(alerts) {
        alertsList.innerHTML = '';
        
        alerts.forEach(alert => {
            const alertElement = document.createElement('li');
            alertElement.className = `alert-item alert-${alert.level.toLowerCase()}`;
            alertElement.innerHTML = `
                <div class='alert-header'>
                    <span class='alert-level'>${alert.level}</span>
                    <span class='alert-time'>${alert.time_ago}</span>
                </div>
                <div class='alert-body'>
                    <strong>${alert.officer_name}</strong> (${alert.officer_badge})
                    <p>${alert.alert_type}</p>
                    <small>${alert.description}</small>
                </div>
            `;
            alertElement.addEventListener('click', () => {
                window.location.href = `/artemis/officers/${alert.officer_id}/`;
            });
            alertsList.appendChild(alertElement);
        });
    }
    function updateNotificationBadge(count) {
        if (count > 0) {
            notificationBadge.style.display = 'block';
        } else {
            notificationBadge.style.display = 'none';
        }
    }

    function getSupervisorId() {
        const supervisorIdElement = document.querySelector('[data-supervisor-id]');
        if (supervisorIdElement) {
            return supervisorIdElement.getAttribute('data-supervisor-id');
        }
        return localStorage.getItem('supervisor_id');
    }

    function getCookie(name) {
        let cookieValue = null;
        if (document.cookie && document.cookie !== '') {
            const cookies = document.cookie.split(';');
            for (let i = 0; i < cookies.length; i++) {
                const cookie = cookies[i].trim();
                if (cookie.substring(0, name.length + 1) === (name + '=')) {
                    cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                    break;
                }
            }
        }
        return cookieValue;
    }
    setInterval(() => {
        if (notificationsMenu.style.display === 'block') {
            loadSupervisorAlerts();
        }
    }, 30000);
    document.addEventListener('click', (event) => {
        if (notificationsMenu.style.display === 'block') {
            const isClickInsideMenu = notificationsMenu.contains(event.target);
            const isClickOnToggle = toggleNotifications.contains(event.target);

            if (!isClickInsideMenu && !isClickOnToggle) {
                notificationsMenu.style.display = 'none';
            }
        }
    });
    const messages = document.querySelectorAll('.django-messages .message');
    const displayTime = 6000;
    const transitionTime = 500;

    messages.forEach(message => {
        message.classList.add('fade-in');
        setTimeout(() => {
            message.classList.remove('fade-in');
            message.classList.add('show');
        }, 10);

        setTimeout(() => {
            message.classList.remove('show');
            message.classList.add('fade-out');

            setTimeout(() => {
                message.remove();

                const container = document.querySelector('.django-messages');
                if (container && container.children.length === 0) {
                    container.style.display = 'none';
                }

            }, transitionTime);

        }, displayTime);
    });

});

/* -------------------------------------------------------------------------- */