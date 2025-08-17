from django.db import models
from users.models import CustomUser

# Create your models here.
class Course(models.Model):
    title = models.CharField(max_length=200) # [cite: 148]
    description = models.TextField() # [cite: 149]
    instructor = models.CharField(max_length=100) # [cite: 150]
    topics = models.JSONField() # [cite: 151]
    price = models.DecimalField(max_digits=10, decimal_places=2) # [cite: 152]
    thumbnail_image = models.URLField(max_length=200, null=True, blank=True) # [cite: 153]
    created_at = models.DateTimeField(auto_now_add=True) # [cite: 154]
    updated_at = models.DateTimeField(auto_now=True) # [cite: 155]

    def __str__(self):
        return self.title

class Module(models.Model):
    course = models.ForeignKey(Course, related_name='modules', on_delete=models.CASCADE) # [cite: 160]
    title = models.CharField(max_length=200) # [cite: 161]
    description = models.TextField() # [cite: 162]
    pdf_content = models.URLField(max_length=200, null=True, blank=True) # [cite: 163]
    video_content = models.URLField(max_length=200, null=True, blank=True)
    order = models.PositiveIntegerField() # [cite: 164]
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        # 'order' harus unik untuk setiap course [cite: 164]
        unique_together = ('course', 'order')
        ordering = ['order']

    def __str__(self):
        return f"{self.course.title} - {self.title}"

class UserCourse(models.Model):
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    course = models.ForeignKey(Course, on_delete=models.CASCADE)
    purchased_at = models.DateTimeField(auto_now_add=True)
    # --- Tambahkan field di bawah ini ---
    completion_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        unique_together = ('user', 'course')

class UserModuleProgress(models.Model):
    user_course = models.ForeignKey(UserCourse, related_name='progress', on_delete=models.CASCADE)
    module = models.ForeignKey(Module, on_delete=models.CASCADE)
    is_completed = models.BooleanField(default=False)

    class Meta:
        unique_together = ('user_course', 'module')