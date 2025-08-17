from rest_framework import viewsets, permissions
from rest_framework.filters import SearchFilter 
from .models import Course, Module
from .serializers import CourseSerializer, ModuleSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly] # User biasa bisa lihat, hanya admin bisa edit

    filter_backends = [SearchFilter]
    search_fields = ['title', 'instructor', 'description'] # Atribut yang bisa dicari

    def get_permissions(self):
        # Hanya admin yang bisa create, update, delete [cite: 145]
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAdminUser] # Hanya admin yang bisa CRUD module [cite: 158]