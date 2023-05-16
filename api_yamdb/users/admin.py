from django.contrib import admin

from api_yamdb.settings import EMPTY_VALUE_DISPLAY

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    """Создает атрибуты для работы с пользователями в панели администратора"""
    list_display = ('pk', 'first_name', 'last_name', 'bio', 'email', 'role',)
    list_editable = ('role',)
    search_fields = ('email',)
    list_filter = ('role',)
    empty_value_display = EMPTY_VALUE_DISPLAY
