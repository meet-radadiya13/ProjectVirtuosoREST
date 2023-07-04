from rest_framework.permissions import BasePermission

from projects.models import Project


class IsProjectOwner(BasePermission):
    def has_permission(self, request, view):
        if view.action in ['update', 'partial_update', 'destroy']:
            project_id = view.kwargs.get('pk')
            project = Project.objects.get(pk=project_id)
            return project.created_by == request.user
        else:
            return True
