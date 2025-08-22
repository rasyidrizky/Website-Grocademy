from django.utils import timezone
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Module, UserCourse, UserModuleProgress
from .serializers import ModuleSerializer

class ModuleListAPIView(generics.ListAPIView):
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        course_id = self.kwargs['pk']
        user = self.request.user
        
        if not UserCourse.objects.filter(user=user, course_id=course_id).exists():
            return Module.objects.none()
        
        return Module.objects.filter(course_id=course_id).order_by('order')

class CompleteModuleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            module = Module.objects.get(pk=pk)
            user_course = UserCourse.objects.get(user=request.user, course=module.course)
        except (Module.DoesNotExist, UserCourse.DoesNotExist):
            return Response({'error': 'Module or course purchase not found'}, status=status.HTTP_404_NOT_FOUND)

        progress, created = UserModuleProgress.objects.get_or_create(
            user_course=user_course,
            module=module,
            defaults={'is_completed': True}
        )

        if not created and not progress.is_completed:
            progress.is_completed = True
            progress.save()

        total_modules = module.course.modules.count()
        completed_modules = UserModuleProgress.objects.filter(user_course=user_course, is_completed=True).count()
        percentage = (completed_modules / total_modules) * 100 if total_modules > 0 else 0
        
        if percentage == 100 and user_course.completion_date is None:
            user_course.completion_date = timezone.now()
            user_course.save()
        
        return Response({
            'message': 'Module marked as complete!',
            'completed_modules': completed_modules,
            'total_modules': total_modules,
            'percentage': round(percentage, 2),
            'course_id': module.course.id
        }, status=status.HTTP_200_OK)