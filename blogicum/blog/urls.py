from django.urls import path, include

from . import views

app_name = 'blog'

posts_patterns = [
    path('<int:post_id>/', views.PostDetailView.as_view(), name='post_detail'),
    path('create/', views.PostCreateView.as_view(), name='create_post'),
    path(
        '<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        '<int:post_id>/delete/',
        views.PostDeleteView.as_view(),
        name='delete_post'),
]

comments_patterns = [
    path('comment/', views.add_comment, name='add_comment'),
    path('edit_comment/<int:comment_id>/',
         views.edit_comment, name='edit_comment'),
    path('delete_comment/<int:comment_id>/',
         views.delete_comment, name='delete_comment'),
]

profile_patterns = [
    path('edit/', views.ProfileUpdateView.as_view(), name='edit_profile'),
    path('<str:username>/', views.ProfileView.as_view(), name='profile'),
]

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path('category/<slug:category_slug>/',
         views.CategoryPostsView.as_view(), name='category_posts'),
    path('profile/', include(profile_patterns)),
    path('posts/', include(posts_patterns)),
    path('posts/<int:post_id>/', include(comments_patterns)),
]
