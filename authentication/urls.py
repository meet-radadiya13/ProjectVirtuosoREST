from rest_framework import routers

from authentication.views import (UserViewSet)

routers = routers.DefaultRouter()
routers.register(r'users', UserViewSet, basename='users')
urlpatterns = [
]
urlpatterns += routers.urls
