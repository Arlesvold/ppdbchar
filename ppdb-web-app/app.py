from flask import Flask, render_template, redirect, url_for, request, flash, session, jsonify, send_file, abort
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect  # Add this line
from config import Config
from models import db, User, StudentProfile, Notification
from datetime import datetime
import os
from werkzeug.utils import secure_filename
import re

app = Flask(__name__, 
           template_folder='src/templates',
           static_folder='src/static')
app.config.from_object(Config)
db.init_app(app)
csrf = CSRFProtect(app)  # Add this line

# Add this near the start of app.py, after app initialization
# Create required upload folders
upload_dirs = ['photos', 'ijazah', 'payments']
for dir_name in upload_dirs:
    dir_path = os.path.join(app.config['UPLOAD_FOLDER'], dir_name)
    os.makedirs(dir_path, exist_ok=True)

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
        profile = StudentProfile.query.filter_by(user_id=user.id).first()
        progress = get_registration_progress(session['username'])
        
        user_data = {
            'name': user.username,
            'email': user.email,
            'registration_date': user.registration_date.strftime('%Y-%m-%d')
        }
        return render_template('dashboard/index.html', 
                             user=user_data, 
                             progress=progress)
    
    session.clear()
    return redirect(url_for('home'))

@app.route('/logout')
def logout():
    username = session.get('username', '')
    session.clear()
    flash(f'Terima kasih, {username}! Anda telah berhasil logout.', 'success')
    return redirect(url_for('home'))

