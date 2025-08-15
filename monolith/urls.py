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
from users.views import register_view, login_view, logout_view
from courses.views import browse_courses, course_detail, buy_course, my_courses, course_modules
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from courses.api import CourseViewSet, ModuleViewSet, UserViewSet

router = DefaultRouter()
router.register("courses", CourseViewSet)
router.register("modules", ModuleViewSet)
router.register("users", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),

    # F01 (FE)
    path("", browse_courses),
    path("courses/", browse_courses, name="browse_courses"),
    path("courses/<int:course_id>/", course_detail, name="course_detail"),
    path("courses/<int:course_id>/modules/", course_modules, name="course_modules"),
    path("my/", my_courses, name="my_courses"),
    path("buy/", buy_course, name="buy_course"),

    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # Kontrak API (OpenAPI/Swagger)
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),

    # API routes
    path("api/", include(router.urls)),
]