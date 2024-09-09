from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    pass

class Fingerprint(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    descriptors = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username}'s fingerprint data"