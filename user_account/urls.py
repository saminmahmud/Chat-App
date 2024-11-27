from django.urls import path
from .views import *

urlpatterns = [
    path('register/', UserRegistration, name="register"),
    path('active/<uid64>/<token>/', activate, name = 'activate'),
    path('login/', user_login, name="login"),
    path('logout/', UserLogout, name="logout"),
    path('update_profile_picture/', update_profile_picture, name='update_profile_picture'),
]
