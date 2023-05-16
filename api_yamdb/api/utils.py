import uuid

from django.core.mail import send_mail

from api_yamdb.settings import EMAIL_HOST_USER


def send_email_with_code(email):
    """Отправка email с кодом подтверждения регистрации."""
    SUBJECT = 'Подтверждение регистрации Yamdb.'
    code = uuid.uuid4()
    MESSAGE = f'Your code: {code}'
    send_mail(
        SUBJECT,
        MESSAGE,
        EMAIL_HOST_USER,
        [email],
        fail_silently=False,
    )
    return code
