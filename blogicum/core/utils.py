from django.utils import timezone
from django.db.models import Count
from blog.models import Post

LIMIT_POSTS = 10


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
