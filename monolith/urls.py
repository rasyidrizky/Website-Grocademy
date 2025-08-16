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
from courses.views import (
    BrowseCoursesView, CourseDetailView, MyCoursesViewFE, BuyCourseViewFE, CourseModulesView
)
from courses.views import BuyCourseView, MyCoursesView  # API versi DRF
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework.routers import DefaultRouter
from courses.api import CourseViewSet, ModuleViewSet, UserViewSet

router = DefaultRouter()
router.register("courses", CourseViewSet)
router.register("modules", ModuleViewSet)
router.register("users", UserViewSet)

urlpatterns = [
    path("admin/", admin.site.urls),

    # -------- Frontend (HTML, pakai class-based view) --------
    path("", BrowseCoursesView.as_view(), name="home"),
    path("courses/", BrowseCoursesView.as_view(), name="browse_courses"),
    path("courses/<int:course_id>/", CourseDetailView.as_view(), name="course_detail"),
    path("courses/<int:course_id>/modules/", CourseModulesView.as_view(), name="course_modules"),
    path("my/", MyCoursesViewFE.as_view(), name="my_courses"),
    path("buy/<int:course_id>/", BuyCourseViewFE.as_view(), name="buy_course"),

    # -------- Auth --------
    path("register/", register_view, name="register"),
    path("login/", login_view, name="login"),
    path("logout/", logout_view, name="logout"),

    # -------- API (DRF) --------
    path("api/schema/", SpectacularAPIView.as_view(), name="schema"),
    path("api/docs/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path("api/", include(router.urls)),

    # Custom API
    path("api/purchases/buy/<int:course_id>/", BuyCourseView.as_view(), name="api_buy_course"),
    path("api/my-courses/", MyCoursesView.as_view(), name="api_my_courses"),
]