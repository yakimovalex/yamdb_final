import django_filters
from reviews.models import Title


class TitleFilter(django_filters.FilterSet):
    """Фильтры для класса Title"""
    genre = django_filters.CharFilter(field_name='genre', lookup_expr='slug')
    category = django_filters.CharFilter(field_name='category',
                                         lookup_expr='slug')

    class Meta:
        model = Title
        fields = ['genre', 'category', 'year', 'name']
