from rest_framework import routers

from projects.views import ProjectViewSet

routers = routers.DefaultRouter()
routers.register(r'projects', ProjectViewSet, basename='projects')
urlpatterns = [
]

urlpatterns += routers.urls
