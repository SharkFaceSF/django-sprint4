from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from . import views

app_name = 'blog'

urlpatterns = [
    path('', views.PostListView.as_view(), name='index'),
    path(
        'posts/<int:post_id>/',
        views.PostDetailView.as_view(),
        name='post_detail'
    ),
    path(
        'posts/create/',
        views.PostCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostUpdateView.as_view(),
        name='edit_post'
    ),
    path('category/<slug:category_slug>/', views.CategoryPostsView.as_view(),
         name='category_posts'),
    path('accounts/profile/edit/',
         views.ProfileUpdateView.as_view(),
         name='edit_profile'
         ),
    path(
        'accounts/profile/<str:username>/',
        views.ProfileView.as_view(),
        name='profile'
    ),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
