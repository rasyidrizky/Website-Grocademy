"""
URL configuration for monolith project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView

# Import API Views
from courses.views_api import CourseViewSet, ModuleViewSet 
from users.views_api import RegisterAPIView, UserDetailAPIView, UserAdminViewSet, CustomTokenObtainPairView 

# Import Frontend Views
from courses.views_frontend import HomePageView, CourseDetailPageView, MyCoursesPageView, CourseModulePageView, CertificateView 

# Import Frontend Views User
from users.views_frontend import RegisterPageView, LoginPageView
from courses.views_api_buy import BuyCourseAPIView
from courses.views_api_mycourses import MyCoursesAPIView
from courses.views_api_modules import ModuleListAPIView, CompleteModuleAPIView

# Router untuk API
router = DefaultRouter()
router.register(r'courses', CourseViewSet)
router.register(r'modules', ModuleViewSet)
router.register(r'users', UserAdminViewSet)

urlpatterns = [
    # 1. Admin Page
    path('admin/', admin.site.urls),

    # 2. REST API Endpoints (untuk FE Admin)
    path('api/', include(router.urls)),
    path('api/auth/register/', RegisterAPIView.as_view(), name='api_register'),
    path('api/auth/login/', CustomTokenObtainPairView.as_view(), name='api_login'),
    path('api/auth/refresh/', TokenRefreshView.as_view(), name='api_refresh'),
    path('api/auth/self/', UserDetailAPIView.as_view(), name='api_self'), # Sesuai kontrak [cite: 582]
    
    path('api/courses/<int:pk>/buy/', BuyCourseAPIView.as_view(), name='api_buy_course'),
    path('api/courses/my-courses/', MyCoursesAPIView.as_view(), name='api_my_courses'),
    path('api/courses/<int:pk>/modules/', ModuleListAPIView.as_view(), name='api_module_list'),
    path('api/modules/<int:pk>/complete/', CompleteModuleAPIView.as_view(), name='api_module_complete'),
    
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/schema/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('api/schema/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),

    # 3. Frontend Monolith Pages
    path('', HomePageView.as_view(), name='home'),
    # --- Tambahkan URL di bawah ini ---
    path('register/', RegisterPageView.as_view(), name='register_page'),
    path('login/', LoginPageView.as_view(), name='login_page'),
    path('course/<int:pk>/', CourseDetailPageView.as_view(), name='course_detail'),
    path('course/<int:pk>/modules/', CourseModulePageView.as_view(), name='course_modules'),
    path('course/<int:pk>/certificate/', CertificateView.as_view(), name='course_certificate'),
    path('my-courses/', MyCoursesPageView.as_view(), name='my_courses'),
]