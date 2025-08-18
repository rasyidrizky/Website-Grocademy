from django.contrib import admin
from django.contrib import admin
from .models import Course, Module, UserCourse, UserModuleProgress

# Register your models here.
admin.site.register(Course)
admin.site.register(Module)
admin.site.register(UserCourse)
admin.site.register(UserModuleProgress)