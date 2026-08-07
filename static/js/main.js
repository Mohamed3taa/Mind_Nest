// ============================
// Mind Nest — Main JavaScript
// ============================

document.addEventListener('DOMContentLoaded', function () {

    // ---- Dark Mode ----
    const html         = document.documentElement;
    const darkBtn      = document.getElementById('darkModeToggle');
    const darkIcon     = document.getElementById('darkModeIcon');
    const savedTheme   = localStorage.getItem('theme') || 'light';

    html.setAttribute('data-bs-theme', savedTheme);
    updateDarkIcon(savedTheme);

    if (darkBtn) {
        darkBtn.addEventListener('click', function () {
            const current = html.getAttribute('data-bs-theme');
            const next    = current === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('theme', next);
            updateDarkIcon(next);
        });
    }

    function updateDarkIcon(theme) {
        if (!darkIcon) return;
        darkIcon.className = theme === 'dark' ? 'bi bi-sun' : 'bi bi-moon-stars';
    }

    // ---- Sidebar Toggle ----
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar       = document.getElementById('sidebar');

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('open');
            } else {
                sidebar.classList.toggle('collapsed');
            }
        });
    }

    // ---- Auto-dismiss alerts after 4s ----
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });

    // ---- Active sidebar link ----
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(function (link) {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });

});
