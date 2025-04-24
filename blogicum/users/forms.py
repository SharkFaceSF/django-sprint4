from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Profile


class UserRegisterForm(UserCreationForm):
    bio = forms.CharField(
        label='Биография',
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False,
        max_length=500
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'bio']

    def save(self, commit=True):
        user = super().save(commit=commit)
        Profile.objects.create(
            user=user,
            bio=self.cleaned_data['bio']
        )
        return user
