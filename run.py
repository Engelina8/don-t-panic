"""
Simple run script for Don't Panic application
No virtual environment needed - runs directly on system Python
"""

from app import create_app
import os

if __name__ == '__main__':
    # Create the Flask app
    app = create_app('development')
    
    # Print startup info
    print("\n" + "="*60)
    print("🚀 DON'T PANIC - Incident Response Training")
    print("="*60)
    print(f"🌐 Server: http://localhost:5000")
    print(f"🌐 Network: http://0.0.0.0:5000")
    print(f"🔧 Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"🐛 Debug: {app.config['DEBUG']}")
    print("="*60)
    print("📝 Default Login:")
    print("   Username: instructor")
    print("   Password: instructor123")
    print("="*60 + "\n")
    
    # Run the application
    app.run(
        host='0.0.0.0',  # Accessible from network
        port=5000,
        debug=True,
        use_reloader=True  # Auto-restart on code changes
    )