def validate_phone_number(phone):
    # Pattern untuk nomor telepon Indonesia (+62 atau 08)
    pattern = r'^(\+62|08)\d{9,11}$'
    if not re.match(pattern, phone):
        raise ValueError('Nomor telepon tidak valid. Gunakan format +62 atau 08')
    return phone

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

        # Check if profile already exists
        existing_profile = StudentProfile.query.filter_by(user_id=user.id).first()
        if existing_profile:
            flash('Anda sudah memiliki profil pendaftaran.', 'error')
            return redirect(url_for('profile_submitted'))

        # Validate required fields
        required_fields = [
        'full_name', 'birth_date', 'gender', 'phone', 'address',
        'school_origin', 'graduation_year', 'jurusan', 'waktu_kuliah',
        'parent_name', 'parent_occupation', 'parent_phone', 'religion', 'age'
    ]

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
                    'waktu_kuliah': 'Waktu Kuliah',
                    'parent_name': 'Nama Orang Tua',
                    'parent_occupation': 'Pekerjaan Orang Tua',
                    'parent_phone': 'Nomor HP Orang Tua',
                    'religion': 'Agama',
                    'age': 'Umur'
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

        # Validate both phone numbers
        phone = request.form.get('phone')
        parent_phone = request.form.get('parent_phone')
        
        try:
            phone = validate_phone_number(phone)
            parent_phone = validate_phone_number(parent_phone)
        except ValueError as e:
            flash(str(e), 'error')
            return redirect(url_for('dashboard'))

        # Create student profile
        profile = StudentProfile(
            user_id=user.id,
            full_name=request.form['full_name'],
            birth_date=birth_date,
            gender=request.form['gender'],
            phone=request.form['phone'],
            address=request.form['address'],
            school_origin=request.form['school_origin'],
            graduation_year=int(request.form['graduation_year']),
            jurusan=request.form['jurusan'],
            waktu_kuliah=request.form['waktu_kuliah'],
            parent_name=request.form['parent_name'],
            parent_occupation=request.form['parent_occupation'],
            parent_phone=request.form['parent_phone'],
            religion=request.form['religion'],
            age=int(request.form['age']),
            photo_path=photo_filename,
            ijazah_path=ijazah_filename,
            status='pending',  # Add this
            payment_status='unpaid',  # Add this
            created_at=datetime.utcnow()  # Add this
        )
    
        
        db.session.add(profile)
        db.session.commit()
        
        flash('Pendaftaran berhasil! Data Anda telah tersimpan.', 'success')
        return redirect(url_for('profile_submitted'))
        
    except ValueError as ve:
        db.session.rollback()
        flash(f'Format data tidak valid: {str(ve)}', 'error')
        print(f"Value Error: {str(ve)}")
        return redirect(url_for('dashboard'))
    except IOError as ie:
        db.session.rollback()
        flash('Terjadi kesalahan saat menyimpan file.', 'error')
        print(f"IO Error: {str(ie)}")
        return redirect(url_for('dashboard'))
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat menyimpan data. Silakan coba lagi.', 'error')
        print(f"General Error: {str(e)}")
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
    
    # Initialize statistics
    stats = {
        'total_pendaftar': len(profiles),
        'status_pendaftaran': {
            'pending': 0,
            'accepted': 0,
            'rejected': 0
        },
        'agama': {},
        'umur': {},
        'kota': {},
        'tahun_lulus': {},
        'jurusan': {},
        'waktu_kuliah': {},
        'payment_status': {
            'unpaid': 0,
            'pending': 0,
            'verified': 0
        }
    }
    
    # Calculate statistics
    for profile in profiles:
        # Status pendaftaran
        stats['status_pendaftaran'][profile.status] += 1
        
        # Agama
        stats['agama'][profile.religion] = stats['agama'].get(profile.religion, 0) + 1
        
        # Umur
        stats['umur'][profile.age] = stats['umur'].get(profile.age, 0) + 1
        
        # Extract city from address
        try:
            city = profile.address.split(',')[-2].strip()
            stats['kota'][city] = stats['kota'].get(city, 0) + 1
        except:
            stats['kota']['Lainnya'] = stats['kota'].get('Lainnya', 0) + 1
            
        # Tahun lulus
        stats['tahun_lulus'][profile.graduation_year] = stats['tahun_lulus'].get(profile.graduation_year, 0) + 1
        
        # Program studi
        jurusan_names = {
            'TI': 'Teknik Informatika',
            'SI': 'Sistem Informasi',
            'RPL': 'Rekayasa Perangkat Lunak',
            'MI': 'Manajemen Informatika'
        }
        jurusan = jurusan_names.get(profile.jurusan, profile.jurusan)
        stats['jurusan'][jurusan] = stats['jurusan'].get(jurusan, 0) + 1
        
        # Waktu kuliah
        stats['waktu_kuliah'][profile.waktu_kuliah] = stats['waktu_kuliah'].get(profile.waktu_kuliah, 0) + 1
        
        # Payment status
        stats['payment_status'][profile.payment_status] += 1
    
    # Sort statistics
    for key in ['agama', 'umur', 'kota', 'tahun_lulus', 'jurusan']:
        stats[key] = dict(sorted(stats[key].items(), key=lambda x: x[1], reverse=True))
    
    # Calculate percentages
    stats['percentages'] = {
        'status': {
            status: round((count / stats['total_pendaftar']) * 100, 1)
            for status, count in stats['status_pendaftaran'].items()
        },
        'payment': {
            status: round((count / stats['total_pendaftar']) * 100, 1)
            for status, count in stats['payment_status'].items()
        }
    }
    
    return render_template('dashboard/dashadmin.html', 
                         profiles=profiles,
                         stats=stats)

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
        return jsonify({'error': 'Unauthorized'}), 403
    
    profile = StudentProfile.query.get_or_404(profile_id)
    file_ext = profile.ijazah_path.rsplit('.', 1)[1].lower() if '.' in profile.ijazah_path else ''
    
    return jsonify({
        'full_name': profile.full_name,
        'birth_date': profile.birth_date.strftime('%d %B %Y'),
        'gender': profile.gender,
        'religion': profile.religion,
        'age': profile.age,
        'phone': profile.phone,
        'address': profile.address,
        'parent_name': profile.parent_name,
        'parent_occupation': profile.parent_occupation,
        'parent_phone': profile.parent_phone,
        'school_origin': profile.school_origin,
        'graduation_year': profile.graduation_year,
        'jurusan': profile.jurusan,
        'waktu_kuliah': profile.waktu_kuliah,
        'photo_path': profile.photo_path,
        'ijazah_path': profile.ijazah_path,
        'ijazah_is_image': file_ext in ['jpg', 'jpeg', 'png'],
        'status': profile.status,
        'created_at': profile.created_at.strftime('%d %B %Y %H:%M'),
        'payment_status': profile.payment_status,
        'payment_date': profile.payment_date.strftime('%d %B %Y %H:%M') if profile.payment_date else None,
        'payment_proof': profile.payment_proof,
        'payment_amount': "{:,.2f}".format(profile.payment_amount) if profile.payment_amount else None
    })

