from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from .models import Course, UserCourse
from .serializers import CourseSerializer, UserCourseSerializer 

class MyCoursesAPIView(generics.ListAPIView):
    serializer_class = CourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = Course.objects.all()
        user = self.request.user
        purchased_courses_ids = user.usercourse_set.values_list('course__id', flat=True)
        return queryset.filter(id__in=purchased_courses_ids)
    
class PurchaseHistoryAPIView(generics.ListAPIView):
    serializer_class = UserCourseSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return UserCourse.objects.filter(user=self.request.user).order_by('-purchased_at')