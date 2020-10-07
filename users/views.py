from django.shortcuts import render

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView

from .models import Profile
from .forms import UserRegistrationForm


# Create your views here.
class UserCreateView(CreateView, SuccessMessageMixin):
    template_name = "users/register.html"
    success_url = reverse_lazy('login')
    form_class = UserRegistrationForm
    success_message = "Your profile was created successfully"


