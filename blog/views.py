from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
import sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.db.models import Count, Q

from django.views.generic import ListView, CreateView, DetailView, DeleteView, UpdateView

from blog.forms import PostCreateForm, NewCommentForm
from blog.models import *
from users.models import Follow
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from operator import attrgetter
from django.contrib import messages


def is_users(post_user, logged_user):
    return post_user == logged_user


PAGINATION_COUNT = 3


# Create your views here.


# ################# Post List View (Start) ################# #
class PostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/home.html'
    context_object_name = 'posts'
    ordering = ['-date_posted']
    paginate_by = PAGINATION_COUNT

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)

        all_users = []
        data_counter = Post.objects.values('author') \
                           .annotate(author_count=Count('author')) \
                           .order_by('-author_count')[:6]

        for aux in data_counter:
            all_users.append(Profile.objects.filter(pk=aux['author']).first())
        # if Preference.objects.get(user = self.request.user):
        #     data['preference'] = True
        # else:
        #     data['preference'] = False
        data['preference'] = Preference.objects.all()
        # print(Preference.objects.get(user= self.request.user))
        data['all_users'] = all_users
        print(all_users, file=sys.stderr)
        return data

    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)
        follows = [user]
        for obj in qs:
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')


#####################################################


def get_post_queryset(query=None, req=None):
    queryset = []
    queries = query.split(" ")

    if len(query) != 0:
        for q in queries:
            posts = Post.objects.filter(
                Q(content__contains=q) | Q(content__icontains=q)).distinct()
            for post in posts:
                queryset.append(post)
    else:
        user = req.user
        follow_obj = Follow.objects.filter(user=user)

        follows = [user]

        for obj in follow_obj:
            follows.append(obj.follow_user)
            posts = Post.objects.filter(author__in=follows).order_by('-date_posted')
            for post in posts:
                queryset.append(post)

                # create unique set and then convert to list
    return list(set(queryset))


@login_required
def post_list_view(request):
    context = {}

    model = Post

    # Search
    query = ""
    if request.GET:
        query = request.GET.get('q', '')
        context['query'] = str(query)

    posts = sorted(get_post_queryset(query, request),
                   key=attrgetter('content'),
                   reverse=True)

    # posts = Post.objects.all()

    # Pagination
    page = request.GET.get('page', 1)
    posts_paginator = Paginator(posts, PAGINATION_COUNT)
    try:
        posts = posts_paginator.page(page)
    except PageNotAnInteger:
        posts = posts_paginator.page(PAGINATION_COUNT)
    except EmptyPage:
        posts = posts_paginator.page(posts_paginator.num_pages)

    context['posts'] = posts

    all_users = []

    data_counter = Post.objects.values('author') \
                       .annotate(author_count=Count('author')) \
                       .order_by('-author_count')[:6]

    for aux in data_counter:
        all_users.append(Profile.objects.filter(pk=aux['author']).first())
    # if Preference.objects.get(user = self.request.user):
    #     data['preference'] = True
    # else:
    #     data['preference'] = False
    context['preference'] = Preference.objects.all()
    # print(Preference.objects.get(user= self.request.user))
    context['all_users'] = all_users
    # print(all_users, file=sys.stderr)

    if posts:
        pass
    else:
        messages.success(request, "There is to relevent available")

    return render(request, 'blog/home.html', context)


################# Post List View (End) ################# #


# ################# Post Create View (Start) ################# #

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    fields = ['content']
    template_name = 'blog/post_new.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Add a new post'
        return data


#####################################################

@login_required
def post_create_view(request):
    context = {}

    user = request.user
    form = PostCreateForm()
    if request.method == 'POST':
        form = PostCreateForm(request.POST)  # or None, request.FILES or None)
        if form.is_valid():
            obj = form.save(commit=False)
            author = request.user
            obj.author = author
            obj.save()
            messages.success(request, "Posted your Content.")
            return redirect('home')
        else:
            messages.success(request, "Post was not posted for an unknown error!!")

    context["form"] = form

    return render(request, "blog/post_new.html", context)


# ################# Post Create View (End) ################# #


