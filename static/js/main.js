// ============================
// Mind Nest — Main JavaScript
// ============================

document.addEventListener('DOMContentLoaded', function () {

    // ── Move all modals to <body> ─────────────────────────────
    // Bootstrap modals must be direct children of <body> to stack
    // correctly above the backdrop (z-index: 1050 vs 1055).
    // Any modal nested inside #wrapper would appear behind its own backdrop.
    function moveModalsToBody() {
        document.querySelectorAll('.modal').forEach(function (modal) {
            if (modal.parentElement !== document.body) {
                document.body.appendChild(modal);
            }
        });
    }
    moveModalsToBody();

    // Also catch any modals added dynamically after page load
    new MutationObserver(moveModalsToBody).observe(
        document.body,
        { childList: true, subtree: true }
    );

    // ── Dark Mode ────────────────────────────────────────────
    const html       = document.documentElement;
    const darkBtn    = document.getElementById('darkModeToggle');
    const darkIcon   = document.getElementById('darkModeIcon');
    const savedTheme = localStorage.getItem('mn-theme') || 'light';

    html.setAttribute('data-bs-theme', savedTheme);
    updateDarkIcon(savedTheme);

    if (darkBtn) {
        darkBtn.addEventListener('click', function () {
            const next = html.getAttribute('data-bs-theme') === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-bs-theme', next);
            localStorage.setItem('mn-theme', next);
            updateDarkIcon(next);
        });
    }

    function updateDarkIcon(theme) {
        if (!darkIcon) return;
        darkIcon.className = theme === 'dark' ? 'bi bi-sun-fill' : 'bi bi-moon-stars-fill';
    }

    // ── Sidebar Toggle ───────────────────────────────────────
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebar       = document.getElementById('sidebar');

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
                if (overlay) overlay.classList.toggle('show');
            } else {
                sidebar.classList.toggle('collapsed');
                const pageContent = document.getElementById('page-content');
                if (pageContent) {
                    pageContent.style.marginLeft =
                        sidebar.classList.contains('collapsed') ? '0' : '';
                }
            }
        });
    }

    if (overlay) {
        overlay.addEventListener('click', function () {
            sidebar.classList.remove('open');
            overlay.classList.remove('show');
        });
    }

    // ── Active sidebar link ──────────────────────────────────
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-link').forEach(function (link) {
        const href = link.getAttribute('href');
        if (href && href !== '/' && currentPath.startsWith(href)) {
            link.classList.add('active');
        }
        // Close mobile sidebar on link click
        link.addEventListener('click', function () {
            if (window.innerWidth <= 768 && sidebar) {
                sidebar.classList.remove('open');
                if (overlay) overlay.classList.remove('show');
            }
        });
    });

    // ── Auto-dismiss alerts ──────────────────────────────────
    document.querySelectorAll('.alert').forEach(function (alert) {
        // Don't auto-dismiss error alerts in auth pages
        if (alert.closest('.auth-card')) return;
        setTimeout(function () {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 4500);
    });

    // ── Page entrance animations ─────────────────────────────
    // Animate stat cards with stagger
    const statCards = document.querySelectorAll('.stat-card');
    statCards.forEach(function (card, i) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(20px)';
        requestAnimationFrame(function () {
            setTimeout(function () {
                card.style.transition = 'opacity 0.4s ease, transform 0.4s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 80 + i * 60);
        });
    });

    // Animate cards in grids
    const gridCards = document.querySelectorAll('.note-item, .resource-item, #taskContainer .col-12');
    gridCards.forEach(function (card, i) {
        card.style.opacity = '0';
        card.style.transform = 'translateY(16px)';
        requestAnimationFrame(function () {
            setTimeout(function () {
                card.style.transition = 'opacity 0.35s ease, transform 0.35s ease';
                card.style.opacity = '1';
                card.style.transform = 'translateY(0)';
            }, 50 + i * 40);
        });
    });

    // ── Stat counter animation ───────────────────────────────
    document.querySelectorAll('.stat-value').forEach(function (el) {
        const target = parseInt(el.textContent, 10);
        if (isNaN(target) || target === 0) return;

        el.textContent = '0';
        const duration = 600;
        const start    = performance.now();

        function step(timestamp) {
            const elapsed  = timestamp - start;
            const progress = Math.min(elapsed / duration, 1);
            // ease-out cubic
            const eased    = 1 - Math.pow(1 - progress, 3);
            el.textContent = Math.round(eased * target);
            if (progress < 1) requestAnimationFrame(step);
        }

        setTimeout(function () { requestAnimationFrame(step); }, 200);
    });

    // ── Smooth hover for list-group items ────────────────────
    document.querySelectorAll('.list-group-item').forEach(function (item) {
        item.style.transition = 'padding-left 0.2s ease, background 0.2s ease';
    });

    // ── Button ripple effect ─────────────────────────────────
    document.querySelectorAll('.btn').forEach(function (btn) {
        btn.addEventListener('click', function (e) {
            const ripple    = document.createElement('span');
            const rect      = btn.getBoundingClientRect();
            const size      = Math.max(rect.width, rect.height);
            const x         = e.clientX - rect.left - size / 2;
            const y         = e.clientY - rect.top  - size / 2;

            ripple.style.cssText = `
                position:absolute;
                width:${size}px; height:${size}px;
                left:${x}px; top:${y}px;
                background:rgba(255,255,255,0.25);
                border-radius:50%;
                transform:scale(0);
                animation:ripple 0.45s ease-out forwards;
                pointer-events:none;
            `;

            btn.style.position = 'relative';
            btn.style.overflow = 'hidden';
            btn.appendChild(ripple);
            setTimeout(() => ripple.remove(), 500);
        });
    });

    // Inject ripple keyframe once
    if (!document.getElementById('mn-ripple-style')) {
        const s = document.createElement('style');
        s.id = 'mn-ripple-style';
        s.textContent = '@keyframes ripple { to { transform:scale(2.5); opacity:0; } }';
        document.head.appendChild(s);
    }

    // ── Tooltip init ─────────────────────────────────────────
    document.querySelectorAll('[title]').forEach(function (el) {
        if (el.closest('.sidebar')) return; // skip sidebar items
        if (el.getAttribute('data-bs-toggle')) return; // skip modal/dropdown/tab triggers
        try {
            new bootstrap.Tooltip(el, { trigger: 'hover', delay: { show: 400, hide: 100 } });
        } catch (_) {}
    });

});
