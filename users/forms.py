from django import forms
from django.core.exceptions import ValidationError
from django.utils.translation import ugettext_lazy
from django.contrib.auth.forms import PasswordResetForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import get_user_model
import re

User = get_user_model()


class UserRegistrationForm(forms.ModelForm):
    '''Форма регистрации пользователя'''
    email = forms.EmailField(max_length=200)
    username = forms.CharField(max_length=150, label='Логин')
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password2 = forms.CharField(
        label='Повтор пароля', widget=forms.PasswordInput)
    error_css_class = 'error'

    class Meta:
        model = User
        fields = ('username', 'email', 'password', 'password2')

    def clean_email(self):
        '''Проверяем, что email уникальный'''
        email = self.cleaned_data['email'].strip()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('Данный email уже есть в БД!')
        return email

    def clean_username(self):
        '''Валидируем логин'''
        username = self.cleaned_data['username'].strip()
        if not re.match(r'^[a-zA-Z0-9_-]{3,16}$', username):
            raise ValidationError('Недопустимые символы в логине!')
        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('Данный логин уже кем-то используется!')

        return username

    def clean_password2(self):
        password2 = self.cleaned_data['password2'].strip()
        password = self.cleaned_data['password'].strip()
        if password2 != password:
            raise ValidationError('Введенные пароли не совпадают!')
        return password2


class EmailValidationOnForgotPassword(PasswordResetForm):

    def clean_email(self):
        '''Валидация в форме восстановления пароя'''
        email = self.cleaned_data['email']
        if not User.objects.filter(email__iexact=email, is_active=True).exists():
            msg = ugettext_lazy(
                "Пользователь с данным email не зарегистрирован!")
            self.add_error('email', msg)
        return email
