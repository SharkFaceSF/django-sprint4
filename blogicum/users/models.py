from django.contrib.auth.models import User
from django.db import models


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField('Биография', blank=True, max_length=500)

    def __str__(self):
        return f'Профиль {self.user.username}'