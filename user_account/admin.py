from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import CustomUser
from .forms import CustomUserCreationForm, CustomUserChangeForm

class CustomUserAdmin(BaseUserAdmin):
    model = CustomUser
    # Define the fields to display on the admin list page
    list_display = ('username', 'id', 'email', 'is_staff', 'is_superuser', 'is_active')
    # Define the fields to be used for filtering
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    # Define the fields to be displayed on the user detail page
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal info', {'fields': ('username', 'profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser')}),
        ('Important dates', {'fields': ('last_login', 'date_joined')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'password1', 'password2')}
        ),
    )
    readonly_fields = ('date_joined', 'last_login')  # Add readonly fields here
    form = CustomUserChangeForm
    add_form = CustomUserCreationForm
    filter_horizontal = ()  # Ensure this is empty if not using groups/permissions

admin.site.register(CustomUser, CustomUserAdmin)
