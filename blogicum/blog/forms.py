from django import forms

from .models import Post, User, Comment


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        exclude = ('author',)


class ProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'username', 'email')


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('text',)
