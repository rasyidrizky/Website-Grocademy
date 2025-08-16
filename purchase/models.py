from django.db import models
from django.contrib.auth.models import User
import uuid
from courses.models import Course, Module, FileModelMixin

# Create your models here.
class Purchase(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="purchases")
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="purchases")
    purchased_at = models.DateTimeField(auto_now_add=True)
    transaction_id = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)

    class Meta:
        unique_together = ("user", "course")

    def __str__(self):
        return f"{self.user.username} - {self.course.title}"

class ModuleProgress(models.Model):
    purchase = models.ForeignKey(Purchase, on_delete=models.CASCADE, related_name="progresses")
    module = models.ForeignKey(Module, on_delete=models.CASCADE, related_name="progresses")
    is_completed = models.BooleanField(default=False)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        unique_together = ("purchase", "module")

    def __str__(self):
        return f"{self.purchase.user.username} - {self.module.title} - {'Done' if self.is_completed else 'Pending'}"

class Certificate(FileModelMixin):
    purchase = models.OneToOneField(Purchase, on_delete=models.CASCADE, related_name="certificate")
    file = models.FileField(upload_to="certificates/")
    generated_at = models.DateTimeField(auto_now_add=True)

    @staticmethod
    def certificate_path(instance, filename):
        return f"certificates/{instance.purchase.id}/{uuid.uuid4()}_{filename}"

    def __str__(self):
        return f"Certificate: {self.purchase.user.username} - {self.purchase.course.title}"