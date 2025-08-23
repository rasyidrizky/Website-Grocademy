from django.shortcuts import render
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin

class RegisterPageView(View):
    def get(self, request):
        return render(request, 'register.html')

class LoginPageView(View):
    def get(self, request):
        return render(request, 'login.html')
    
class ProfilePageView(LoginRequiredMixin, View):
    login_url = '/login/'
    def get(self, request):
        return render(request, 'profile.html')