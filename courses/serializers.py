from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Course, Module

class ModuleSer(serializers.ModelSerializer):
    class Meta: model = Module; fields = "__all__"

class CourseSer(serializers.ModelSerializer):
    modules = ModuleSer(many=True, read_only=True)
    class Meta: model = Course; fields = "__all__"

class UserSer(serializers.ModelSerializer):
    class Meta: model = User; fields = ["id","username","email"]
