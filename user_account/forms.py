from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from .models import CustomUser
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.forms import AuthenticationForm

# from django.contrib.auth import get_user_model
# User = get_user_model()
from django.conf import settings  
User = settings.AUTH_USER_MODEL


class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username')

class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'username', 'profile_picture', 'is_active', 'is_staff', 'is_superuser')


# class UserRegistrationForm(UserCreationForm):
#     class Meta:
#         model = CustomUser
#         fields = ('email', 'password1', 'password2')

class UserRegistrationForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = ('email', 'password1', 'password2') 
        widgets = {
            'password1': forms.PasswordInput(),
            'password2': forms.PasswordInput(),
        }  

class CustomLoginForm(AuthenticationForm):
    username = forms.EmailField(label='Email')