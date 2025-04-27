from django.views.generic import (
    ListView, DetailView, CreateView, UpdateView, DeleteView
)
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth.mixins import (
    LoginRequiredMixin,
    UserPassesTestMixin,
)
from django.urls import reverse_lazy
from django.contrib.auth import get_user_model
from django.http import HttpResponseForbidden

from .models import Category, Post, Comment
from .forms import PostForm, CommentForm
from django.db.models import Count


User = get_user_model()


class PostBaseMixin:
    def get_queryset(self):
        return Post.objects.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        ).select_related('category', 'location', 'author').order_by('-pub_date')


class OnlyAuthorMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user


class PostListView(PostBaseMixin, ListView):
    template_name = 'blog/index.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        return super().get_queryset().annotate(comment_count=Count('comments'))


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


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = User
    fields = ['first_name', 'last_name', 'username', 'email']
    template_name = 'blog/user.html'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )

    def get_object(self, queryset=None):
        return self.request.user


class ProfileView(ListView):
    template_name = 'blog/profile.html'
    context_object_name = 'post_list'
    paginate_by = 10

    def get_queryset(self):
        self.author = get_object_or_404(User, username=self.kwargs['username'])

        queryset = Post.objects.filter(
            author=self.author
        ).select_related('category', 'location', 'author').annotate(
            comment_count=Count('comments')
        ).order_by('-pub_date')

        if self.request.user != self.author:
            queryset = queryset.filter(
                pub_date__lte=timezone.now(),
                is_published=True,
                category__is_published=True
            )
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.author
        if not self.author.first_name:
            self.author.first_name = self.author.username
            self.author.save()
        return context


class PostDetailView(DetailView):
    template_name = 'blog/detail.html'
    context_object_name = 'post'
    pk_url_kwarg = 'post_id'

    def get_queryset(self):
        queryset = Post.objects.select_related('category', 'location', 'author')
        if self.request.user.is_authenticated and self.request.user == queryset.first().author:
            return queryset
        return queryset.filter(
            pub_date__lte=timezone.now(),
            is_published=True,
            category__is_published=True
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm()
        context['comments'] = self.object.comments.all().select_related('author')
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
            kwargs={'username': self.request.user.username}
        )


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def handle_no_permission(self):
        post_id = self.kwargs.get('post_id')
        if post_id:
            return redirect(reverse_lazy('blog:post_detail', kwargs={'post_id': post_id}))
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse_lazy(
            'blog:post_detail',
            kwargs={'post_id': self.object.id}
        )


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/post.html'
    pk_url_kwarg = 'post_id'
    context_object_name = 'post'

    def get_success_url(self):
        return reverse_lazy(
            'blog:profile',
            kwargs={'username': self.request.user.username})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_delete'] = True
        return context


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', post_id=post_id)


@login_required
def edit_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        form = CommentForm(request.POST, instance=comment)
        if form.is_valid():
            form.save()
            return redirect('blog:post_detail', post_id=post_id)
    else:
        form = CommentForm(instance=comment)

    return render(request, 'blog/comment.html', {
        'form': form,
        'comment': comment,
        'post_id': post_id
    })


@login_required
def delete_comment(request, post_id, comment_id):
    comment = get_object_or_404(Comment, pk=comment_id, post_id=post_id)
    if comment.author != request.user:
        return HttpResponseForbidden()

    if request.method == 'POST':
        comment.delete()
        return redirect('blog:post_detail', post_id=post_id)

    return render(request, 'blog/comment.html', {
        'comment': comment,
        'is_delete': True,
        'post_id': post_id
    })
