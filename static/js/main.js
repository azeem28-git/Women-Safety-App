/* ===== SAFEHER MAIN JS ===== */

// Sidebar Toggle
function toggleSidebar() {
    const sidebar = document.getElementById('sidebar');
    const wrapper = document.getElementById('mainWrapper');
    if (sidebar) {
        sidebar.classList.toggle('open');
        // Overlay click to close
        if (sidebar.classList.contains('open')) {
            if (!document.getElementById('sidebarOverlay')) {
                const overlay = document.createElement('div');
                overlay.id = 'sidebarOverlay';
                overlay.style.cssText = 'position:fixed;inset:0;background:rgba(0,0,0,0.5);z-index:999;';
                overlay.onclick = closeSidebar;
                document.body.appendChild(overlay);
            }
        } else {
            removeSidebarOverlay();
        }
    }
}

function closeSidebar() {
    const sidebar = document.getElementById('sidebar');
    if (sidebar) sidebar.classList.remove('open');
    removeSidebarOverlay();
}

function removeSidebarOverlay() {
    const overlay = document.getElementById('sidebarOverlay');
    if (overlay) overlay.remove();
}

// Auto-dismiss alerts after 5 seconds
document.addEventListener('DOMContentLoaded', function () {
    const alerts = document.querySelectorAll('.alert.fade.show');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = bootstrap.Alert.getOrCreateInstance(alert);
            if (bsAlert) bsAlert.close();
        }, 5000);
    });

    // Active nav link highlight on mobile
    const currentPath = window.location.pathname;
    document.querySelectorAll('.sidebar-nav .nav-link').forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
});

// Geolocation helper
function getCurrentLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error('Geolocation not supported'));
            return;
        }
        navigator.geolocation.getCurrentPosition(
            pos => resolve({ lat: pos.coords.latitude, lng: pos.coords.longitude }),
            err => reject(err),
            { timeout: 10000, enableHighAccuracy: true }
        );
    });
}

// Format date helper
function formatDate(dateStr) {
    const d = new Date(dateStr);
    return d.toLocaleDateString('en-IN', { day: '2-digit', month: 'short', year: 'numeric' });
}

// Confirm delete helper
function confirmDelete(formId, name) {
    if (confirm(`Are you sure you want to delete "${name}"? This cannot be undone.`)) {
        document.getElementById(formId).submit();
    }
}

// Copy to clipboard
function copyToClipboard(text) {
    navigator.clipboard.writeText(text).then(() => {
        showToast('Copied to clipboard!', 'success');
    }).catch(() => {
        showToast('Failed to copy', 'danger');
    });
}

// Toast notification
function showToast(message, type = 'info') {
    const toast = document.createElement('div');
    toast.className = `alert alert-${type} position-fixed bottom-0 end-0 m-3`;
    toast.style.cssText = 'z-index:9999;min-width:250px;border-radius:12px;box-shadow:0 8px 24px rgba(0,0,0,0.15);';
    toast.innerHTML = message;
    document.body.appendChild(toast);
    setTimeout(() => toast.remove(), 3000);
}

// Share location via Web Share API
async function shareLocation() {
    try {
        const loc = await getCurrentLocation();
        const url = `https://www.google.com/maps?q=${loc.lat},${loc.lng}`;
        if (navigator.share) {
            await navigator.share({
                title: 'My Current Location',
                text: 'Here is my current location — SafeHer',
                url
            });
        } else {
            copyToClipboard(url);
        }
    } catch (e) {
        showToast('Could not get location', 'warning');
    }
}
