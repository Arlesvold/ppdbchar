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

## 📸 Screenshots

### 🏠 User Interface
![Tampilan Awal](/ppdb-web-app/src/static/readfoto/Tampilan%20awal.png)
![Tampilan Awal 2](/ppdb-web-app/src/static/readfoto/Tampilan%20awal%20(2).png)
*Modern and responsive landing page showcasing key features and easy navigation*

### 🔐 Authentication
![Login Page](/ppdb-web-app/src/static/readfoto/Login.png)
![Register Page](/ppdb-web-app/src/static/readfoto/Register.png)
*Secure and user-friendly authentication system with clean interface*

### ✍️ Registration Process
#### Form Submission
![Form Pengisian](./ppdb-web-app/src/static/readfoto/Mengisi%20Formulir.png)
![Form Pengisian 3](./ppdb-web-app/src/static/readfoto/Mengisi%20Formulir%20(3).png)
![Notifikasi Form](/ppdb-web-app/src/static/readfoto/Notifikasi%20jika%20formulir%20tidak%20lengkap%20diisi.png)
*Intuitive form with real-time validation and helpful notifications*

#### 📄 Document Upload
![Upload Dokumen](/ppdb-web-app/src/static/readfoto/Upload%20dokumen.png)
![Upload Foto dan Ijazah](/ppdb-web-app/src/static/readfoto/Upload%20dokumen%20Pas%20foto%20dan%20ijazah.png)
*Seamless document upload system for photos and certificates*

#### 📊 Status Tracking
![Progress Pendaftaran](/ppdb-web-app/src/static/readfoto/Progress%20pendaftaran.png)
![Menunggu Verifikasi](/ppdb-web-app/src/static/readfoto/Menunggu%20verikasi%20admin%20setelah%20mendaftar.png)
![Pendaftaran Diterima](/ppdb-web-app/src/static/readfoto/Pendaftaran%20diterima.png)
*Visual progress tracking with status updates and clear notifications*

### 💳 Payment System
![Kartu Transfer](/ppdb-web-app/src/static/readfoto/kartu%20untuk%20transfer.png)
![Bukti Pembayaran](/ppdb-web-app/src/static/readfoto/Bukti%20pembayaran.png)
![Menunggu Verifikasi Pembayaran](/ppdb-web-app/src/static/readfoto/Menunggu%20verifikasi%20pembayaran%20oleh%20admin.png)
![Pembayaran Diverifikasi](/ppdb-web-app/src/static/readfoto/Pembayaran%20diverifikasi.png)
![Progress Complete](./ppdb-web-app/src/static/readfoto/Progress%20100%25%20jika%20sudah%20selesai%20pembayaran.png)
*Comprehensive payment system with transfer details, proof upload, and status tracking*

### 👨‍💼 Admin Dashboard
![Admin Dashboard](/ppdb-web-app/src/static/readfoto/Admin%20Dashboard.png)
*Powerful admin dashboard with overview statistics and quick actions*

![Laporan Statistik](/ppdb-web-app/src/static/readfoto/laporan.png)
*Detailed statistical reports with interactive filters and export options*

![Detail Pendaftar](/ppdb-web-app/src/static/readfoto/Detail.png)
![Detail Pendaftar 2](/ppdb-web-app/src/static/readfoto/Detail%20(2).png)
*Comprehensive applicant details with document preview and status management*

![Detail Diterima](/ppdb-web-app/src/static/readfoto/Detail%20pendaftar%20jika%20sudah%20diterima.png)
*Acceptance status view with complete applicant information*

![Alasan Penolakan](/ppdb-web-app/src/static/readfoto/Alasan%20jika%20menolak%20pendaftaran.png)
*Rejection management with reason documentation*

### 📧 Email Notifications
![Email Notifikasi](/ppdb-web-app/src/static/readfoto/Menerika%20pemberitahuan%20di%20email%20user.png)
![Status Pembayaran](/ppdb-web-app/src/static/readfoto/Pembayaran%20ketika%20sudah%20diterima%20oleh%20admin.png)
*Automated email notifications for registration updates and payment verification*

## 📝 License

This project is licensed under the MIT License.

---

<div align="center">
Made with ❤️ by Charles Adrian
</div>