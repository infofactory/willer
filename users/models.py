from django.db import models
from django.contrib.auth.models import User

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    profile = models.JSONField()

    def __str__(self):
        return self.user.username
    
    class Meta:
        verbose_name = 'User Profile'
        verbose_name_plural = 'User Profiles'

