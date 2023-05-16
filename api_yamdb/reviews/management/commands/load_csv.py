"""Модуль для заполнения базы данных из документов формата .csv.
Данные в документах должны быть структурированны согласно модели
 и в качестве разделителя используется запятая.
 Для загрузки данные должны находиться по пути /static/data"""
import csv
from pathlib import Path

from django.conf import settings
from django.core.management.base import BaseCommand
from django.shortcuts import get_object_or_404
from reviews.models import Category, Comments, Genre, GenreTitle, Review, Title
from users.models import User


def read_csv(file_name: str):
    csv_path = Path(settings.BASE_DIR, 'static/data/', file_name)
    csv_file = open(csv_path, 'r', encoding='utf-8')
    reader = csv.reader(csv_file, delimiter=',')
    return reader


class Command(BaseCommand):
    """Парсер базы данных из файлов CSV."""
    help = 'load_csv'

    def handle(self, *args, **options):
        csv_reader = read_csv('category.csv')
        next(csv_reader, None)
        for row in csv_reader:
            obj, created = Category.objects.get_or_create(
                id=row[0],
                name=row[1],
                slug=row[2]
            )
        print('Категории - OK')

        csv_reader = read_csv('genre.csv')
        next(csv_reader, None)
        for row in csv_reader:
            obj, created = Genre.objects.get_or_create(
                id=row[0],
                name=row[1],
                slug=row[2]
            )
        print('Жанры - OK')

        csv_reader = read_csv('titles.csv')
        next(csv_reader, None)
        for row in csv_reader:
            obj_category = get_object_or_404(Category, id=row[3])
            obj, created = Title.objects.get_or_create(
                id=row[0],
                name=row[1],
                year=row[2],
                category=obj_category
            )
        print('Произведения - OK')

        csv_reader = read_csv('genre_title.csv')
        next(csv_reader, None)
        for row in csv_reader:
            obj_genre = get_object_or_404(Genre, id=row[2])
            obj_title = get_object_or_404(Title, id=row[1])
            obj, created = GenreTitle.objects.get_or_create(
                id=row[0],
                genre=obj_genre,
                title=obj_title
            )
        print('Жанры произведений - OK')

        csv_reader = read_csv('users.csv')
        next(csv_reader, None)
        for row in csv_reader:
            obj, created = User.objects.get_or_create(
                id=row[0],
                username=row[1],
                email=row[2],
                role=row[3],
                bio=row[4],
                first_name=row[5],
                last_name=row[6]
            )
        print('Пользователи - OK')

        csv_reader = read_csv('review.csv')
        next(csv_reader, None)
        for row in csv_reader:
            obj_title = get_object_or_404(Title, id=row[1])
            obj_user = get_object_or_404(User, id=row[3])
            obj, created = Review.objects.get_or_create(
                id=row[0],
                title=obj_title,
                text=row[2],
                author=obj_user,
                score=row[4],
                pub_date=row[5]
            )
        print('Отзывы - OK')

        csv_reader = read_csv('comments.csv')
        next(csv_reader, None)
        for row in csv_reader:
            obj_review = get_object_or_404(Review, id=row[1])
            obj_user = get_object_or_404(User, id=row[3])
            obj, created = Comments.objects.get_or_create(
                id=row[0],
                review=obj_review,
                text=row[2],
                author=obj_user,
                pub_date=row[4]
            )
        print('Комментарии - OK')
