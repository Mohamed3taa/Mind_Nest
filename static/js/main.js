// ============================
// Mind Nest — Main JavaScript
// ============================

document.addEventListener('DOMContentLoaded', function () {

    // ---- Dark Mode ----
    const html       = document.documentElement;
    const darkBtn    = document.getElementById('darkModeToggle');
    const darkIcon   = document.getElementById('darkModeIcon');
    const savedTheme = localStorage.getItem('theme') || 'light';

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

    // Add overlay element
    let overlay = document.getElementById('sidebarOverlay');
    if (!overlay && sidebar) {
        overlay = document.createElement('div');
        overlay.id = 'sidebarOverlay';
        document.body.appendChild(overlay);
    }

    if (sidebarToggle && sidebar) {
        sidebarToggle.addEventListener('click', function () {
            if (window.innerWidth <= 768) {
                sidebar.classList.toggle('open');
                overlay.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                document.getElementById('page-content').style.marginLeft =
                    sidebar.classList.contains('collapsed') ? '0' : '';
            }
        });
    }

    // Close sidebar on overlay click (mobile)
    if (overlay) {
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        });
    }

    // ---- Auto-dismiss alerts after 4s ----
    document.querySelectorAll('.alert').forEach(function (alert) {
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            bsAlert.close();
        }, 4000);
    });

    // ---- Active sidebar link ----
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && currentPath.startsWith(href) && href !== '/') {
            link.classList.add('active');
        }
    });

});
