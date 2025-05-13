from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect  # Add this line
from config import Config
from models import db, User, StudentProfile, Notification
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__, 
           template_folder='src/templates',
           static_folder='src/static')
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)  # Add this line

# Add database connection check here
with app.app_context():
    try:
        db.create_all()
        print("Database tables created successfully")
    except Exception as e:
        print(f"Error creating database tables: {e}")

def allowed_file(filename, allowed_extensions):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

@app.route('/')
def home():
    return render_template('index.html')  # This is your main landing page

@app.route('/login', methods=['GET', 'POST'])
def login():
    if 'username' in session:
        if session.get('is_admin'):
            return redirect(url_for('admin_dashboard'))
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        # Check if it's admin login
        if username == 'admin' and password == '22':
            session['username'] = username
            session['is_admin'] = True
            flash('Welcome Admin!', 'success')
            return redirect(url_for('admin_dashboard'))
        
        # If not admin, check regular user login
        user = User.query.filter_by(username=username).first()
        if user and user.check_password(password):
            session['username'] = username
            session['user_id'] = user.id
            session['email'] = user.email
            
            # Check if user has already submitted profile
            profile = StudentProfile.query.filter_by(user_id=user.id).first()
            if profile:
                return redirect(url_for('profile_submitted'))
            
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Invalid username or password.', 'error')
    
    return render_template('auth/login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if 'username' in session:
        return redirect(url_for('dashboard'))
    
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        
        # Check for existing username
        existing_username = User.query.filter_by(username=username).first()
        if existing_username:
            flash('Username sudah digunakan. Silakan pilih username lain.', 'error')
            return render_template('auth/register.html', 
                                email=email,
                                username_error=True)
            
        # Check for existing email
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email sudah terdaftar. Silakan gunakan email lain.', 'error')
            return render_template('auth/register.html', 
                                username=username,
                                email_error=True)

        try:
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registrasi berhasil! Silakan login dengan akun Anda.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('Terjadi kesalahan saat registrasi. Silakan coba lagi.', 'error')
            print(f"Registration error: {str(e)}")
            
    return render_template('auth/register.html')

@app.route('/dashboard')
def dashboard():
    if 'username' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    
    if user:
        # Check if user has already submitted profile
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        
        if profile:
            # If profile exists, redirect to profile_submitted page
            flash('Welcome back! Here is your submitted application.', 'info')
            return redirect(url_for('profile_submitted'))
        
        # If no profile exists, show the form to submit profile
        user_data = {
            'name': user.username,
            'email': user.email,
            'registration_date': user.registration_date.strftime('%Y-%m-%d')
        }
        return render_template('dashboard/index.html', user=user_data)
    
    session.clear()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    username = session.get('username', '')
    session.clear()
    flash(f'Terima kasih, {username}! Anda telah berhasil logout.', 'success')
    return redirect(url_for('home'))

@app.route('/submit-profile', methods=['POST'])
def submit_profile():
    if 'username' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))
    
    try:
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash('User tidak ditemukan.', 'error')
            return redirect(url_for('login'))

        # Validate required fields
        required_fields = ['full_name', 'birth_date', 'gender', 'phone', 'address', 
                         'school_origin', 'graduation_year', 'jurusan', 'waktu_kuliah']
        
        for field in required_fields:
            if not request.form.get(field):
                field_names = {
                    'full_name': 'Nama Lengkap',
                    'birth_date': 'Tanggal Lahir',
                    'gender': 'Jenis Kelamin',
                    'phone': 'Nomor Telepon',
                    'address': 'Alamat',
                    'school_origin': 'Asal Sekolah',
                    'graduation_year': 'Tahun Lulus',
                    'jurusan': 'Program Studi',
                    'waktu_kuliah': 'Waktu Kuliah'
                }
                flash(f'{field_names.get(field, field)} harus diisi.', 'error')
                return redirect(url_for('dashboard'))

        # Validate file uploads
        if 'photo' not in request.files or 'ijazah' not in request.files:
            flash('Foto dan ijazah harus diunggah.', 'error')
            return redirect(url_for('dashboard'))

        photo = request.files['photo']
        ijazah = request.files['ijazah']

        if photo.filename == '' or ijazah.filename == '':
            flash('Foto dan ijazah harus diunggah.', 'error')
            return redirect(url_for('dashboard'))

        ALLOWED_PHOTO_EXTENSIONS = {'png', 'jpg', 'jpeg'}
        ALLOWED_IJAZAH_EXTENSIONS = {'pdf', 'png', 'jpg', 'jpeg'}

        if not allowed_file(photo.filename, ALLOWED_PHOTO_EXTENSIONS):
            flash('Foto harus dalam format PNG/JPG.', 'error')
            return redirect(url_for('dashboard'))

        if not allowed_file(ijazah.filename, ALLOWED_IJAZAH_EXTENSIONS):
            flash('Ijazah harus dalam format PDF/PNG/JPG.', 'error')
            return redirect(url_for('dashboard'))

        # Create upload directories
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(os.path.join(upload_folder, 'photos'), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'ijazah'), exist_ok=True)

        # Save files with secure filenames
        photo_ext = photo.filename.rsplit('.', 1)[1].lower()
        ijazah_ext = ijazah.filename.rsplit('.', 1)[1].lower()
        
        photo_filename = secure_filename(f"{user.username}_photo.{photo_ext}")
        ijazah_filename = secure_filename(f"{user.username}_ijazah.{ijazah_ext}")
        
        photo.save(os.path.join(upload_folder, 'photos', photo_filename))
        ijazah.save(os.path.join(upload_folder, 'ijazah', ijazah_filename))

        # Convert date string to datetime object
        try:
            birth_date = datetime.strptime(request.form['birth_date'], '%Y-%m-%d')
        except ValueError:
            flash('Invalid date format. Please use YYYY-MM-DD format.', 'error')
            return redirect(url_for('dashboard'))

        # Create student profile
        profile = StudentProfile(
            user_id=user.id,
            full_name=request.form['full_name'],
            birth_date=birth_date,
            gender=request.form['gender'],  # Add this line
            phone=request.form['phone'],
            address=request.form['address'],
            school_origin=request.form['school_origin'],
            graduation_year=int(request.form['graduation_year']),
            jurusan=request.form['jurusan'],
            waktu_kuliah=request.form['waktu_kuliah'],
            photo_path=photo_filename,
            ijazah_path=ijazah_filename
        )
        
        db.session.add(profile)
        db.session.commit()
        
        flash('Pendaftaran berhasil! Data Anda telah tersimpan.', 'success')
        return redirect(url_for('profile_submitted'))
        
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menyimpan data. Silakan coba lagi.', 'error')
        print(f"Error: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/profile-submitted')
def profile_submitted():
    if 'username' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('login'))
    
    profile = StudentProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        flash('Silakan lengkapi profil Anda terlebih dahulu.', 'warning')
        return redirect(url_for('dashboard'))
    
    # Check for unread notifications
    notifications = Notification.query.filter_by(user_id=user.id, is_read=False).all()
    for notification in notifications:
        message = notification.message
        if notification.reason:
            message += f'\nAlasan: {notification.reason}'
        flash(message, notification.type)
        notification.is_read = True
    
    db.session.commit()
    
    if profile.status == 'pending':
        flash('Pendaftaran Anda sedang dalam proses verifikasi admin.', 'info') 
    
    return render_template('dashboard/profile_submitted.html', profile=profile, user=user)

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    # Fetch all student profiles
    profiles = StudentProfile.query.all()
    return render_template('dashboard/dashadmin.html', profiles=profiles)

