from django import forms
from django.contrib.auth.forms import AuthenticationForm

from apps.accounts.models import User


class UserLoginForm(AuthenticationForm):
    """Custom login form with styled widgets."""

    username = forms.CharField(
        label="Usuario",
        widget=forms.TextInput(
            attrs={
                "class": "form-control",
                "placeholder": "Nombre de usuario",
                "autofocus": True,
            }
        ),
    )
    password = forms.CharField(
        label="Contraseña",
        widget=forms.PasswordInput(
            attrs={
                "class": "form-control",
                "placeholder": "Contraseña",
            }
        ),
    )


class UserProfileForm(forms.ModelForm):
    """Form for editing user profile basic fields."""

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "phone", "avatar")
        labels = {
            "first_name": "Nombre",
            "last_name": "Apellido",
            "email": "Correo electrónico",
            "phone": "Teléfono",
            "avatar": "Avatar",
        }
        widgets = {
            "first_name": forms.TextInput(attrs={"class": "form-control"}),
            "last_name": forms.TextInput(attrs={"class": "form-control"}),
            "email": forms.EmailInput(attrs={"class": "form-control"}),
            "phone": forms.TextInput(attrs={"class": "form-control"}),
            "avatar": forms.ClearableFileInput(attrs={"class": "form-control"}),
        }
