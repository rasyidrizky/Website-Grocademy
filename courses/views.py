from django.db.models import Q
from django.db import transaction
from django.utils import timezone

from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.parsers import MultiPartParser, FormParser, JSONParser
from rest_framework.decorators import action
from rest_framework.views import APIView

from .models import Course, Module
from .serializers import CourseSerializer, CourseListSerializer, ModuleSerializer, ModuleDetailSerializer
from purchase.models import Purchase, ModuleProgress, Certificate
from purchase.certificates import CertificateGenerator
from utils import APIUtils

from django.views import View
from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Course, Module
from purchase.models import Purchase

# Create your views here.
class CourseViewSet(viewsets.ModelViewSet):
    queryset = Course.objects.all().order_by("-created_at")
    serializer_class = CourseSerializer
    permission_classes = [IsAdminUser]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_serializer_class(self):
        if self.action == "list":
            return CourseListSerializer
        return CourseSerializer

    def list(self, request, *args, **kwargs):
        q = request.query_params.get("q", "").strip()
        qs = self.get_queryset()
        if q:
            qs = qs.filter(
                Q(title__icontains=q) |
                Q(instructor__icontains=q) |
                Q(topics__icontains=q)
            )
        data, pagination = APIUtils.paginate_queryset(
            qs, request, self.get_serializer_class(), context={"request": request}
        )
        return APIUtils.api_response("success", "OK", data, pagination)

    def retrieve(self, request, *args, **kwargs):
        obj = self.get_object()
        ser = CourseSerializer(obj, context={"request": request})
        return APIUtils.api_response("success", "OK", ser.data)


class ModuleViewSet(viewsets.ModelViewSet):
    queryset = Module.objects.all().select_related("course")
    serializer_class = ModuleSerializer
    permission_classes = [IsAuthenticated]
    parser_classes = [MultiPartParser, FormParser, JSONParser]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy", "reorder"]:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, course_pk=None):
        try:
            course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            return APIUtils.api_response("error", "Course tidak ditemukan", None, http_status=404)

        data = request.data.copy()
        if "order" not in data:
            last = course.modules.order_by("-order").first()
            data["order"] = (last.order + 1) if last else 1

        ser = ModuleSerializer(data=data)
        if not ser.is_valid():
            return APIUtils.api_response("error", "Validasi gagal", ser.errors, http_status=400)

        ser.save(course=course)
        return APIUtils.api_response("success", "Module dibuat", ser.data, http_status=201)

    def list(self, request, course_pk=None):
        if not course_pk:
            return APIUtils.api_response("error", "courseId wajib", None, http_status=400)

        try:
            course = Course.objects.get(pk=course_pk)
        except Course.DoesNotExist:
            return APIUtils.api_response("error", "Course tidak ditemukan", None, http_status=404)

        if not request.user.is_staff:
            if not Purchase.objects.filter(user=request.user, course=course).exists():
                return APIUtils.api_response("error", "Akses ditolak", None, http_status=403)

        qs = course.modules.all()
        data, pagination = APIUtils.paginate_queryset(
            qs, request, ModuleDetailSerializer, context={"request": request}
        )
        return APIUtils.api_response("success", "OK", data, pagination)

    def retrieve(self, request, pk=None):
        obj = Module.objects.get(pk=pk)
        ser = ModuleDetailSerializer(obj, context={"request": request})
        return APIUtils.api_response("success", "OK", ser.data)

    def update(self, request, pk=None):
        obj = Module.objects.get(pk=pk)
        ser = ModuleSerializer(obj, data=request.data, partial=True)
        if not ser.is_valid():
            return APIUtils.api_response("error", "Validasi gagal", ser.errors, http_status=400)
        ser.save()
        return APIUtils.api_response("success", "Module diupdate", ser.data)

    def destroy(self, request, pk=None):
        Module.objects.filter(pk=pk).delete()
        return APIUtils.api_response("success", "Module dihapus", None, http_status=204)

    @action(detail=False, methods=["patch"], url_path="reorder", permission_classes=[IsAdminUser])
    def reorder(self, request, course_pk=None):
        body = request.data
        if "module_order" not in body or not isinstance(body["module_order"], list):
            return APIUtils.api_response("error", "Format salah: butuh module_order[]", None, http_status=400)

        try:
            with transaction.atomic():
                for item in body["module_order"]:
                    Module.objects.filter(pk=item["id"], course_id=course_pk).update(order=item["order"])
        except Exception as e:
            return APIUtils.api_response("error", f"Gagal reorder: {e}", None, http_status=400)

        return APIUtils.api_response("success", "Reorder berhasil", {"module_order": body["module_order"]})


class CompleteModuleView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def patch(self, request, pk):
        try:
            module = Module.objects.select_related("course").get(pk=pk)
        except Module.DoesNotExist:
            return APIUtils.api_response("error", "Module tidak ditemukan", None, http_status=404)

        try:
            purchase = Purchase.objects.get(user=request.user, course=module.course)
        except Purchase.DoesNotExist:
            return APIUtils.api_response("error", "Kamu belum membeli course ini", None, http_status=403)

        prog, _ = ModuleProgress.objects.get_or_create(purchase=purchase, module=module)
        if not prog.is_completed:
            prog.is_completed = True
            prog.completed_at = timezone.now()
            prog.save()

        total = module.course.total_modules
        completed = ModuleProgress.objects.filter(purchase=purchase, is_completed=True).count()
        percentage = round(completed * 100 / total) if total else 0

        certificate_url = None
        if total and completed == total:
            if not hasattr(purchase, "certificate"):
                generator = CertificateGenerator()
                pdf_file = generator.generate(
                    username=request.user.username,
                    course_title=module.course.title,
                    instructor=module.course.instructor,
                    completed_date=timezone.now(),
                )
                cert = Certificate.objects.create(purchase=purchase)
                cert.file.save("certificate.pdf", pdf_file, save=True)
                certificate_url = cert.file.url
            else:
                certificate_url = purchase.certificate.file.url

        return APIUtils.api_response("success", "Module ditandai selesai", {
            "module_id": str(module.id),
            "is_completed": True,
            "course_progress": {
                "total_modules": total,
                "completed_modules": completed,
                "percentage": percentage
            },
            "certificate_url": certificate_url
        })
    
class BrowseCoursesView(View):
    def get(self, request):
        q = request.GET.get("q", "").strip()
        courses = Course.objects.all().order_by("-created_at")
        if q:
            courses = courses.filter(title__icontains=q)
        return render(request, "courses/browse.html", {"courses": courses})


class CourseDetailView(View):
    def get(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return render(request, "404.html", status=404)
        return render(request, "courses/detail.html", {"course": course})


class MyCoursesView(LoginRequiredMixin, View):
    def get(self, request):
        purchases = Purchase.objects.filter(user=request.user)
        return render(request, "courses/my.html", {"purchases": purchases})


class BuyCourseView(LoginRequiredMixin, View):
    def post(self, request):
        course_id = request.POST.get("course_id")
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return render(request, "404.html", status=404)

        Purchase.objects.get_or_create(user=request.user, course=course)
        return redirect("my_courses")