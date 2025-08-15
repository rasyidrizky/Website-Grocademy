from rest_framework import viewsets, permissions
from django.contrib.auth.models import User
from .models import Course, Module
from .serializers import CourseSer, ModuleSer, UserSer

class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in ("GET", "HEAD", "OPTIONS"): return True
        return bool(request.user and request.user.is_staff)

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSer
    permission_classes = [IsAdminOrReadOnly]

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSer
    permission_classes = [IsAdminOrReadOnly]

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSer
    permission_classes = [permissions.IsAdminUser]
