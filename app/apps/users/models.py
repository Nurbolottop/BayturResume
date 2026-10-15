from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Своя модель с первого дня: после первой миграции заменить её почти невозможно."""

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
