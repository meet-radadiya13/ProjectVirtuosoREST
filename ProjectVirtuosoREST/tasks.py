from datetime import timedelta

from celery import shared_task
from django.contrib.auth import get_user_model
from django.utils import timezone

User = get_user_model()


@shared_task
def clear_otp(user_id):
    user = User.objects.get(id=user_id)
    if user.otp_created_at and (
            user.otp_created_at + timedelta(minutes=10)) <= timezone.now():
        user.otp_code = None
        user.otp_created_at = None
        user.save()
