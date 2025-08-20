from django.shortcuts import render
from django.views import View

class RegisterPageView(View):
    def get(self, request):
        return render(request, 'register.html')

class LoginPageView(View):
    def get(self, request):
        return render(request, 'login.html')