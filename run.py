"""
Simple run script for Don't Panic application
No virtual environment needed - runs directly on system Python
"""

from app import create_app
import os

if __name__ == '__main__':

    app = create_app('development')

    debug_mode = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'
    host = os.environ.get('FLASK_HOST', '127.0.0.1')
    port = int(os.environ.get('FLASK_PORT', 5000))

    print("\n" + "="*60)
    print("DON'T PANIC - Incident Response Training")
    print("="*60)
    print(f"Local: http://localhost:{port}")
    print(f"Host: {host}")
    print(f"Environment: {os.environ.get('FLASK_ENV', 'development')}")
    print(f"Debug: {debug_mode}")
    print("="*60)
    print("Default Login:")
    print("   Username: instructor")
    print("   Password: instructor123")
    print("="*60 + "\n")

    app.run(
        host=host,
        port=port,
        debug=debug_mode,
        use_reloader=True
    )
