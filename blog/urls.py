from django.urls import path
from blog.views import *

urlpatterns = [
    # path('', PostListView.as_view(), name='home'),
    path('', post_list_view, name='home'),

    # path('post/new/', PostCreateView.as_view(), name='post-create'),
    path('post/new/', post_create_view, name='post-create'),

    path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    # path('post/<int:pk>/', PostDetailView.as_view(), name='post-detail'),

    path('user/<str:username>', UserPostListView.as_view(), name='user-posts'),
    # path('user/<str:username>', user_post_list_view, name='user-posts'),

    path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),
    # path('post/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),

    path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),
    # path('post/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),

    path('user/<str:username>/follows', FollowsListView.as_view(), name='user-follows'),
    # path('user/<str:username>/follows', FollowsListView.as_view(), name='user-follows'),

    path('user/<str:username>/followers', FollowersListView.as_view(), name='user-followers'),
    # path('user/<str:username>/followers', FollowersListView.as_view(), name='user-followers'),

]
