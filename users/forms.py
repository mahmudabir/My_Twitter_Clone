from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm

from .models import Profile
from django.contrib.auth import authenticate


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text='Required. Add a valid email address')

    # date_of_birth = forms.DateInput()

    class Meta:
        model = Profile
        fields = ['username', 'name', 'email', 'date_of_birth', 'password1',
                  'password2',  # 'is_user', 'is_superuser',
                  ]

        widgets = {
            'date_of_birth': forms.DateInput(
                attrs={
                    'type': 'date'
                }
            )
        }


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = Profile
        fields = ['name', 'username', 'email', 'date_of_birth']

    def clean_username(self):
        if self.is_valid():
            username = self.cleaned_data['username']

            try:
                profile = Profile.objects.exclude(pk=self.instance.pk).get(username=username)
            except Profile.DoesNotExist:
                return username
            raise forms.ValidationError('Username "%s" is already in use.' %username)

    def clean_email(self):
        if self.is_valid():
            email = self.cleaned_data['email']

            try:
                profile = Profile.objects.exclude(pk=self.instance.pk).get(email=email)
            except Profile.DoesNotExist:
                return email
            raise forms.ValidationError('Email "%s" is already in use.' %email)


class ProfilePhotoUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ['image']


class LoginForm(forms.ModelForm):
    password = forms.CharField(label='Password', widget=forms.PasswordInput)

    class Meta:
        model = Profile
        fields = ['username', 'password']

    def clean(self):
        if self.is_valid():
            username = self.cleaned_data['username']
            password = self.cleaned_data['password']
            if not authenticate(username=username, password=password):
                raise forms.ValidationError("Invalid Login")
