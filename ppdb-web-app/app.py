from flask import Flask, render_template, redirect, url_for, request, flash, session
from flask_sqlalchemy import SQLAlchemy
from flask_wtf.csrf import CSRFProtect  # Add this line
from config import Config
from models import db, User, StudentProfile
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
            flash('Username already exists. Please choose a different username.', 'error')
            return render_template('auth/register.html', 
                                email=email,  # Preserve the email input
                                username_error=True)
            
        # Check for existing email
        existing_email = User.query.filter_by(email=email).first()
        if existing_email:
            flash('Email already registered. Please use a different email or login.', 'error')
            return render_template('auth/register.html', 
                                username=username,  # Preserve the username input
                                email_error=True)

        # If both checks pass, create new user
        try:
            user = User(username=username, email=email)
            user.set_password(password)
            
            db.session.add(user)
            db.session.commit()
            
            flash('Registration successful! Please login with your credentials.', 'success')
            return redirect(url_for('login'))
            
        except Exception as e:
            db.session.rollback()
            flash('An error occurred during registration. Please try again.', 'error')
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
    session.clear()
    flash('You have been logged out successfully.', 'success')
    return redirect(url_for('home'))  # Changed from 'index' to 'home'

@app.route('/submit-profile', methods=['POST'])
def submit_profile():
    if 'username' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    try:
        user = User.query.filter_by(username=session['username']).first()
        if not user:
            flash('User not found.', 'error')
            return redirect(url_for('login'))

        # Validate required fields
        required_fields = ['full_name', 'birth_date', 'gender', 'phone', 'address', 
                         'school_origin', 'graduation_year', 'jurusan', 'waktu_kuliah']
        
        for field in required_fields:
            if not request.form.get(field):
                flash(f'{field.replace("_", " ").title()} is required.', 'error')
                return redirect(url_for('dashboard'))

        # Validate file uploads
        if 'photo' not in request.files or 'ijazah' not in request.files:
            flash('Both photo and ijazah files are required.', 'error')
            return redirect(url_for('dashboard'))

        photo = request.files['photo']
        ijazah = request.files['ijazah']

        if photo.filename == '' or ijazah.filename == '':
            flash('Both photo and ijazah files are required.', 'error')
            return redirect(url_for('dashboard'))

        # Create upload directories
        upload_folder = app.config['UPLOAD_FOLDER']
        os.makedirs(os.path.join(upload_folder, 'photos'), exist_ok=True)
        os.makedirs(os.path.join(upload_folder, 'ijazah'), exist_ok=True)

        # Save files with secure filenames
        photo_filename = secure_filename(f"{user.username}_photo.{photo.filename.split('.')[-1]}")
        ijazah_filename = secure_filename(f"{user.username}_ijazah.pdf")
        
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
        
        flash('Application submitted successfully! Your data has been saved.', 'success')
        return redirect(url_for('profile_submitted'))
        
    except Exception as e:
        db.session.rollback()
        flash(f'Error submitting profile: {str(e)}', 'error')
        print(f"Error: {str(e)}")
        return redirect(url_for('dashboard'))

@app.route('/profile-submitted')
def profile_submitted():
    if 'username' not in session:
        flash('Please login first.', 'error')
        return redirect(url_for('login'))
    
    user = User.query.filter_by(username=session['username']).first()
    if not user:
        return redirect(url_for('login'))
    
    profile = StudentProfile.query.filter_by(user_id=user.id).first()
    if not profile:
        flash('Please complete your profile first.', 'warning')
        return redirect(url_for('dashboard'))
    
    return render_template('dashboard/profile_submitted.html', profile=profile, user=user)

@app.route('/admin-dashboard')
def admin_dashboard():
    if not session.get('is_admin'):
        flash('Access denied. Admin privileges required.', 'error')
        return redirect(url_for('login'))
    
    # Fetch all student profiles
    profiles = StudentProfile.query.all()
    return render_template('dashboard/dashadmin.html', profiles=profiles)

if __name__ == '__main__':
    app.run(debug=True)