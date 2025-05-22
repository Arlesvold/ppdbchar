# 🎓 PMB Online System

## 👨‍💻 Author

**Charles Adrian**
- Software Engineering Student
- SMK KARYA BANGSA
- Class: XI RPL


A modern web-based student registration system built with Flask, featuring real-time notifications, email integration, and secure document handling.

## 📋 Features

### Student Features
- **User Authentication**
  - Secure registration and login
  - Email verification system
  - Password encryption and protection

- **Profile Management**
  - Personal information submission
  - Document uploads (photos, certificates)
  - Real-time form validation
  - Profile status tracking

- **Document Management**
  - Secure file uploads
  - Support for images and PDFs
  - Document verification system

- **Payment System**
  - Multiple payment methods
  - Payment proof upload
  - Payment status tracking
  - Automatic email notifications

### Admin Features
- **Dashboard Analytics**
  - Real-time registration statistics
  - Payment monitoring
  - Document verification
  - User management

- **Application Processing**
  - Review student applications
  - Accept/Reject applications
  - Payment verification
  - Automated email notifications

## 🔧 Technical Stack

- **Backend**: Python Flask
- **Database**: SQLAlchemy with SQLite
- **Frontend**: HTML5, CSS3, JavaScript
- **Email Service**: Flask-Mail
- **Security**: Flask-WTF, CSRFProtect
- **File Handling**: Werkzeug

## 📁 Project Structure
```
ppdb-web-app/
├── src/
│   ├── static/
│   │   ├── css/
│   │   │   ├── auth.css
│   │   │   ├── dashboard.css
│   │   │   ├── profile_submitted.css
│   │   │   └── styles.css
│   │   ├── js/
│   │   │   └── main.js
│   │   └── uploads/
│   │       ├── photos/
│   │       ├── ijazah/
│   │       └── payments/
│   └── templates/
│       ├── auth/
│       ├── dashboard/
│       ├── emails/
│       └── layout/
├── app.py
├── config.py
├── models.py
├── email_service.py
├── requirements.txt
└── .env
```

## 💻 Installation

1. Clone the repository:
```bash
git clone <repository-url>
cd ppdb-web-app
```

2. Create and activate virtual environment:
```bash
python -m venv env
.\env\Scripts\activate  # Windows
source env/bin/activate # Linux/Mac
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Configure environment variables in `.env`:
```plaintext
FLASK_APP=app.py
FLASK_ENV=development
SECRET_KEY=your-secret-key
MAIL_USERNAME=your-email@gmail.com
MAIL_PASSWORD=your-app-password
MAIL_DEFAULT_SENDER=PPDB Online <your-email@gmail.com>
```

5. Initialize database:
```bash
flask db init
flask db migrate
flask db upgrade
```

6. Run the application:
```bash
python run.py
```

## 📧 Email Configuration

1. Enable 2-Step Verification in Google Account
2. Generate App Password:
   - Go to Google Account Security
   - Select 'App Passwords'
   - Generate new password for 'Mail'
3. Update `.env` with credentials

## 👥 User Roles

### Student
- Register account
- Submit personal information
- Upload required documents
- Monitor application status
- Process payments

### Administrator
- Review applications
- Accept/Reject registrations
- Verify documents
- Monitor payments
- View statistics

## 🔐 Security Features

- Password hashing
- CSRF protection
- Secure file uploads
- Session management
- Input validation
- Email verification

## 📝 License

This project is licensed under the MIT License.

---

<div align="center">
Made with ❤️ by Charles Adrian
</div>