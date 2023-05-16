import datetime as dt

from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models

User = get_user_model()


def not_future(val):
    if not (0 <= val <= dt.datetime.now().year):
        raise ValidationError('Не достижимая дата.')


class Category(models.Model):
    """Класс категорий."""

    name = models.CharField('Hазвание', max_length=256)
    slug = models.SlugField('slug', unique=True)

    class Meta:
        verbose_name = 'Категория'
        verbose_name_plural = 'Категории'
        ordering = ('name',)

    def __str__(self):
        return self.name[:15]


class Genre(models.Model):
    """Класс жанров."""

    name = models.CharField('Hазвание', max_length=75)
    slug = models.SlugField('slug', unique=True)

    class Meta:
        verbose_name = 'Жанр'
        verbose_name_plural = 'Жанры'
        ordering = ('name',)

    def __str__(self):
        return self.name[:15]


class Title(models.Model):
    """Класс произведений."""

    name = models.CharField('Hазвание', max_length=150)
    year = models.PositiveIntegerField(
        verbose_name='Год выпуска',
        db_index=True,
        validators=(
            not_future,
            # или ограничть в сериализаторе
            # как делал в предыдущей версии этого проекта
        ),
    )
    description = models.TextField('описание', blank=True)
    genre = models.ManyToManyField(
        Genre,
        verbose_name='жанр',
        through='GenreTitle',
        related_name='titles',
    )
    category = models.ForeignKey(
        Category,
        verbose_name='категория',
        on_delete=models.SET_NULL,
        related_name='titles',
        null=True
    )

    def clean(self) -> None:
        from django.core.exceptions import ValidationError
        if self.year > dt.datetime.now().year:
            raise ValidationError({'year': ('Enter Correct number.')})
        return super().clean()

    class Meta:
        verbose_name = 'Произведение'
        verbose_name_plural = 'Произведения'
        ordering = ('-year', 'name')

    def __str__(self):
        return self.name[:15]


class GenreTitle(models.Model):
    """Вспомогательный класс, связывающий жанры и произведения."""

    genre = models.ForeignKey(
        Genre,
        verbose_name='Жанр',
        on_delete=models.CASCADE,
    )
    title = models.ForeignKey(
        Title,
        verbose_name='произведение',
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Соответствие жанра и произведения'
        verbose_name_plural = 'Таблица соответствия жанров и произведений'
        ordering = ('id', )

    def __str__(self):
        return f'{self.title} принадлежит жанру/ам {self.genre}'


class Review(models.Model):  # Изменить название

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    title = models.ForeignKey(
        Title,
        verbose_name='Произведение',
        on_delete=models.CASCADE,
        related_name='reviews',
    )
    text = models.TextField(
        'Текст отзыва',
    )
    score = models.SmallIntegerField(
        'Оценка',
        validators=(
            MinValueValidator(1, message='Минимальная оценка 1'),
            MaxValueValidator(10, message='Максимальная оценка 10')
        )
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Отзыв'
        verbose_name_plural = 'Отзывы'
        ordering = ('-pub_date', )
        constraints = (
            models.UniqueConstraint(
                fields=('author', 'title'), name='unique_review'
            ),
        )

    def __str__(self):
        return self.text[:15]


class Comments(models.Model):

    author = models.ForeignKey(
        User,
        verbose_name='Автор',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    review = models.ForeignKey(
        Review,
        verbose_name='Отзыв',
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'Текст комментария',
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True
    )

    class Meta:
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
        ordering = ('-pub_date', )

    def __str__(self):
        return self.text[:15]
