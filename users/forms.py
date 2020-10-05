from django import forms

from django.contrib.auth.models import Group
from django.contrib.auth.forms import ReadOnlyPasswordHashField, UserCreationForm

from .models import Profile


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(help_text='Required. Add a valid email address')

    class Meta:
        model = Profile
        fields = ['username', 'name', 'email', 'date_of_birth', 'password1', 'password2', 'is_active', 'is_superuser']

    # def clean_password2(self):
    #     # Check that the two password entries match
    #     password1 = self.cleaned_data.get('password1')
    #     password2 = self.cleaned_data.get('password2')
    #     if password1 and password2 and password1 != password2:
    #         raise forms.ValidationError("Passwords don't match")
    #     return password2


    # def save(self, commit=True):
    #     # Save the provided password in hashed format
    #     user = super().save(commit=False)
    #     user.set_password(self.cleaned_data["password1"])
    #     if commit:
    #         user.save()
    #     return user

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
            raise forms.ValidationError('Username "%s" is already in use.' % username)

    def clean_username(self):
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