from datetime import timedelta
from multiprocessing import Process

from django.conf import settings
from django.core import mail
from django.utils import timezone
from django.utils.crypto import get_random_string

from authentication.models import User


def send_registration_mail(email, password, ):
    connection = mail.get_connection()
    subject = "Welcome!"
    message = "We are glad to have you here! \n" \
              "Your credentials are \nEmail: " \
              + email + "\nPassword: " + password + "\n"
    email = mail.EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        connection=connection,
    )
    email.send()


def send_otp(email, otp, ):
    connection = mail.get_connection()
    subject = "Welcome!"
    message = "We are glad to have you here! \n" \
              "Your OTP is " + otp
    email = mail.EmailMessage(
        subject,
        message,
        settings.EMAIL_HOST_USER,
        [email],
        connection=connection,
    )
    email.send()


def generate_otp(user_id):
    user = User.objects.get(id=user_id)
    otp_code = get_random_string(length=6, allowed_chars='0123456789')
    user.otp = otp_code
    user.otp_created = timezone.now()
    user.save()
    email_process = Process(
        target=send_otp,
        args=(user.email, otp_code,)
    )
    email_process.start()
    return True


def verify_otp(user_id, otp):
    user = User.objects.get(id=user_id)
    if otp == user.otp and (
            user.otp_created + timedelta(minutes=10)) >= timezone.now():
        user.otp = None
        user.otp_created = None
        user.save()
        return True
    return False
