from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (CategoryViewSet, CommentsViewSet, GenreViewSet,
                    ReviewsViewSet, TitleViewSet, UserGetTokenAPIView,
                    UserRegistrationAPIView, UserViewSet)

router_v1 = DefaultRouter()
router_v1.register('users', UserViewSet, basename='users')
router_v1.register('categories', CategoryViewSet, basename='categories')
router_v1.register('genres', GenreViewSet, basename='genres')
router_v1.register('titles', TitleViewSet, basename='titles')
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews/(?P<review_id>\d+)/comments',
    CommentsViewSet, basename='comments'
)
router_v1.register(
    r'titles/(?P<title_id>\d+)/reviews', ReviewsViewSet, basename='viewsets'
)

urlpatterns = [
    path('v1/auth/signup/', UserRegistrationAPIView.as_view(), name='signup'),
    path('v1/auth/token/', UserGetTokenAPIView.as_view(), name='token'),
    path('v1/', include(router_v1.urls)),
]
