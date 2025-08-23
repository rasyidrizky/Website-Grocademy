from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Course, UserCourse
from .serializers import CourseSerializer, UserCourseSerializer 

class MyCoursesAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        purchased_course_ids = UserCourse.objects.filter(user=self.request.user).values_list('course_id', flat=True)
        return Course.objects.filter(id__in=purchased_course_ids)
    
class PurchaseHistoryAPIView(generics.ListAPIView):
    serializer_class = UserCourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCourse.objects.filter(user=self.request.user).order_by('-purchased_at')