from django.urls import path
from blog.views import *

urlpatterns = [
    # path('', PostListView.as_view(), name='home'),
    path('', post_list_view, name='home'),

    path('post/new/', PostCreateView.as_view(), name='post-create'),
]
