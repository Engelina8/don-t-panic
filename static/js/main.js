// DON'T PANIC - Main JavaScript

// Register Service Worker for PWA
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('/static/js/service-worker.js')
            .then(reg => console.log('Service Worker registered'))
            .catch(err => console.log('Service Worker registration failed:', err));
    });
}

// PWA Install Button Handler
let deferredPrompt;
const installContainer = document.getElementById('install-app-container');
const installBtn = document.getElementById('install-app-btn');

// Listen for the beforeinstallprompt event
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
    // Show the install button
    if (installContainer) {
        installContainer.style.display = 'block';
    }
});

// Handle install button click
if (installBtn) {
    installBtn.addEventListener('click', async () => {
        if (deferredPrompt) {
            deferredPrompt.prompt();
            const { outcome } = await deferredPrompt.userChoice;
            console.log(`User response to the install prompt: ${outcome}`);
            deferredPrompt = null;
            if (installContainer) {
                installContainer.style.display = 'none';
            }
        }
    });
}

// Hide install button if already installed
window.addEventListener('appinstalled', () => {
    console.log('App installed successfully');
    if (installContainer) {
        installContainer.style.display = 'none';
    }
    deferredPrompt = null;
});

document.addEventListener('DOMContentLoaded', function() {
    
    // Auto-dismiss flash messages
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            alert.style.animation = 'slideOutRight 0.3s ease';
            setTimeout(() => alert.remove(), 300);
        }, 5000);
        
        // Manual close
        const closeBtn = alert.querySelector('.close-btn');
        if (closeBtn) {
            closeBtn.addEventListener('click', () => {
                alert.style.animation = 'slideOutRight 0.3s ease';
                setTimeout(() => alert.remove(), 300);
            });
        }
    });
    
    // Add ripple effect to buttons
    const buttons = document.querySelectorAll('.btn');
    buttons.forEach(button => {
        button.addEventListener('click', function(e) {
            const ripple = document.createElement('span');
            ripple.classList.add('ripple');
            this.appendChild(ripple);
            
            setTimeout(() => ripple.remove(), 600);
        });
    });
    
    // Add active class to current nav item
    const currentPath = window.location.pathname;
    const navLinks = document.querySelectorAll('nav a');
    navLinks.forEach(link => {
        if (link.getAttribute('href') === currentPath) {
            link.classList.add('active');
        }
    });
    
    // Form validation helper
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', function(e) {
            const inputs = form.querySelectorAll('input[required], textarea[required]');
            let isValid = true;
            
            inputs.forEach(input => {
                if (!input.value.trim()) {
                    input.classList.add('error');
                    isValid = false;
                } else {
                    input.classList.remove('error');
                    input.classList.add('success');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
            }
        });
    });
});

// Slide out animation for alerts
const style = document.createElement('style');
style.textContent = `
    @keyframes slideOutRight {
        to {
            transform: translateX(400px);
            opacity: 0;
        }
    }
`;
document.head.appendChild(style);
