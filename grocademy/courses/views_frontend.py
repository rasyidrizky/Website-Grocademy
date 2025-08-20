from django.shortcuts import render, redirect
from django.views import View
from django.core.paginator import Paginator
from .models import Course, UserCourse, Module, UserModuleProgress
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.http import HttpResponse
from django.template.loader import render_to_string
from weasyprint import HTML
import json

class HomePageView(View):
    def get(self, request):
        # Ambil query pencarian dari URL
        query = request.GET.get('q', '') 
        
        # Filter course berdasarkan query
        course_list = Course.objects.filter(title__icontains=query).order_by('title')

        # Setup paginator
        paginator = Paginator(course_list, 6) # Tampilkan 6 course per halaman
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'query': query, # Kirim query kembali ke template
        }
        return render(request, 'index.html', context)
    
@method_decorator(never_cache, name='dispatch')
class CourseDetailPageView(View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)

        # --- [LOGIKA BARU] Logika cerdas untuk menangani 'topics' ---
        topics_data = course.topics
        topics_list = []
        if isinstance(topics_data, list):
            # Jika sudah berupa list, langsung gunakan
            topics_list = topics_data
        elif isinstance(topics_data, str):
            # Jika berupa string, coba parsing sebagai JSON
            try:
                topics_list = json.loads(topics_data)
                # Pastikan hasilnya adalah list
                if not isinstance(topics_list, list):
                    topics_list = [topics_list]
            except json.JSONDecodeError:
                # Jika gagal parsing, anggap sebagai satu topik utuh
                topics_list = [topics_data]
        # ----------------------------------------------------

        is_purchased = False
        is_completed = False
        if request.user.is_authenticated:
            try:
                user_course = UserCourse.objects.get(user=request.user, course=course)
                is_purchased = True
                if user_course.completion_date:
                    is_completed = True
            except UserCourse.DoesNotExist:
                is_purchased = False

        context = {
            'course': course,
            'is_purchased': is_purchased,
            'is_completed': is_completed,
            'topics_list': topics_list  # Gunakan hasil dari logika cerdas
        }
        return render(request, 'course_detail.html', context)
    
@method_decorator(never_cache, name='dispatch')
class MyCoursesPageView(LoginRequiredMixin, View):
    login_url = '/login/' # URL tujuan jika user belum login

    def get(self, request):
        # Ambil semua course yang dimiliki user
        user_courses = UserCourse.objects.filter(user=request.user).select_related('course')
        courses = [uc.course for uc in user_courses]
        
        context = {
            'courses': courses
        }
        return render(request, 'my_courses.html', context)
    
@method_decorator(never_cache, name='dispatch')
class CourseModulePageView(LoginRequiredMixin, View):
    """
    View ini sekarang DILINDUNGI.
    LoginRequiredMixin adalah lapis keamanan pertama.
    """
    login_url = '/login/'  # Jika tidak login, alihkan ke sini.

    def get(self, request, pk):
        try:
            # Lapis Keamanan Kedua: Cek apakah user telah membeli kursus ini.
            # Jika baris ini gagal (user belum membeli), akan loncat ke blok 'except'.
            user_course = UserCourse.objects.get(user=request.user, course_id=pk)
        except UserCourse.DoesNotExist:
            # Jika user sudah login tapi belum membeli, alihkan ke halaman utama.
            return redirect('home')

        # --- Kode di bawah ini hanya akan berjalan jika user sudah login DAN sudah membeli ---
        
        course = user_course.course
        modules = course.modules.all().order_by('order')
        
        completed_modules = UserModuleProgress.objects.filter(user_course=user_course, is_completed=True)
        completed_modules_ids = completed_modules.values_list('module_id', flat=True)

        total_modules = modules.count()
        completed_count = completed_modules.count()
        progress_percentage = (completed_count / total_modules) * 100 if total_modules > 0 else 0
        
        # --- [LOGIKA BARU] Salin logika cerdas yang sama ke sini ---
        topics_data = course.topics
        topics_list = []
        if isinstance(topics_data, list):
            topics_list = topics_data
        elif isinstance(topics_data, str):
            try:
                topics_list = json.loads(topics_data)
                if not isinstance(topics_list, list):
                    topics_list = [topics_list]
            except json.JSONDecodeError:
                topics_list = [topics_data]
        # ----------------------------------------------------

        context = {
            'course': course,
            'modules': modules,
            'completed_modules_ids': list(completed_modules_ids),
            'progress_percentage': round(progress_percentage),
            'topics_list': json.loads(course.topics) # <-- TAMBAHKAN BARIS INI
        }
        return render(request, 'course_module.html', context)
    
@method_decorator(never_cache, name='dispatch')
class CertificateView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, pk):
        try:
            user_course = UserCourse.objects.get(user=request.user, course_id=pk)
        except UserCourse.DoesNotExist:
            return redirect('home')

        if not user_course.completion_date:
            return redirect('course_modules', pk=pk)

        context = {
            'user': request.user,
            'course': user_course.course,
            'completion_date': user_course.completion_date
        }

        # 1. Render template HTML menjadi sebuah string
        html_string = render_to_string('certificate.html', context)

        # 2. Buat objek HTML dari string tersebut
        html = HTML(string=html_string, base_url=request.build_absolute_uri())

        # 3. Buat file PDF di dalam memori
        pdf = html.write_pdf()

        # 4. Buat response HTTP dengan konten PDF
        response = HttpResponse(pdf, content_type='application/pdf')

        # 5. Tambahkan header agar file di-download dengan nama yang bagus
        filename = f"Sertifikat-{user_course.course.title.replace(' ', '-')}.pdf"
        response['Content-Disposition'] = f'attachment; filename="{filename}"'

        return response
    
class CartPageView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        return render(request, 'cart.html')
    
class HistoryPageView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        return render(request, 'history.html')