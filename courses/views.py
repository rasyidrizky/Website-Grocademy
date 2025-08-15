from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Course, Module, UserCourse

# Create your views here.
def browse_courses(request):
    courses = Course.objects.all()
    return render(request, "courses/browse.html", {"courses": courses})

def course_detail(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    return render(request, "courses/detail.html", {"course": course})

@login_required
def buy_course(request):
    if request.method == "POST":
        cid = request.POST.get("course_id")
        course = get_object_or_404(Course, id=cid)
        UserCourse.objects.get_or_create(user=request.user, course=course)
        return redirect("/my/")
    return redirect("/courses/")

@login_required
def my_courses(request):
    items = UserCourse.objects.filter(user=request.user).select_related("course")
    return render(request, "my/my_courses.html", {"items": items})

@login_required
def course_modules(request, course_id):
    course = get_object_or_404(Course, id=course_id)
    # optional: validasi kepemilikan
    modules = Module.objects.filter(course=course)
    return render(request, "courses/modules.html", {"course": course, "modules": modules})