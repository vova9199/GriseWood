import re

from django import forms
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    password1 = forms.CharField(
        label="Пароль",
        strip=False,  # Allow leading/trailing whitespace
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введіть пароль'}),
        help_text="Мінімум 6 символів: латиниця та цифри"
    )

    password2 = forms.CharField(
        label="Підтвердіть пароль",
        strip=False,  # Allow leading/trailing whitespace
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Введіть пароль ще раз'}),
        help_text="Мінімум 6 символів: латиниця та цифри"
    )

    show_password = forms.BooleanField(required=False, initial=False,
                                       widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}))

    class Meta:
        model = CustomUser
        fields = ('last_name', 'first_name', 'patronymic', 'phone', 'email', 'username', 'password1', 'password2',
                  'show_password',
                  'role', 'is_staff', 'is_superuser')
        # fields = '__all__'
        widgets = {
            'last_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Бандера'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Степан'}),
            'patronymic': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Андрійович'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+380987654321 або 0987654321'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'example@gmail.com'}),
            'username': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'banderas1945'}),
            'password1': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Пароль'}),
            'password2': forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Підтвердіть пароль'}),
            'role': forms.Select(attrs={'class': 'form-control'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

    def __init__(self, *args, request=None, **kwargs):
        self.request = request
        super().__init__(*args, **kwargs)

        # Check if the user is authenticated, and if not, remove certain fields
        if not self.request.user.is_authenticated:
            del self.fields['is_staff']
            del self.fields['is_superuser']
            del self.fields['role']

        # # Disable the validation of password2
        # del self.fields['password2']

    def clean(self):
        cleaned_data = super().clean()

        # Check if the user is authenticated, and if not, validate the absence of certain fields
        if not self.request.user.is_authenticated:
            is_staff = cleaned_data.get('is_staff')
            is_superuser = cleaned_data.get('is_superuser')
            role = cleaned_data.get('role')

            if is_staff or is_superuser or role:
                raise forms.ValidationError('You are not allowed to set staff, superuser, or role.')

        return cleaned_data


class CustomUserUpdateForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = (
        'first_name', 'patronymic', 'last_name', 'phone', 'username', 'email', 'role', 'is_active', 'is_staff', 'is_superuser')

    def clean_password(self):
        password = self.cleaned_data.get('password')

        if password:
            # Проста валідація: латинські літери та цифри, не менше 6 символів
            if not re.match(r'^(?=.*[a-zA-Z])(?=.*\d).{6,}$', password):
                raise forms.ValidationError(
                    'Пароль повинен містити принаймні одну літеру та одну цифру, і бути не менше 6 символів довгим.'
                )

        return password


class CustomLoginForm(AuthenticationForm):
    username = forms.CharField(
        label="Username",
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your username'}),
    )
    password = forms.CharField(
        label="Password",
        strip=False,  # Allow leading/trailing whitespace
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'Enter your password'}),
    )
