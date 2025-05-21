from app import app
import os
from config import Config

if __name__ == '__main__':
    # Ensure required directories exist
    upload_dirs = ['photos', 'ijazah', 'payments']
    for dir_name in upload_dirs:
        dir_path = os.path.join(Config.UPLOAD_FOLDER, dir_name)
        os.makedirs(dir_path, exist_ok=True)

    # Create logs directory for email error logging
    os.makedirs('logs', exist_ok=True)

    # Set host and port
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Set debug mode from environment variable or default to False
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Run the application
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=True
    )