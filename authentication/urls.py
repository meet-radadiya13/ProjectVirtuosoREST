from django.urls import path
from rest_framework import routers

from authentication.views import (RenderHomeView, UserViewSet)

routers = routers.DefaultRouter()
routers.register(r'users', UserViewSet, basename='users')
urlpatterns = [
    path('home/', RenderHomeView.as_view(), name='home'),
]
urlpatterns += routers.urls
