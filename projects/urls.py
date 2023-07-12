from rest_framework import routers

from projects.views import AuditHistoryViewSet, ProjectViewSet

routers = routers.DefaultRouter()
routers.register(r'projects', ProjectViewSet, basename='projects')
routers.register(
    r'audit_history', AuditHistoryViewSet,
    basename='audit_history'
    )
urlpatterns = [
]

urlpatterns += routers.urls