@app.route('/upload-payment-proof', methods=['POST'])
def upload_payment_proof():
    if 'username' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    profile = StudentProfile.query.filter_by(user_id=user.id).first()
    
    if not profile:
        flash('Profile tidak ditemukan.', 'error')
        return redirect(url_for('dashboard'))
        
    if profile.status != 'accepted':
        flash('Pendaftaran Anda belum diverifikasi admin.', 'error')
        return redirect(url_for('profile_submitted'))

    if 'payment_proof' not in request.files:
        flash('Tidak ada file yang dipilih.', 'error')
        return redirect(url_for('profile_submitted'))
        
    payment_proof = request.files['payment_proof']
    
    if payment_proof.filename == '':
        flash('Tidak ada file yang dipilih.', 'error')
        return redirect(url_for('profile_submitted'))
        
    if not allowed_file(payment_proof.filename, {'png', 'jpg', 'jpeg'}):
        flash('File harus berupa gambar (PNG/JPG).', 'error')
        return redirect(url_for('profile_submitted'))
        
    try:
        # Create payments directory if it doesn't exist
        payments_dir = os.path.join(app.config['UPLOAD_FOLDER'], 'payments')
        os.makedirs(payments_dir, exist_ok=True)
        
        # Save payment proof
        filename = secure_filename(f"payment_{user.username}_{int(datetime.now().timestamp())}.{payment_proof.filename.rsplit('.', 1)[1].lower()}")
        payment_proof.save(os.path.join(payments_dir, filename))
        
        # Update profile
        profile.payment_proof = filename
        profile.payment_status = 'pending'
        profile.payment_date = datetime.now()
        
        db.session.commit()
        
        flash('Bukti pembayaran berhasil diunggah dan sedang menunggu verifikasi admin.', 'success')
        
    except Exception as e:
        db.session.rollback()
        flash('Terjadi kesalahan saat mengunggah bukti pembayaran.', 'error')
        print(f"Error: {str(e)}")
        
    return redirect(url_for('profile_submitted'))

@app.route('/admin/verify-payment/<int:profile_id>', methods=['POST'])
def verify_payment(profile_id):
    if not session.get('is_admin'):
        return jsonify({'success': False, 'message': 'Unauthorized'}), 403
    
    try:
        profile = StudentProfile.query.get_or_404(profile_id)
        
        if profile.payment_status != 'pending':
            return jsonify({
                'success': False, 
                'message': 'Status pembayaran tidak valid'
            }), 400
        
        # Update payment status
        profile.payment_status = 'verified'
        profile.payment_date = datetime.utcnow()
        
        # Create notification for user
        notification = Notification(
            user_id=profile.user_id,
            message='Pembayaran Anda telah diverifikasi.',
            type='success'
        )
        
        db.session.add(notification)
        db.session.commit()
        
        return jsonify({
            'success': True,
            'message': 'Pembayaran berhasil diverifikasi'
        })
        
    except Exception as e:
        db.session.rollback()
        print(f"Error in verify_payment: {str(e)}")
        return jsonify({
            'success': False,
            'message': f'Terjadi kesalahan: {str(e)}'
        }), 500

# Add this function in app.py
def get_registration_progress(username):
    user = User.query.filter_by(username=username).first()
    if not user:
        return {
            'percentage': 0,
            'status': 'Belum Terdaftar',
            'steps': []
        }

    profile = StudentProfile.query.filter_by(user_id=user.id).first()
    steps = [
        {
            'name': 'Registrasi Akun',
            'completed': True,
            'icon': 'fas fa-user-plus'
        },
        {
            'name': 'Pengisian Formulir',
            'completed': profile is not None,
            'icon': 'fas fa-file-alt'
        },
        {
            'name': 'Verifikasi Admin',
            'completed': profile and profile.status == 'accepted',
            'icon': 'fas fa-check-circle'
        },
        {
            'name': 'Pembayaran',
            'completed': profile and profile.payment_status == 'verified',
            'icon': 'fas fa-money-bill-wave'
        }
    ]
    
    completed_steps = sum(1 for step in steps if step['completed'])
    percentage = int((completed_steps / len(steps)) * 100)
    
    status_messages = {
        0: 'Mulai Pendaftaran',
        25: 'Lengkapi Formulir',
        50: 'Menunggu Verifikasi',
        75: 'Lakukan Pembayaran',
        100: 'Pendaftaran Selesai'
    }
    
    return {
        'percentage': percentage,
        'status': status_messages[round(percentage / 25) * 25],
        'steps': steps
    }

# Add this to make the function available in templates
app.jinja_env.globals.update(get_registration_progress=get_registration_progress)

@app.route('/registration-progress')
def registration_progress():
    if 'username' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('login'))
    
    progress = get_registration_progress(session['username'])
    profile = StudentProfile.query.filter_by(user_id=user.id).first()
    
    return render_template('dashboard/registration_progress.html', 
                         progress=progress,
                         profile=profile)

