from django.shortcuts import get_object_or_404, redirect, render
from django.http import HttpResponse
import sys

from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count, Q

from django.views.generic import ListView

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
        context = super().get_context_data(**kwargs)

        all_users = []

        context_counter = Post.objects.values('author') \
            .annotate(author_count=Count('author')) \
                .order_by('-author_count')[:6]

        for aux in context_counter:
            all_users.append(Profile.objects.filter(pk=aux['author']).first())

        context['preference'] = Preference.objects.all()

        context["all_users"] = all_users
        print(all_users, file=sys.stderr)
        return context

    def get_queryset(self):
        user = self.request.user
        qs = Follow.objects.filter(user=user)

        follows = [user]

        for obj in qs:
            follows.append(obj.follow_user)
        return Post.objects.filter(author__in=follows).order_by('-date_posted')

        return super().get_queryset()


#####################################################


def get_post_queryset(query=None, req=None):
    queryset = []
    queries = query.split(" ")
    
    for q in queries:
        posts = Post.objects.filter(
            Q(content__contains=q) | Q(content__icontains=q)).distinct()
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

    if posts:
        pass
    else:
        messages.success(
            request, "There is to relevent results available you searched for")

    return render(request, 'blog/home.html', context)


################# Post List View (End) ################# #

################# Like Functionality View (Start) ################# #
# @login_required
# def postpreference(request, postid, userpreference):
#     if request.method == "POST":
#         eachpost = get_object_or_404(Post, id=postid)
#         obj = ''
#         valueobj = ''
#         try:
#             obj = Preference.objects.get(user=request.user, post=eachpost)
#             valueobj = obj.value
#             valueobj = int(valueobj)
#             userpreference = int(userpreference)
#             if valueobj != userpreference:
#                 obj.delete()
#                 upref = Preference()
#                 upref.user = request.user
#                 upref.post = eachpost
#                 upref.value = userpreference
#                 if userpreference == 1 and valueobj != 1:
#                     eachpost.likes += 1
#                     eachpost.dislikes -= 1
#                 elif userpreference == 2 and valueobj != 2:
#                     eachpost.dislikes += 1
#                     eachpost.likes -= 1
#                 upref.save()
#                 eachpost.save()
#                 context = {'eachpost': eachpost, 'postid': postid}
#                 return redirect('blog-home')
#             elif valueobj == userpreference:
#                 obj.delete()
#                 if userpreference == 1:
#                     eachpost.likes -= 1
#                 elif userpreference == 2:
#                     eachpost.dislikes -= 1
#                 eachpost.save()
#                 context = {'eachpost': eachpost, 'postid': postid}
#                 return redirect('blog-home')

#         except Preference.DoesNotExist:
#             upref = Preference()
#             upref.user = request.user
#             upref.post = eachpost
#             upref.value = userpreference
#             userpreference = int(userpreference)
#             if userpreference == 1:
#                 eachpost.likes += 1
#             elif userpreference == 2:
#                 eachpost.dislikes += 1
#             upref.save()
#             eachpost.save()

#             context = {'post': eachpost, 'postid': postid}

#             return redirect('blog-home')

#     else:
#         eachpost = get_object_or_404(Post, id=postid)
#         context = {'eachpost': eachpost, 'postid': postid}

#         return redirect('home')

# ################# Like Functionality View (End) ################# #
