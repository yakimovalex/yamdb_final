import re

from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.serializers import (IntegerField, ModelSerializer,
                                        ValidationError)
from reviews.models import Category, Comments, Genre, Review, Title
from users.models import User

REGEXP = r'^[\w.@+-]+\Z'


def valid_username(value):
    if not re.fullmatch(REGEXP, value) or value == 'me':
        raise serializers.ValidationError('Недопустимое имя!')
    return value


class UserRegistrationSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('username', 'email')
        model = User

    def validate_username(self, value):
        return valid_username(value)


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        fields = ('first_name', 'last_name',
                  'username', 'bio',
                  'role', 'email')
        model = User

    def validate_username(self, value):
        return valid_username(value)


class ObtainTokenSerializer(serializers.ModelSerializer):
    username = serializers.CharField(required=True, max_length=150)
    confirmation_code = serializers.CharField(required=True, max_length=50)

    class Meta:
        model = User
        fields = ('username', 'confirmation_code')


class CategorySerializer(serializers.ModelSerializer):

    class Meta:
        model = Category
        exclude = ('id',)


class GenreSerializer(serializers.ModelSerializer):

    class Meta:
        model = Genre
        fields = ('name', 'slug')


class CategoryTitle(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = CategorySerializer(value)
        return serializer.data


class GenreTitle(serializers.SlugRelatedField):
    def to_representation(self, value):
        serializer = GenreSerializer(value)
        return serializer.data


class TitleSerializer(serializers.ModelSerializer):

    genre = GenreTitle(slug_field='slug',
                       queryset=Genre.objects.all(),
                       many=True)
    category = CategoryTitle(slug_field='slug',
                             required=False,
                             queryset=Category.objects.all())
    rating = IntegerField(
        source='reviews__score__avg',
        read_only=True
    )

    class Meta:
        model = Title
        fields = ('id', 'name', 'year',
                  'description', 'genre',
                  'category', 'rating')


class ReviewsSerializer(ModelSerializer):
    author = serializers.SlugRelatedField(
        slug_field='username', read_only=True)

    class Meta:
        fields = '__all__'
        model = Review
        read_only_fields = ('title',)

    def validate(self, data):
        title_id = self.context.get('view').kwargs.get('title_id')
        author = self.context.get('request').user
        title = get_object_or_404(Title, id=title_id)
        if (title.reviews.filter(author=author).exists()
                and self.context.get('request').method != 'PATCH'):
            raise ValidationError(
                'Можно оставлять только один отзыв!'
            )
        return data


class CommentsSerializer(ModelSerializer):
    author = serializers.SlugRelatedField(
        read_only=True, slug_field='username')

    class Meta:
        fields = '__all__'
        model = Comments
        read_only_fields = ('review',)
