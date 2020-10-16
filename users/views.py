from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect

from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.contrib import messages
from django.contrib.auth import login, authenticate, logout

from django.contrib.messages.views import SuccessMessageMixin
from django.views.generic import CreateView, DetailView, UpdateView

from .models import Profile
from .forms import UserRegistrationForm, LoginForm, UserUpdateForm
from django.db.models import Q

# Create your views here.

# ################# User Creation View (Start) ################# #

# class UserCreateView(CreateView, SuccessMessageMixin):
#     """
#         Class to create new user profile
#     """
#     template_name = "users/register.html"
#     success_url = reverse_lazy('login')
#     form_class = UserRegistrationForm
#     success_message = "Your profile was created successfully"


def user_create_view(request):
    context = {}
    if request.method == "POST":
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            messages.success(request, f'Account created for {username}.')
            account = authenticate(username=username, password=password)
            login(request, account)
            return redirect('home')
            # return redirect('register_users')
    else:
        form = UserRegistrationForm()
        context['form'] = form
    return render(request, 'users/register.html', context)


# ################# User Creation View (End) ################# #

# ################# Log In $ Log Out View (Start) ################# #


def logout_view(request):
    logout(request)
    return redirect('login')


def login_view(request):
    context = {}
    user = request.user

    if user.is_authenticated:
        return redirect("home")

    if request.POST:
        form = LoginForm(request.POST)
        if form.is_valid():
            username = request.POST["username"]
            password = request.POST["password"]
            user = authenticate(username=username, password=password)

            if user:
                login(request, user)
                return redirect("home")
    else:
        form = LoginForm()

    context["form"] = form
    return render(request, "users/login.html", context)


# ################# Log In $ Log Out View(End) ################# #

# ################# Profile View View(Start) ################# #


@login_required
def profile_view(request, pk):

    try:
        user = Profile.objects.get(pk=pk)
    except:
        user = Profile.objects.get(pk=request.user.pk)
        messages.success(request, "The profile you want Does Not Exist")

    if request.user.is_authenticated and request.user.pk == user.pk:
        form = UserUpdateForm(instance=user)
        model = Profile.objects.get(pk=user.pk)

        if request.method == 'POST':
            form = UserUpdateForm(request.POST, request.FILES, instance=user)

            if form.is_valid():
                try:
                    created_prof = form.save(commit=False)
                    created_prof.save()
                    messages.success(request, "Your profile is updated.")
                except:
                    messages.success(request, "Your profile was not updated.")
                return redirect('profile', pk=pk)
        else:
            form = UserUpdateForm(instance=user)
            model = Profile.objects.get(pk=user.pk)
            context = {'form': form, 'model': model, 'pk': pk}
        return render(request, 'users/profile.html', context)
    else:
        others_model = Profile.objects.get(pk=user.pk)
        others_form = UserUpdateForm(instance=user)
        context = {
            'others_form': others_form,
            'others_model': others_model,
        }
        messages.success(request,
                         "You are not authenticated to modify anything.")
        return render(request, 'users/profile.html', context)


# ################# Profile View View(End) ################# #


# ################# Serach View View (Start) ################# #
# @login_required
# def SearchView(request):
#     if request.method == 'POST':
#         kerko = request.POST.get('search')
#         print(kerko)
#         results = Profile.objects.filter(username__contains=kerko)
#         context = {
#             'results':results
#         }
#         return render(request, 'users/search_result.html', context)
# ################# Serach View View (End) ################# #
