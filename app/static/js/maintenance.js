cat > app/static/js/maintenance.js << 'EOF'
/**
 * DON'T PANIC - Maintenance Page Interactivity
 */

document.addEventListener('DOMContentLoaded', function() {
    // Type writer effect for status messages
    const statusMessages = [
        'Scanning network topology...',
        'Analyzing threat vectors...',
        'Deploying firewall rules...',
        'Encrypting communications...',
        'Validating security certificates...'
    ];
    
    let messageIndex = 0;
    const statusElement = document.querySelector('.status-text');
    
    function rotateMessages() {
        if (statusElement) {
            statusElement.style.opacity = '0';
            
            setTimeout(() => {
                messageIndex = (messageIndex + 1) % statusMessages.length;
                statusElement.textContent = statusMessages[messageIndex];
                statusElement.style.opacity = '1';
            }, 500);
        }
    }
    
    // Rotate messages every 3 seconds
    setInterval(rotateMessages, 3000);
    
    // Add smooth transition
    if (statusElement) {
        statusElement.style.transition = 'opacity 0.5s ease';
    }
    
    // Matrix rain effect (optional easter egg)
    const commandLine = document.querySelector('.command');
    const commands = [
        'npm install security',
        'docker-compose up',
        'python train_model.py',
        'git commit -m "feat: add scenarios"',
        'flask db upgrade',
        'pytest tests/'
    ];
    
    let cmdIndex = 0;
    
    function rotateCommands() {
        if (commandLine) {
            cmdIndex = (cmdIndex + 1) % commands.length;
            commandLine.textContent = commands[cmdIndex] + '_';
        }
    }
    
    setInterval(rotateCommands, 4000);
    
    // GitHub link functionality
    const repoLink = document.querySelector('.repo-link');
    if (repoLink) {
        repoLink.addEventListener('click', function() {
            // Replace with your actual repository URL
            // window.open('https://github.com/yourusername/dont-panic-platform', '_blank');
            alert('Repository link will be added here!');
        });
        
        repoLink.style.cursor = 'pointer';
    }
    
    // Loading bar progress update
    const loadingProgress = document.querySelector('.loading-progress');
    let progress = 70;
    
    function updateProgress() {
        if (loadingProgress && progress < 95) {
            progress += Math.random() * 2;
            loadingProgress.style.width = progress + '%';
        }
    }
    
    setInterval(updateProgress, 2000);
    
    // Console easter egg
    console.log('%cDON\'T PANIC', 'color: #00ff41; font-size: 24px; font-weight: bold; font-family: monospace;');
    console.log('%cCybersecurity Training Platform', 'color: #58a6ff; font-size: 14px; font-family: monospace;');
    console.log('%cUnder construction... 🚧', 'color: #d29922; font-size: 12px; font-family: monospace;');
    console.log('%cType "panic()" for emergency contact info', 'color: #8b949e; font-size: 11px; font-style: italic;');
    
    window.panic = function() {
        console.log('%c⚠️  EMERGENCY PROTOCOL ACTIVATED', 'color: #f85149; font-size: 16px; font-weight: bold;');
        console.log('Contact: your.instructor@school.com');
        console.log('GitHub: [Your Repository URL]');
        console.log('Status: Platform expected online January 2026');
    };
});

// Add keyboard shortcuts
document.addEventListener('keydown', function(e) {
    // Ctrl/Cmd + K = Toggle terminal glow
    if ((e.ctrlKey || e.metaKey) && e.key === 'k') {
        e.preventDefault();
        const terminal = document.querySelector('.terminal-window');
        terminal.style.boxShadow = terminal.style.boxShadow 
            ? '' 
            : '0 0 30px rgba(0, 255, 65, 0.5), 0 20px 60px rgba(0, 0, 0, 0.5)';
    }
});
EOF
