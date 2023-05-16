from django.db.models import Avg
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import MethodNotAllowed
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from reviews.models import Category, Genre, Review, Title
from users.models import User

from .filters import TitleFilter
from .permissions import (IsAdminOrReadOnly, IsAuthorAdminModeratorOrReadOnly,
                          OnlyAdmin)
from .serializers import (CategorySerializer, CommentsSerializer,
                          GenreSerializer, ObtainTokenSerializer,
                          ReviewsSerializer, TitleSerializer,
                          UserRegistrationSerializer, UserSerializer)
from .utils import send_email_with_code


class UserRegistrationAPIView(APIView):
    """Создает аккаунт пользователя в БД и отправляет
     на почту код подтверждения для получения токена."""

    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if not User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).exists():
            if serializer.is_valid(raise_exception=True):
                serializer.save()
        user = get_object_or_404(
            User,
            username=request.data.get('username'),
            email=request.data.get('email'))
        confirmation_code = send_email_with_code(request.data.get('email'))
        user.confirmation_code = confirmation_code
        user.save()
        return Response(request.data, status=status.HTTP_200_OK)


class UserGetTokenAPIView(APIView):
    """Отправляет пользователю токен
     в случае верного кода подтверждения."""

    def post(self, request):
        serializer = ObtainTokenSerializer(data=request.data)
        if serializer.is_valid(raise_exception=True):
            username = request.data.get('username')
            confirmation_code = request.data.get('confirmation_code')
            user = get_object_or_404(User, username=username)
            if confirmation_code == user.confirmation_code:
                refresh = RefreshToken.for_user(user)
                return Response({
                    'token': str(refresh.access_token)},
                    status=status.HTTP_201_CREATED)
            return Response({'message': 'Неверный код активации'},
                            status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    """Позволяет просматривать собственные данные пользователя и изменять их.
     Позволяет администратору создавать пользователей
      и изменять их информацию."""

    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (OnlyAdmin, )
    lookup_field = 'username'
    filter_backends = (filters.SearchFilter,)
    search_fields = ('username', )

    def update(self, request, pk=None, *args, **kwargs):
        if request.method == 'PUT':
            raise MethodNotAllowed(method='PUT')
        return super().update(request, *args, **kwargs)

    @action(
        detail=False,
        url_path='me',
        methods=['GET', 'PATCH'],
        permission_classes=(permissions.IsAuthenticated,))
    def me(self, request):
        serializer = self.get_serializer(request.user)
        if request.method == 'PATCH':
            serializer = self.get_serializer(
                request.user,
                data=request.data,
                partial=True)
            if serializer.is_valid(raise_exception=True):
                serializer.save(role=request.user.role)
                return Response(serializer.data,
                                status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TitleViewSet(viewsets.ModelViewSet):
    """Отправляет информацию о произведениях.
     Создавать произведения может только администратор."""

    queryset = Title.objects.all().annotate(
        Avg('reviews__score')).order_by('name')
    serializer_class = TitleSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filterset_class = TitleFilter


class CategoryViewSet(viewsets.ModelViewSet):
    """Отправляет информацию о категориях.
     Создавать категории может только администратор."""

    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class GenreViewSet(viewsets.ModelViewSet):
    """Отправляет информацию о жанрах.
     Создавать новые жанры может только администратор."""

    queryset = Genre.objects.all()
    serializer_class = GenreSerializer
    permission_classes = (IsAdminOrReadOnly, )
    filter_backends = (filters.SearchFilter, )
    search_fields = ('name', )
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)

    def update(self, request, *args, **kwargs):
        return Response(status=status.HTTP_405_METHOD_NOT_ALLOWED)


class ReviewsViewSet(viewsets.ModelViewSet):
    """Отправляет отзывы на произведение.
     Авторы могут редактировать свои отзывы.
     Изменение всех отзывов доступно также модератору и администратору."""

    serializer_class = ReviewsSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly, )

    def get_queryset(self):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        return title.reviews.all()

    def perform_create(self, serializer):
        title = get_object_or_404(Title, id=self.kwargs.get('title_id'))
        serializer.save(author=self.request.user, title=title)


class CommentsViewSet(viewsets.ModelViewSet):
    """Отправляет комментарии на отзывы.
     Авторы могут редактировать свои отзывы.
     Изменение всех отзывов доступно также модератору и администратору."""

    serializer_class = CommentsSerializer
    permission_classes = (IsAuthorAdminModeratorOrReadOnly, )

    def get_queryset(self):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        return review.comments.all()

    def perform_create(self, serializer):
        review = get_object_or_404(Review, id=self.kwargs.get('review_id'))
        serializer.save(author=self.request.user, review=review)
