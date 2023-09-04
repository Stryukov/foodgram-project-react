from rest_framework import permissions


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Доступ на изменение авторам, остальным на чтение.
    """

    def has_permission(self, request, view):
        return (
            request.method in permissions.SAFE_METHODS
            or request.user.is_authenticated
        )

    def has_object_permission(self, request, view, obj):
        return (
            obj.author == request.user
            or request.user.is_staff
        )


class IsAdmin(permissions.BasePermission):
    """
    Доступ пользователям с ролью superuser.
    """

    def has_permission(self, request, view):
        return (
            request.user.is_authenticated
            and request.user.is_superuser
        )


class ReadOnly(permissions.BasePermission):
    """
    Доступ к одному рецепту анонимному пользователю.
    """
    def has_permission(self, request, view):
        return request.method in permissions.SAFE_METHODS
