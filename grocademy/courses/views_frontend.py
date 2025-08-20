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
        query = request.GET.get('q', '') 
        
        course_list = Course.objects.filter(title__icontains=query).order_by('title')

        paginator = Paginator(course_list, 6)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)
        
        context = {
            'page_obj': page_obj,
            'query': query,
        }
        return render(request, 'index.html', context)
    
@method_decorator(never_cache, name='dispatch')
class CourseDetailPageView(View):
    def get(self, request, pk):
        course = Course.objects.get(pk=pk)

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
            'topics_list': topics_list
        }
        return render(request, 'course_detail.html', context)
    
@method_decorator(never_cache, name='dispatch')
class MyCoursesPageView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request):
        user_courses = UserCourse.objects.filter(user=request.user).select_related('course')
        courses = [uc.course for uc in user_courses]
        
        context = {
            'courses': courses
        }
        return render(request, 'my_courses.html', context)
    
@method_decorator(never_cache, name='dispatch')
class CourseModulePageView(LoginRequiredMixin, View):
    login_url = '/login/'

    def get(self, request, pk):
        try:
            user_course = UserCourse.objects.get(user=request.user, course_id=pk)
        except UserCourse.DoesNotExist:
            return redirect('home')
        
        course = user_course.course
        modules = course.modules.all().order_by('order')
        
        completed_modules = UserModuleProgress.objects.filter(user_course=user_course, is_completed=True)
        completed_modules_ids = completed_modules.values_list('module_id', flat=True)

        total_modules = modules.count()
        completed_count = completed_modules.count()
        progress_percentage = (completed_count / total_modules) * 100 if total_modules > 0 else 0
        
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

        context = {
            'course': course,
            'modules': modules,
            'completed_modules_ids': list(completed_modules_ids),
            'progress_percentage': round(progress_percentage),
            'topics_list': json.loads(course.topics)
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

        html_string = render_to_string('certificate.html', context)
        html = HTML(string=html_string, base_url=request.build_absolute_uri())
        pdf = html.write_pdf()
        response = HttpResponse(pdf, content_type='application/pdf')

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