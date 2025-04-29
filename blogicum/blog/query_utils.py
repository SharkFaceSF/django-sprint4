from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import redirect
from django.urls import reverse
from django.utils import timezone
from django.db.models import Count

from blog.models import Post


def get_posts(manager=Post.objects, only_published=True, with_comments=False):
    posts = manager.select_related('author', 'category', 'location')

    if only_published:
        posts = posts.filter(
            is_published=True,
            pub_date__lte=timezone.now(),
            category__is_published=True
        )

    if with_comments:
        posts = posts.annotate(comment_count=Count('comments'))

    return posts.order_by('-pub_date')


class PostBaseMixin:
    def get_queryset(self):
        return get_posts()


class OnlyAuthorMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        obj = self.get_object()
        return obj.author == self.request.user

    def handle_no_permission(self):
        post_id = self.kwargs.get('post_id')
        return redirect(
            reverse('blog:post_detail', kwargs={'post_id': post_id})
        )
