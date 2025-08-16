from django.contrib.auth.models import User
from rest_framework import serializers
from .models import Course, Module, Purchase, ModuleProgress, Certificate, UserProfile

class CourseSerializer(serializers.ModelSerializer):
    total_modules = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id","title","description","instructor","topics","price",
            "thumbnail_image","total_modules","created_at","updated_at"
        ]

class CourseListSerializer(serializers.ModelSerializer):
    total_modules = serializers.IntegerField(read_only=True)

    class Meta:
        model = Course
        fields = [
            "id","title","instructor","description","topics","price",
            "thumbnail_image","total_modules","created_at","updated_at"
        ]

class ModuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Module
        fields = [
            "id","course","title","description","order",
            "pdf_content","video_content","created_at","updated_at"
        ]
        read_only_fields = ["course"]

class ModuleDetailSerializer(serializers.ModelSerializer):
    is_completed = serializers.SerializerMethodField()

    class Meta:
        model = Module
        fields = [
            "id","course","title","description","order",
            "pdf_content","video_content","is_completed",
            "created_at","updated_at"
        ]

    def get_is_completed(self, obj):
        user = self.context.get("request").user
        if not user.is_authenticated:
            return False
        try:
            purchase = Purchase.objects.get(user=user, course=obj.course)
        except Purchase.DoesNotExist:
            return False
        return ModuleProgress.objects.filter(purchase=purchase, module=obj, is_completed=True).exists()

class MyCourseItemSerializer(serializers.ModelSerializer):
    progress_percentage = serializers.SerializerMethodField()
    purchased_at = serializers.DateTimeField(source="purchased_at")

    class Meta:
        model = Purchase
        fields = [
            "id","purchased_at",
            "course","progress_percentage",
        ]
        depth = 1  # include course fields

    def get_progress_percentage(self, obj):
        total = obj.course.total_modules
        if total == 0:
            return 0
        completed = ModuleProgress.objects.filter(purchase=obj, is_completed=True).count()
        return round(completed * 100 / total)

class UserSerializer(serializers.ModelSerializer):
    balance = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ["id","username","email","first_name","last_name","balance"]

    def get_balance(self, obj):
        return getattr(obj.profile, "balance", 0)

class UserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email","username","first_name","last_name","password"]
        extra_kwargs = {"password": {"write_only": True, "required": False}}

    def update(self, instance, validated_data):
        password = validated_data.pop("password", None)
        for k,v in validated_data.items():
            setattr(instance, k, v)
        if password:
            instance.set_password(password)
        instance.save()
        return instance