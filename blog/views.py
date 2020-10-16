from django.shortcuts import render
from django.http import HttpResponse

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import ListView

from blog.models import *


def is_users(post_user, logged_user):
    return post_user == logged_user

PAGINATION_COUNT = 3

# Create your views here.

def post_list_view(request):
    return render(request, 'blog/home.html')



# class PostListView(LoginRequiredMixin, ListView):




