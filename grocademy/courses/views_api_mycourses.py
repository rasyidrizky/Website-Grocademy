# courses/views_api_mycourses.py

from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Course
from .serializers import CourseSerializer

class MyCoursesAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Mengambil queryset awal
        queryset = Course.objects.all()
        # Mengambil user yang sedang login
        user = self.request.user
        # Filter course berdasarkan course yang telah dibeli oleh user
        purchased_courses_ids = user.usercourse_set.values_list('course__id', flat=True)
        return queryset.filter(id__in=purchased_courses_ids)