# ################# User Post List View (Start) ################# #
class UserPostListView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'blog/user_posts.html'
    context_object_name = 'posts'
    paginate_by = PAGINATION_COUNT

    def visible_user(self):
        return get_object_or_404(Profile, username=self.kwargs.get('username'))

    def get_context_data(self, **kwargs):
        visible_user = self.visible_user()
        logged_user = self.request.user
        print(logged_user.username == '', file=sys.stderr)

        if logged_user.username == '' or logged_user is None:
            can_follow = False
        else:
            can_follow = (Follow.objects.filter(user=logged_user,
                                                follow_user=visible_user).count() == 0)
        data = super().get_context_data(**kwargs)

        data['user_profile'] = visible_user
        data['can_follow'] = can_follow
        return data

    def get_queryset(self):
        user = self.visible_user()
        return Post.objects.filter(author=user).order_by('-date_posted')

    def post(self, request, *args, **kwargs):
        if request.user.id is not None:
            follows_between = Follow.objects.filter(user=request.user,
                                                    follow_user=self.visible_user())

            if 'follow' in request.POST:
                new_relation = Follow(user=request.user, follow_user=self.visible_user())
                if follows_between.count() == 0:
                    new_relation.save()
            elif 'unfollow' in request.POST:
                if follows_between.count() > 0:
                    follows_between.delete()

        return self.get(self, request, *args, **kwargs)


#################################################################

# def user_post_list_view(request):

# ################# User Post List View (End) ################# #


# ################# Post Detail List View (Start) ################# #

class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        comments_connected = Comment.objects.filter(post_connected=self.get_object()).order_by('-date_posted')
        data['comments'] = comments_connected
        data['form'] = NewCommentForm(instance=self.request.user)
        return data

    def post(self, request, *args, **kwargs):
        new_comment = Comment(content=request.POST.get('content'),
                              author=self.request.user,
                              post_connected=self.get_object())
        new_comment.save()

        return self.get(self, request, *args, **kwargs)


# ################# Post Detail List View (End) ################# #


# ################# Follows List View (Start) ################# #

class FollowsListView(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(Profile, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'follows'
        return data


# ################# Follows List View (End) ################# #


# ################# Followers List View (Start) ################# #

class FollowersListView(ListView):
    model = Follow
    template_name = 'blog/follow.html'
    context_object_name = 'follows'

    def visible_user(self):
        return get_object_or_404(Profile, username=self.kwargs.get('username'))

    def get_queryset(self):
        user = self.visible_user()
        return Follow.objects.filter(follow_user=user).order_by('-date')

    def get_context_data(self, *, object_list=None, **kwargs):
        data = super().get_context_data(**kwargs)
        data['follow'] = 'followers'
        return data


# ################# Followers List View (End) ################# #


# ################# Post Delete View (Start) ################# #

class PostDeleteView(LoginRequiredMixin, UserPassesTestMixin, DeleteView):
    model = Post
    template_name = 'blog/post_delete.html'
    context_object_name = 'post'
    success_url = '/'

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)
# ################# Post Delete View (End) ################# #


# ################# Post Update View (Start) ################# #
class PostUpdateView(LoginRequiredMixin, UserPassesTestMixin, UpdateView):
    model = Post
    fields = ['content']
    template_name = 'blog/post_new.html'
    success_url = '/'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def test_func(self):
        return is_users(self.get_object().author, self.request.user)

    def get_context_data(self, **kwargs):
        data = super().get_context_data(**kwargs)
        data['tag_line'] = 'Edit a post'
        return data
# ################# Post Update View (End) ################# #



# ################# Like Functionality View (Start) ################# #
@login_required
def postpreference(request, postid, userpreference):
    if request.method == "POST":
        eachpost = get_object_or_404(Post, id=postid)
        obj = ''
        valueobj = ''
        try:
            obj = Preference.objects.get(user=request.user, post=eachpost)
            valueobj = obj.value
            valueobj = int(valueobj)
            userpreference = int(userpreference)
            if valueobj != userpreference:
                obj.delete()
                upref = Preference()
                upref.user = request.user
                upref.post = eachpost
                upref.value = userpreference
                if userpreference == 1 and valueobj != 1:
                    eachpost.likes += 1
                    eachpost.dislikes -= 1
                elif userpreference == 2 and valueobj != 2:
                    eachpost.dislikes += 1
                    eachpost.likes -= 1
                upref.save()
                eachpost.save()
                context = {'eachpost': eachpost, 'postid': postid}
                return redirect('blog-home')
            elif valueobj == userpreference:
                obj.delete()
                if userpreference == 1:
                    eachpost.likes -= 1
                elif userpreference == 2:
                    eachpost.dislikes -= 1
                eachpost.save()
                context = {'eachpost': eachpost, 'postid': postid}
                return redirect('blog-home')

        except Preference.DoesNotExist:
            upref = Preference()
            upref.user = request.user
            upref.post = eachpost
            upref.value = userpreference
            userpreference = int(userpreference)
            if userpreference == 1:
                eachpost.likes += 1
            elif userpreference == 2:
                eachpost.dislikes += 1
            upref.save()
            eachpost.save()

            context = {'post': eachpost, 'postid': postid}

            return redirect('blog-home')

    else:
        eachpost = get_object_or_404(Post, id=postid)
        context = {'eachpost': eachpost, 'postid': postid}

        return redirect('home')

# ################# Like Functionality View (End) ################# #
