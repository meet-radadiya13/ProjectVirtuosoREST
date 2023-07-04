from rest_framework.permissions import BasePermission


class IsCompanyOwner(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['create', 'partial_update', 'destroy', 'update']:
            return request.user.is_owner
        else:
            return True
