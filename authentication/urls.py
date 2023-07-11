from django.urls import path
from rest_framework import routers

from authentication.views import (LoginView, OTPVerifyView, RenderHomeView,
                                  UserViewSet,
                                  )

routers = routers.DefaultRouter()
routers.register(r'users', UserViewSet, basename='users')
urlpatterns = [
    path('home/', RenderHomeView.as_view(), name='home'),
    path('login/', LoginView.as_view(), name='login'),
    path('otp/', OTPVerifyView.as_view(), name='otp'),
]
urlpatterns += routers.urls
