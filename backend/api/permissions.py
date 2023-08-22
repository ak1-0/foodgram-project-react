from rest_framework import permissions


class IsAdminOrAuthorOrReadOnly(permissions.BasePermission):
    """
    Разрешение: админ, автор или только чтение для
    аутентифицированных пользователей.
    """
    def has_permission(self, request, view):
        """
        Проверка прав доступа на уровне представления.
        """
        return (request.method in permissions.SAFE_METHODS
                or request.user.is_authenticated)

    def has_object_permission(self, request, view, obj):
        """
        Проверка прав доступа к объекту.
        """
        return (request.method in permissions.SAFE_METHODS
                or obj.author == request.user
                or request.user.is_superuser
                or request.user.is_staff)
