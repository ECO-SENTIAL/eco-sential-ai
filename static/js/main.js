/**
 * EcoSentinel – Main JavaScript
 * Real-time alerts, toast notifications, counter animations, sidebar toggle
 */

// ===== SIDEBAR TOGGLE =====
const sidebar = document.getElementById('sidebar');
const toggleBtn = document.getElementById('sidebar-toggle');
if (toggleBtn) {
    toggleBtn.addEventListener('click', () => sidebar.classList.toggle('open'));
    document.addEventListener('click', e => {
        if (window.innerWidth < 993 && !sidebar.contains(e.target) && !toggleBtn.contains(e.target)) {
            sidebar.classList.remove('open');
        }
    });
}

// ===== COUNTER ANIMATION =====
function animateCounter(el, target, duration = 1800) {
    if (!el) return;
    let start = 0;
    const step = target / (duration / 16);
    const timer = setInterval(() => {
        start = Math.min(start + Math.ceil(step), target);
        el.textContent = start.toLocaleString();
        if (start >= target) clearInterval(timer);
    }, 16);
}

// ===== TOAST NOTIFICATION =====
const toastContainer = document.getElementById('toast-container');
function showToast(title, message, type = 'info', duration = 4500) {
    if (!toastContainer) return;
    const icons = { success: 'bi-check-circle-fill', error: 'bi-x-circle-fill', warning: 'bi-exclamation-triangle-fill', info: 'bi-info-circle-fill' };
    const colors = { success: '#2ecc71', error: '#ff4444', warning: '#ffa500', info: '#3498db' };
    const toast = document.createElement('div');
    toast.className = 'eco-toast';
    toast.style.borderLeftColor = colors[type] || colors.info;
    toast.style.borderLeftWidth = '3px';
    toast.innerHTML = `
        <div class="toast-icon" style="color:${colors[type]};"><i class="bi ${icons[type]}"></i></div>
        <div><div class="toast-title">${title}</div><div class="toast-msg">${message}</div></div>
        <button onclick="this.parentElement.remove()" style="background:none;border:none;color:#8b949e;margin-left:auto;cursor:pointer;font-size:1.1rem;">&times;</button>
    `;
    toastContainer.appendChild(toast);
    setTimeout(() => {
        toast.style.animation = 'toast-in 0.35s ease reverse';
        setTimeout(() => toast.remove(), 300);
    }, duration);
}

// ===== REAL-TIME DETECTION POLLING =====
let lastDetectionId = null;
let pollInterval = null;

function startPolling() {
    pollInterval = setInterval(async () => {
        try {
            const res = await fetch('/api/detections/');
            const data = await res.json();
            if (data.detections && data.detections.length > 0) {
                const latest = data.detections[0];
                if (lastDetectionId !== null && latest.id !== lastDetectionId) {
                    // New detection!
                    const badge = document.getElementById('alert-badge');
                    const bellDot = document.getElementById('bell-dot');
                    if (badge) { badge.classList.add('show'); }
                    if (bellDot) { bellDot.classList.add('show'); }
                    const severityEmoji = {critical:'🚨', high:'⚠️', medium:'🟡', low:'🟢'};
                    showToast(
                        `${severityEmoji[latest.severity] || '🦁'} ${latest.animal} Detected!`,
                        `${latest.location} – Confidence: ${latest.confidence}%`,
                        latest.severity === 'critical' || latest.severity === 'high' ? 'warning' : 'info',
                        6000
                    );
                }
                lastDetectionId = latest.id;
            }
        } catch (e) {}
    }, 15000); // Poll every 15 seconds
}

// Alert bell click
const alertBell = document.getElementById('alert-bell');
if (alertBell) {
    alertBell.addEventListener('click', () => {
        const badge = document.getElementById('alert-badge');
        const bellDot = document.getElementById('bell-dot');
        if (badge) badge.classList.remove('show');
        if (bellDot) bellDot.classList.remove('show');
        window.location.href = '/dashboard/';
    });
}

// Start polling on all pages
document.addEventListener('DOMContentLoaded', () => {
    startPolling();
    // Initialize lastDetectionId from current data
    fetch('/api/detections/').then(r => r.json()).then(data => {
        if (data.detections && data.detections.length > 0) {
            lastDetectionId = data.detections[0].id;
        }
    }).catch(() => {});
});

// ===== CONFIDENCE BAR ANIMATION =====
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.conf-fill').forEach(bar => {
        const target = bar.style.width;
        bar.style.width = '0%';
        setTimeout(() => { bar.style.width = target; }, 200);
    });
});

// ===== FORM VALIDATION HELPERS =====
function validateImageUpload(input) {
    const allowed = ['image/jpeg', 'image/png', 'image/bmp', 'image/webp'];
    if (input.files[0] && !allowed.includes(input.files[0].type)) {
        showToast('Invalid File', 'Please upload a JPG, PNG, or BMP image.', 'error');
        input.value = '';
        return false;
    }
    return true;
}

// ===== MAP TABLE ROW HOVER =====
document.addEventListener('DOMContentLoaded', () => {
    document.querySelectorAll('.eco-table tbody tr').forEach(row => {
        row.style.cursor = 'default';
    });
});
