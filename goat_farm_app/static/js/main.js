// Notification System for High Weight Goats
function showNotification(tagId, weight, color) {
    const container = document.getElementById('notification-container');
    
    // Create notification element
    const notification = document.createElement('div');
    notification.className = 'goat-notification';
    
    // Determine badge color based on goat color
    const colorClass = getColorBadgeClass(color);
    
    notification.innerHTML = `
        <div class="notification-icon">
            <i class="bi bi-bell-fill"></i>
        </div>
        <div class="notification-content">
            <div class="notification-title">Weight Alert</div>
            <div class="notification-message">
                Goat <strong>${tagId}</strong> reached <strong>${weight} kg</strong>
            </div>
            <div class="notification-color">
                Color: <span class="color-badge ${colorClass}">${color || 'Unknown'}</span>
            </div>
        </div>
        <button class="notification-close" onclick="this.parentElement.remove()">
            <i class="bi bi-x"></i>
        </button>
    `;
    
    container.appendChild(notification);
    
    // Auto-dismiss after 7 seconds
    setTimeout(function() {
        if (notification.parentElement) {
            notification.remove();
        }
    }, 7000);
}

function getColorBadgeClass(color) {
    if (!color) return 'color-unknown';
    
    const colorLower = color.toLowerCase();
    
    if (colorLower.includes('white') || colorLower.includes('blanco')) return 'color-white';
    if (colorLower.includes('black') || colorLower.includes('negro')) return 'color-black';
    if (colorLower.includes('brown') || colorLower.includes('marron')) return 'color-brown';
    if (colorLower.includes('red') || colorLower.includes('rojo')) return 'color-red';
    if (colorLower.includes('gray') || colorLower.includes('grey') || colorLower.includes('gris')) return 'color-gray';
    if (colorLower.includes('spotted') || colorLower.includes('manchado')) return 'color-spotted';
    
    return 'color-unknown';
}

function displayHighWeightGoatNotifications(goats) {
    if (!goats || goats.length === 0) return;
    
    // Display notifications with a delay between each one
    goats.forEach((goat, index) => {
        setTimeout(function() {
            showNotification(goat.tag_no, goat.weight_kg, goat.color);
        }, index * 1500); // 1.5 second delay between notifications
    });
}

// Add any global javascript functionality here
document.addEventListener("DOMContentLoaded", function() {
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(function(alert) {
        setTimeout(function() {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });

    // Add smooth scroll behavior
    document.querySelectorAll('a[href^="#"]').forEach(anchor => {
        anchor.addEventListener('click', function(e) {
            const target = document.querySelector(this.getAttribute('href'));
            if (target) {
                e.preventDefault();
                target.scrollIntoView({ behavior: 'smooth', block: 'start' });
            }
        });
    });
});
