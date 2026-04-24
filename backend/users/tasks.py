from celery import shared_task
from django.core.mail import send_mail
from django.conf import settings


@shared_task
def send_activation_key_email(email, activation_key):
    subject = "Ваш ключ активации"
    message = (
        "Здравствуйте!\n\n"
        f"Ваш ключ активации: {activation_key}\n\n"
        "Используйте его для подключения к прокси-серверу."
    )

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [email],
        fail_silently=False,
    )
