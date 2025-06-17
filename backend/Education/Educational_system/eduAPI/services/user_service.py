import random
import string
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from django.conf import settings
from rest_framework_simplejwt.tokens import RefreshToken, TokenError
from eduAPI.models import User
from datetime import datetime, timedelta
import secrets
from django.utils import timezone
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags


def generate_verification_code():
    """Generate a random 6-digit verification code."""
    return ''.join(random.choices(string.digits, k=6))


def send_verification_email(user):
    """Send verification email to the user with the verification code"""
    verification_code = generate_verification_code()
    user.verification_code = verification_code
    user.save()
    
    subject = 'Email Verification - Complementary Education System'
    html_message = render_to_string('verification_email.html', {
        'user': user,
        'verification_code': verification_code
    })
    plain_message = strip_tags(html_message)
    from_email = settings.EMAIL_HOST_USER
    to_email = user.email
    
    send_mail(
        subject,
        plain_message,
        from_email,
        [to_email],
        html_message=html_message,
        fail_silently=False
    )


def verify_email(user, verification_code):
    """Verify user's email with the provided verification code."""
    if user.verification_code == verification_code:
        user.is_email_verified = True
        user.verification_code = None
        user.save()
        return True
    return False


def get_tokens_for_user(user):
    """Generate access and refresh tokens for the user."""
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


def update_user_profile(user, profile_data):
    """Update user profile with the provided data."""
    for field, value in profile_data.items():
        setattr(user, field, value)
    user.save()
    return user


def generate_password_reset_token():
    """Generate a random secure token for password reset"""
    return secrets.token_hex(32)  # 64 characters long


def initiate_password_reset(email):
    """
    Generate password reset token and send email to user
    Returns: (success, message)
    """
    try:
        user = User.objects.get(email=email)
        token = generate_password_reset_token()
        
        # Set token and expiration (24 hours from now)
        user.password_reset_token = token
        user.password_reset_expires = timezone.now() + timedelta(hours=24)
        user.save()
        
        # Send reset password email - use direct email approach first
        reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
        
        print(f"Generating password reset for {email} with token {token}")
        print(f"Reset link: {reset_link}")
        
        try:
            # Try django's send_mail first
            subject = 'Password Reset - Complementary Education System'
            html_message = render_to_string('password_reset_email.html', {
                'user': user,
                'reset_link': reset_link
            })
            plain_message = strip_tags(html_message)
            from_email = settings.EMAIL_HOST_USER
            
            send_mail(
                subject,
                plain_message,
                from_email,
                [email],
                html_message=html_message,
                fail_silently=False
            )
            print(f"Password reset email sent via Django's send_mail")
        except Exception as email_error:
            print(f"Error sending email via Django's send_mail: {email_error}")
            
            # Fallback to SMTP directly
            try:
                sender_email = settings.EMAIL_HOST_USER
                password = settings.EMAIL_HOST_PASSWORD

                message = MIMEMultipart("alternative")
                message["Subject"] = "Password Reset - Complementary Education System"
                message["From"] = sender_email
                message["To"] = email

                # Create the plain-text version of your message
                text = f"""
                Hello {user.first_name},
                
                We received a request to reset your password for your account at the Complementary Education System.
                To reset your password, click on the following link:
                
                {reset_link}
                
                If you didn't request a password reset, you can ignore this email. Your password will remain unchanged.
                
                The password reset link is valid for 24 hours.
                
                Best regards,
                The Complementary Education System Team
                """
                
                part1 = MIMEText(text, "plain")
                message.attach(part1)

                with smtplib.SMTP_SSL(settings.EMAIL_HOST, settings.EMAIL_PORT) as server:
                    server.login(sender_email, password)
                    server.sendmail(sender_email, email, message.as_string())
                print(f"Password reset email sent via direct SMTP")
            except Exception as smtp_error:
                print(f"Error sending email via SMTP: {smtp_error}")
                # Don't fail - the token is still saved, user can be given the link directly
        
        return True, "Password reset instructions sent to your email"
    except User.DoesNotExist:
        # Still return success to prevent email enumeration attacks
        print(f"Password reset requested for non-existent email: {email}")
        return True, "If this email exists in our system, password reset instructions will be sent"
    except Exception as e:
        print(f"Error in password reset: {str(e)}")
        return False, str(e)


def validate_password_reset_token(token):
    """
    Validate that the token exists and has not expired
    Returns: user object or None
    """
    try:
        user = User.objects.get(password_reset_token=token)
        
        # Check if token has expired
        if user.password_reset_expires is None or user.password_reset_expires < timezone.now():
            return None
            
        return user
    except User.DoesNotExist:
        return None


def reset_password(token, new_password):
    """
    Reset the user's password if token is valid
    Returns: (success, message)
    """
    user = validate_password_reset_token(token)
    
    if not user:
        return False, "Invalid or expired reset link"
    
    # Set new password
    user.set_password(new_password)
    
    # Clear reset token fields
    user.password_reset_token = None
    user.password_reset_expires = None
    user.save()
    
    return True, "Password has been reset successfully" 