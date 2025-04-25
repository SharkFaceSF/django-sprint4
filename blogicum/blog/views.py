from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.contrib.auth.mixins import UserPassesTestMixin
from django.contrib.auth import get_user_model

from .models import Category, Post
from .forms import PostForm


User = get_user_model()


class PostBaseMixin:
    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related('category', 'location', 'author')


class OnlyAuthorMixin(UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class PostListView(PostBaseMixin, ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10


class PostDetailView(PostBaseMixin, DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'


class CategoryPostsView(PostBaseMixin, ListView):
    template_name = 'blog/category.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(
            Category.objects.only('title', 'description'),
            slug=self.kwargs['category_slug'],
            is_published=True
        )
        return context

    def get_queryset(self):
        queryset = super().get_queryset()
        return queryset.filter(
            category__slug=self.kwargs['category_slug']
        )


class ProfileView(ListView):
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])
        return Post.objects.filter(
            author=self.author,
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related('category', 'location', 'author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username})


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'blog/user.html'
    success_url = reverse_lazy('profile')

    def get_success_url(self):
        return reverse_lazy('blog:profile', kwargs={'username': self.request.user.username})

    def get_object(self, queryset=None):
        return self.request.user
