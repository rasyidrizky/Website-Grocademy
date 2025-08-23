from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
from .models import Course
import json

# Create your tests here.
class CourseModelTest(TestCase):

    def setUp(self):
        Course.objects.create(
            title="Test Course for Model",
            description="A description.",
            instructor="Test Instructor",
            topics=json.dumps(["Testing", "Django"]),
            price=99.99
        )

    def test_course_creation(self):
        course = Course.objects.get(title="Test Course for Model")
        self.assertEqual(course.instructor, "Test Instructor")
        self.assertEqual(float(course.price), 99.99)

class CourseAPITest(TestCase):

    def setUp(self):
        self.user = CustomUser.objects.create_user(
            username='testuser', 
            email='test@example.com', 
            password='password123'
        )
        Course.objects.create(
            title="API Test Course",
            description="Desc 1",
            instructor="Instructor 1",
            topics=json.dumps(["API"]),
            price=25.00
        )
        self.list_url = reverse('course-list')

    def test_list_courses_unauthenticated(self):
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_courses_authenticated(self):
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        response = self.client.get(
            self.list_url, 
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)