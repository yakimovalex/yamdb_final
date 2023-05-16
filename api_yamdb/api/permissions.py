from rest_framework import permissions


class IsAuthorAdminModeratorOrReadOnly(permissions.BasePermission):
    message = 'Доступно на четение или админу, модератору и автору.'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            request.method in permissions.SAFE_METHODS
            or (obj.author == request.user or (
                request.user.is_authenticated
                and (
                    request.user.is_admin or request.user.is_moder
                    or request.user.is_staff)))
        )


class OnlyAdmin(permissions.BasePermission):
    message = 'Доступно только администратору.'

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and (request.user.is_admin or request.user.is_staff)
        )


class IsAdminOrReadOnly(permissions.BasePermission):
    message = 'Доступно на четение или только администратору.'

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or (request.user.is_authenticated and (
                request.user.is_admin or request.user.is_staff))
        )
