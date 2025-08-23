# courses/tests.py

from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from users.models import CustomUser
from .models import Course
import json

# --- KELAS TES UNTUK MODEL ---
class CourseModelTest(TestCase):

    def setUp(self):
        """Metode ini berjalan sebelum setiap tes untuk menyiapkan data."""
        Course.objects.create(
            title="Test Course for Model",
            description="A description.",
            instructor="Test Instructor",
            topics=json.dumps(["Testing", "Django"]),
            price=99.99
        )

    def test_course_creation(self):
        """MENGUJI: Apakah objek Course berhasil dibuat dengan data yang benar."""
        course = Course.objects.get(title="Test Course for Model")
        self.assertEqual(course.instructor, "Test Instructor")
        self.assertEqual(float(course.price), 99.99)


# --- KELAS TES UNTUK API ---
class CourseAPITest(TestCase):

    def setUp(self):
        """Siapkan data user dan course untuk tes API."""
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
        """MENGUJI: Apakah pengguna yang BELUM LOGIN DITOLAK saat mengakses API."""
        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_list_courses_authenticated(self):
        """MENGUJI: Apakah pengguna yang SUDAH LOGIN BISA melihat daftar kursus."""
        # [DIPERBARUI] Buat token JWT untuk user
        refresh = RefreshToken.for_user(self.user)
        access_token = str(refresh.access_token)
        
        # Kirim request dengan header Authorization
        response = self.client.get(
            self.list_url, 
            HTTP_AUTHORIZATION=f'Bearer {access_token}'
        )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)