from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    admin = 'admin'
    user = 'user'
    moderator = 'moderator'
    CHOICES_ROLE = [
        (admin, 'Администратор'),
        (user, 'Пользователь'),
        (moderator, 'Модератор'),
    ]
    email = models.EmailField(
        _('email'),
        unique=True,
        max_length=254,
    )
    bio = models.TextField(verbose_name='Биография', blank=True)
    role = models.CharField(
        verbose_name='Роль позователя',
        max_length=15,
        choices=CHOICES_ROLE,
        default=user,
    )
    confirmation_code = models.CharField(max_length=50, blank=True)
    REQUIRED_FIELDS = ['email']

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    @property
    def is_admin(self):
        return self.role == 'admin'

    @property
    def is_moder(self):
        return self.role == 'moderator'

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        constraints = [models.UniqueConstraint(
            fields=('username', 'email'),
            name='Поля `email` и `username` должны быть уникальными.'), ]
