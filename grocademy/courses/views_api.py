from rest_framework import viewsets, permissions, status
from rest_framework.filters import SearchFilter 
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Course, Module
from .serializers import CourseSerializer, ModuleSerializer

class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all()
    serializer_class = CourseSerializer
    permission_classes = [permissions.IsAuthenticated]

    filter_backends = [SearchFilter]
    search_fields = ['title', 'instructor', 'description']

    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [permissions.IsAdminUser()]
        return super().get_permissions()

class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all()
    serializer_class = ModuleSerializer
    permission_classes = [permissions.IsAdminUser]
    
class CourseCountView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, _request, *_args, **_kwargs):
        count = Course.objects.count()
        return Response({'total_courses': count}, status=status.HTTP_200_OK)