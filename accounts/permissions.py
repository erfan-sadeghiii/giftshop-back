from rest_framework import permissions

class IsOwnerOrAdmin(permissions.BasePermission):
    """
    Allows access only to users with role 'owner' or 'admin'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role in ['owner', 'admin']

class IsOwner(permissions.BasePermission):
    """
    Allows access only to users with role 'owner'.
    """
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.role == 'owner'