@app.route('/admin/detail/<int:profile_id>')
def admin_detail(profile_id):
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    profile = StudentProfile.query.get_or_404(profile_id)
    return render_template('dashboard/admin_detail.html', profile=profile)

@app.route('/admin/action/<int:profile_id>/<action>')
def admin_action(profile_id, action):
    if not session.get('is_admin'):
        flash('Akses ditolak. Diperlukan hak akses admin.', 'error')
        return redirect(url_for('login'))
    
    profile = StudentProfile.query.get_or_404(profile_id)
    user = User.query.get(profile.user_id)
    
    if action == 'accept':
        profile.status = 'accepted'
        # Store notification for user
        flash_message = f'Selamat! Pendaftaran untuk {profile.full_name} telah diterima.'
        db.session.add(Notification(
            user_id=profile.user_id,
            message=flash_message,
            type='success'
        ))
        flash(f'Pendaftaran {profile.full_name} telah diterima.', 'success')
    elif action == 'reject':
        profile.status = 'rejected'
        # Store notification for user
        flash_message = f'Maaf, pendaftaran untuk {profile.full_name} tidak diterima.'
        db.session.add(Notification(
            user_id=profile.user_id,
            message=flash_message,
            type='error'
        ))
        flash(f'Pendaftaran {profile.full_name} telah ditolak.', 'error')
    
    db.session.commit()
    return redirect(url_for('admin_dashboard'))

@app.route('/admin/action/<int:profile_id>/reject', methods=['POST'])
def admin_reject(profile_id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 401
    
    try:
        data = request.get_json()
        reason = data.get('reason')
        
        if not reason:
            return jsonify({'success': False, 'message': 'Alasan penolakan harus diisi'}), 400
        
        profile = StudentProfile.query.get_or_404(profile_id)
        profile.status = 'rejected'
        
        # Store notification with reason
        flash_message = f'Maaf, pendaftaran untuk {profile.full_name} tidak diterima.'
        notification = Notification(
            user_id=profile.user_id,
            message=flash_message,
            reason=reason,
            type='error'
        )
        
        db.session.add(notification)
        db.session.commit()
        
        flash(f'Pendaftaran {profile.full_name} telah ditolak.', 'success')
        return jsonify({'success': True})
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in admin_reject: {str(e)}")
        return jsonify({'success': False, 'message': str(e)}), 500

@app.route('/admin/get-detail/<int:profile_id>')
def get_profile_detail(profile_id):
    if not session.get('is_admin'):
        return jsonify({'error': 'Unauthorized'}), 401
    
    profile = StudentProfile.query.get_or_404(profile_id)
    file_ext = profile.ijazah_path.rsplit('.', 1)[1].lower() if '.' in profile.ijazah_path else ''
    
    return jsonify({
        'full_name': profile.full_name,
        'birth_date': profile.birth_date.strftime('%d %B %Y'),
        'gender': profile.gender,
        'phone': profile.phone,
        'address': profile.address,
        'school_origin': profile.school_origin,
        'graduation_year': profile.graduation_year,
        'photo_path': profile.photo_path,
        'ijazah_path': profile.ijazah_path,
        'ijazah_is_image': file_ext in ['jpg', 'jpeg', 'png']
    })

if __name__ == '__main__':
    app.run(debug=True)