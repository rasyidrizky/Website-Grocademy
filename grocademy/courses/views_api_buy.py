from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Course, UserCourse

class BuyCourseAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            course = Course.objects.get(pk=pk)
        except Course.DoesNotExist:
            return Response({'error': 'Course not found'}, status=status.HTTP_404_NOT_FOUND)

        user = request.user

        if UserCourse.objects.filter(user=user, course=course).exists():
            return Response({'error': 'You have already purchased this course'}, status=status.HTTP_400_BAD_REQUEST)
        
        if user.balance < course.price:
            return Response({'error': 'Insufficient balance'}, status=status.HTTP_400_BAD_REQUEST)

        user.balance -= course.price
        user.save()

        UserCourse.objects.create(user=user, course=course)

        return Response({
            'message': 'Course purchased successfully!',
            'user_balance': user.balance
        }, status=status.HTTP_200_OK)