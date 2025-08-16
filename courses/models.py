from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid

# Create your models here.
class FileModelMixin(models.Model):
    """Mixin untuk auto-handle file update/delete"""
    class Meta:
        abstract = True

    def _delete_file(self, fieldfile):
        """Hapus file jika ada"""
        try:
            if fieldfile and fieldfile.storage.exists(fieldfile.name):
                fieldfile.storage.delete(fieldfile.name)
        except Exception:
            pass

    def replace_file(self, field_name, new_file):
        old_file = getattr(self, field_name)
        if old_file and old_file != new_file:
            self._delete_file(old_file)
        setattr(self, field_name, new_file)

    def delete(self, *args, **kwargs):
        """Hapus semua file sebelum delete object"""
        for field in self._meta.get_fields():
            if isinstance(field, models.FileField):
                self._delete_file(getattr(self, field.name))
        super().delete(*args, **kwargs)

class Course(FileModelMixin):
    title = models.CharField(max_length=200)
    description = models.TextField()
    instructor = models.CharField(max_length=200)
    topics = models.JSONField(default=list)
    price = models.PositiveIntegerField(validators=[MinValueValidator(0)])
    thumbnail_image = models.ImageField(upload_to="courses/%Y/%m/%d/thumb/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def total_modules(self):
        return self.modules.count()

    @staticmethod
    def thumbnail_path(instance, filename):
        return f"courses/{instance.id or 'new'}/thumb/{uuid.uuid4()}_{filename}"

    def __str__(self):
        return self.title

class Module(FileModelMixin):
    course = models.ForeignKey(Course, on_delete=models.CASCADE, related_name="modules")
    title = models.CharField(max_length=200)
    description = models.TextField()
    order = models.PositiveIntegerField()
    pdf_content = models.FileField(upload_to="courses/modules/pdf/", blank=True, null=True)
    video_content = models.FileField(upload_to="courses/modules/video/", blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("course", "order")
        ordering = ["order", "id"]

    @staticmethod
    def pdf_path(instance, filename):
        return f"courses/{instance.course.id}/modules/{instance.id or 'new'}/pdf/{uuid.uuid4()}_{filename}"

    @staticmethod
    def video_path(instance, filename):
        return f"courses/{instance.course.id}/modules/{instance.id or 'new'}/video/{uuid.uuid4()}_{filename}"

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class UserCourse(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    enrolled_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user","course")