@app.route('/admin/reports')
@app.route('/admin/reports/<filter_type>/<filter_value>')
def admin_reports(filter_type=None, filter_value=None):
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    # Base query
    query = StudentProfile.query
    
    # Apply filters
    if filter_type and filter_value:
        if filter_type == 'agama':
            query = query.filter_by(religion=filter_value)
        elif filter_type == 'umur':
            query = query.filter_by(age=int(filter_value))
        elif filter_type == 'kota':
            query = query.filter(StudentProfile.address.like(f'%{filter_value}%'))
        elif filter_type == 'tahun_lulus':
            query = query.filter_by(graduation_year=int(filter_value))
        elif filter_type == 'jurusan':
            query = query.filter_by(jurusan=filter_value)
        elif filter_type == 'waktu_kuliah':
            query = query.filter_by(waktu_kuliah=filter_value)
        elif filter_type == 'gender':
            query = query.filter_by(gender=filter_value)
        elif filter_type == 'status':
            query = query.filter_by(status=filter_value)
        elif filter_type == 'payment_status':
            query = query.filter_by(payment_status=filter_value)
    
    profiles = query.all()
    
    # Initialize statistics dictionary
    stats = {
        'total_pendaftar': len(StudentProfile.query.all()),
        'filtered_total': len(profiles),
        'gender': {'L': 0, 'P': 0},
        'agama': {},
        'umur': {},
        'kota': {},
        'tahun_lulus': {},
        'jurusan': {},
        'waktu_kuliah': {'siang': 0, 'malam': 0},
        'status_pendaftaran': {
            'pending': 0,
            'accepted': 0,
            'rejected': 0
        },
        'payment_status': {
            'unpaid': 0,
            'pending': 0,
            'verified': 0
        }
    }
    
    # Calculate statistics from all profiles
    all_profiles = StudentProfile.query.all()
    for profile in all_profiles:
        # Gender stats
        stats['gender'][profile.gender] = stats['gender'].get(profile.gender, 0) + 1
        
        # Religion stats
        stats['agama'][profile.religion] = stats['agama'].get(profile.religion, 0) + 1
        
        # Age stats
        stats['umur'][profile.age] = stats['umur'].get(profile.age, 0) + 1
        
        # City stats
        try:
            city = profile.address.split(',')[-2].strip()
            stats['kota'][city] = stats['kota'].get(city, 0) + 1
        except:
            stats['kota']['Lainnya'] = stats['kota'].get('Lainnya', 0) + 1
        
        # Graduation year stats
        stats['tahun_lulus'][profile.graduation_year] = stats['tahun_lulus'].get(profile.graduation_year, 0) + 1
        
        # Major stats
        jurusan_names = {
            'TI': 'Teknik Informatika',
            'SI': 'Sistem Informasi',
            'RPL': 'Rekayasa Perangkat Lunak',
            'MI': 'Manajemen Informatika'
        }
        jurusan = jurusan_names.get(profile.jurusan, profile.jurusan)
        stats['jurusan'][jurusan] = stats['jurusan'].get(jurusan, 0) + 1
        
        # Study time stats
        waktu_display = {
            'siang': 'Kelas Siang',
            'malam': 'Kelas Malam'
        }
        waktu = waktu_display.get(profile.waktu_kuliah, profile.waktu_kuliah)
        stats['waktu_kuliah'][waktu] = stats['waktu_kuliah'].get(waktu, 0) + 1
        
        # Registration status stats
        stats['status_pendaftaran'][profile.status] = stats['status_pendaftaran'].get(profile.status, 0) + 1
        
        # Payment status stats
        stats['payment_status'][profile.payment_status] = stats['payment_status'].get(profile.payment_status, 0) + 1
    
    # Sort all statistics
    for key in stats.keys():
        if isinstance(stats[key], dict):
            stats[key] = dict(sorted(stats[key].items(), key=lambda x: x[1], reverse=True))
    
    return render_template('dashboard/admin_reports.html',
                         stats=stats,
                         profiles=profiles,
                         filter_type=filter_type,
                         filter_value=filter_value)

@app.route('/download/<folder>/<filename>')
def download_file(folder, filename):
    if 'username' not in session:
        flash('Silakan login terlebih dahulu.', 'error')
        return redirect(url_for('login'))
        
    # Validate folder name
    if folder not in ['photos', 'ijazah', 'payments']:
        abort(404)
        
    try:
        # Construct the file path
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], folder, filename)
        
        # Check if file exists
        if not os.path.exists(file_path):
            abort(404)
            
        # Get the file extension
        file_ext = os.path.splitext(filename)[1].lower()
        
        # Set correct MIME type
        mime_type = 'application/pdf' if file_ext == '.pdf' else 'image/jpeg'
        
        return send_file(
            file_path,
            mimetype=mime_type,
            as_attachment=True,
            download_name=filename
        )
        
    except Exception as e:
        app.logger.error(f"Download error: {str(e)}")
        flash('Gagal mengunduh file.', 'error')
        return redirect(url_for('profile_submitted'))

if __name__ == '__main__':
    app.run(debug=True)