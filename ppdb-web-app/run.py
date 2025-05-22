from app import app
import os
from config import Config

if __name__ == '__main__':
    # Buat direktori yang diperlukan
    upload_dirs = ['photos', 'ijazah', 'payments']
    for dir_name in upload_dirs:
        dir_path = os.path.join(Config.UPLOAD_FOLDER, dir_name)
        os.makedirs(dir_path, exist_ok=True)

    # Buat direktori logs
    os.makedirs('logs', exist_ok=True)

    # Set host dan port
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    
    # Set mode debug
    debug = os.environ.get('FLASK_DEBUG', 'False').lower() == 'true'

    # Jalankan aplikasi
    app.run(
        host=host,
        port=port,
        debug=debug,
        use_reloader=True
    )