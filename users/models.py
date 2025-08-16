from django.contrib.auth.models import User
from django.db import models
from courses.models import FileModelMixin

# Create your models here.
class UserProfile(FileModelMixin):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    balance = models.PositiveIntegerField(default=0)
    avatar = models.ImageField(upload_to="users/avatars/", blank=True, null=True)

    @staticmethod
    def avatar_path(instance, filename):
        import uuid
        return f"users/{instance.user.id}/avatars/{uuid.uuid4()}_{filename}"

    def __str__(self):
        return f"{self.user.username} Profile"