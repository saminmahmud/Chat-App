from django.shortcuts import render, redirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth import login, logout, authenticate

from .forms import *
from django.contrib import messages
from django.http import JsonResponse
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.contrib.auth.hashers import make_password

from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes

# from django.contrib.auth import get_user_model
# from django.utils.functional import LazyObject

# class LazyUserModel(LazyObject):
#     def _setup(self):
#         self._wrapped = get_user_model()
        
# User = LazyUserModel()
from django.conf import settings  
User = settings.AUTH_USER_MODEL


def UserRegistration(request):
    if not request.user.is_authenticated:
        if request.method == 'POST':
            email = request.POST.get('email')
            password1 = request.POST.get('password1')
            password2 = request.POST.get('password2')

            # Validate the email
            try:
                validate_email(email)
            except ValidationError:
                messages.error(request, 'Invalid email address.')
                return render(request, 'register.html')
            
            # Check if the email already exists
            if User.objects.filter(email=email).exists():
                messages.error(request, 'An account with this email already exists.')
                return render(request, 'register.html')

            # Validate passwords
            if not email or not password1 or not password2:
                messages.error(request, 'All fields are required.')
            elif password1 != password2:
                messages.error(request, 'Passwords do not match.')
            elif len(password1) < 8:
                messages.error(request, 'Password must contain at least 8 characters.')
            else:
                # Create the user object with is_active=False
                user = User.objects.create(
                    email=email,
                    username=email.split('@')[0],  # Set username from email
                    password=make_password(password1),  # Hash the password
                    is_active=False  # Set user as inactive initially
                )

                # Generate token and uid for email confirmation
                token = default_token_generator.make_token(user)
                uid = urlsafe_base64_encode(force_bytes(user.pk))

                # Get the domain name for the confirmation link
                confirm_link = f"https://talk-dlc8.onrender.com/active/{uid}/{token}/"  # Confirmation URL

                # Send the confirmation email
                email_subject = "Confirm Your Email"
                email_body = render_to_string('confirm_email.html', {'link': confirm_link})
                email = EmailMultiAlternatives(email_subject, '', to=[user.email])
                email.attach_alternative(email_body, "text/html")
                email.send()

                # Notify user to check email for confirmation
                messages.success(request, 'Check your email for Email Verification🎯')

                return redirect('login')  # Or any other page

        return render(request, 'register.html')
    else:
        return redirect('home')


# Activation view
def activate(request, uid64, token):
    try:
        # Decode the uid and retrieve the user
        uid = urlsafe_base64_decode(uid64).decode()
        user = User._default_manager.get(pk=uid)
    except (TypeError, ValueError, User.DoesNotExist):
        user = None

    # Check if the user exists and if the token is valid
    if user is not None and default_token_generator.check_token(user, token):
        user.is_active = True  # Activate the user
        user.save()
        messages.success(request, 'Your account has been activated! You can now log in.')
        return redirect('login')  # Redirect to login after activation
    else:
        messages.error(request, 'Invalid or expired activation link.')
        return redirect('register')  # Or any other page


def user_login(request):
    if not request.user.is_authenticated :
        if request.method == 'POST':
            form = AuthenticationForm(request, request.POST)
            if form.is_valid():
                email = form.cleaned_data['username']
                password = form.cleaned_data['password']
                user = authenticate(request, username=email, password=password)
                if user is not None:
                    login(request,user)
                    messages.success(request, 'Logged In Successfully')
                    return redirect('home')
        else:
            form=AuthenticationForm()
        return render(request, 'login.html', {'form':form})
    else:
        return redirect('home')


def UserLogout(request):
    logout(request)
    messages.success(request, 'Logout Successfully')
    return redirect('login')


def update_profile_picture(request):
    if request.method == 'POST' and request.FILES.get('profile_picture'):
        user = request.user 
        profile_picture = request.FILES['profile_picture'] 

        user.profile_picture = profile_picture
        user.save()
        messages.success(request, 'Profile picture updated successfully.')
        return JsonResponse({'success': True, 'message': 'Profile picture updated.'})
    return JsonResponse({'success': False, 'message': 'No image provided.'})

