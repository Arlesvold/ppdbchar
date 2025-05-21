from flask_mail import Mail, Message
from flask import render_template, current_app
import logging

mail = Mail()
logger = logging.getLogger(__name__)

def send_verification_email(user_email, user_name, status):
    """Send email notification to user based on their registration status"""
    try:
        subject = {
            'accepted': 'Selamat! Pendaftaran Anda Diterima - PPDB Online',
            'rejected': 'Informasi Status Pendaftaran - PPDB Online'
        }
        
        template = {
            'accepted': 'emails/registration_accepted.html',
            'rejected': 'emails/registration_rejected.html'
        }
        
        msg = Message(
            subject=subject.get(status, 'Status Pendaftaran PPDB Online'),
            recipients=[user_email],  # Uses user's registered email
            sender=('PPDB Online', current_app.config['MAIL_USERNAME'])
        )
        
        msg.html = render_template(
            template.get(status),
            name=user_name
        )
        
        mail.send(msg)
        logger.info(f"Verification email sent to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send verification email to {user_email}: {str(e)}")
        return False

def send_payment_verification_email(user_email, user_name):
    """Send payment verification email to user"""
    try:
        msg = Message(
            subject='Pembayaran Berhasil Diverifikasi - PPDB Online',
            recipients=[user_email],  # Uses user's registered email
            sender=('PPDB Online', current_app.config['MAIL_USERNAME'])
        )
        
        msg.html = render_template(
            'emails/payment_verified.html',
            name=user_name
        )
        
        mail.send(msg)
        logger.info(f"Payment verification email sent to {user_email}")
        return True
        
    except Exception as e:
        logger.error(f"Failed to send payment verification email to {user_email}: {str(e)}")
        return False