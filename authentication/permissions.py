from rest_framework.permissions import BasePermission


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_owner
