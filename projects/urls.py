from rest_framework import routers

from projects.views import ProjectViewSet, TaskViewSet, AttachmentViewSet

routers = routers.DefaultRouter()
routers.register(r'projects', ProjectViewSet, basename='projects')
routers.register(r'tasks', TaskViewSet, basename='tasks')
routers.register(r'attachments', AttachmentViewSet, basename='tasks')
urlpatterns = [
]

urlpatterns += routers.urls
