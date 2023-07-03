from django.conf import settings
from django.core import mail


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
