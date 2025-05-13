document.addEventListener('DOMContentLoaded', function() {
    const notifications = document.querySelectorAll('.notification');
    
    notifications.forEach(notification => {
        // Add animation class
        notification.style.animation = 'slideIn 0.5s ease-out forwards';
        
        // Add click handler to close button
        const closeBtn = notification.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                notification.style.animation = 'slideOut 0.5s ease-out forwards';
                setTimeout(() => {
                    notification.remove();
                }, 500);
            });
        }
    });
});