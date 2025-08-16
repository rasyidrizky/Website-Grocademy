from django.db import transaction
from django.db.models import Q
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated

from .models import Purchase, ModuleProgress
from utils import APIUtils
from courses.models import Course

from django.http import FileResponse
from .certificates import CertificateGenerator
from datetime import datetime

# Create your views here.
class BuyCourseView(APIView):
    permission_classes = [IsAuthenticated]

    @transaction.atomic
    def post(self, request, course_id):
        try:
            course = Course.objects.get(pk=course_id)
        except Course.DoesNotExist:
            return APIUtils.api_response("error", "Course tidak ditemukan", None, http_status=404)

        user = request.user
        profile = user.profile

        if Purchase.objects.filter(user=user, course=course).exists():
            return APIUtils.api_response("error", "Course sudah dibeli", None, http_status=400)

        if profile.balance < course.price:
            return APIUtils.api_response("error", "Saldo tidak cukup", None, http_status=400)

        profile.balance -= course.price
        profile.save()

        purchase = Purchase.objects.create(user=user, course=course)
        ModuleProgress.objects.bulk_create([
            ModuleProgress(purchase=purchase, module=m) for m in course.modules.all()
        ])

        return APIUtils.api_response("success", "Pembelian berhasil", {
            "course_id": str(course.id),
            "user_balance": profile.balance,
            "transaction_id": str(purchase.transaction_id),
        }, http_status=201)

class MyCoursesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        from courses.serializers import MyCourseItemSerializer

        q = request.query_params.get("q", "").strip()
        qs = Purchase.objects.filter(user=request.user).select_related("course").order_by("-purchased_at")
        if q:
            qs = qs.filter(
                Q(course__title__icontains=q) |
                Q(course__instructor__icontains=q) |
                Q(course__topics__icontains=q)
            )

        data, pagination = APIUtils.paginate_queryset(
            qs,
            request,
            MyCourseItemSerializer,
            context={"request": request}
        )

        normalized = []
        for item in data:
            purchase = Purchase.objects.get(user=request.user, course__id=item["course"]["id"])
            total_modules = purchase.course.modules.count()
            completed_modules = purchase.progress.filter(is_completed=True).count()

            normalized.append({
                "id": str(item["course"]["id"]),
                "title": item["course"]["title"],
                "instructor": item["course"]["instructor"],
                "topics": item["course"]["topics"],
                "thumbnail_image": item["course"]["thumbnail_image"],
                "progress_percentage": item["progress_percentage"],
                "purchased_at": item["purchased_at"],
                "certificate_available": (
                    total_modules > 0 and completed_modules == total_modules
                ),
            })

        return APIUtils.api_response("success", "OK", normalized, pagination)
    
class CertificateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, course_id):
        try:
            purchase = Purchase.objects.select_related("course", "user").get(
                user=request.user,
                course__id=course_id
            )
        except Purchase.DoesNotExist:
            return APIUtils.api_response("error", "Course tidak ditemukan / belum dibeli", None, http_status=404)

        # Pastikan course sudah selesai
        total_modules = purchase.course.modules.count()
        completed_modules = purchase.progress.filter(is_completed=True).count()

        if total_modules == 0 or completed_modules < total_modules:
            return APIUtils.api_response("error", "Course belum diselesaikan", None, http_status=400)

        # Generate certificate
        certificate_file = CertificateGenerator.generate(
            username=request.user.username,
            course_title=purchase.course.title,
            instructor=purchase.course.instructor,
            completed_date=datetime.now()
        )

        # Return sebagai file download
        return FileResponse(certificate_file, as_attachment=True, filename=certificate_file.name)