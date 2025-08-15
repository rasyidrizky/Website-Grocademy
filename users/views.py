from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect

# Create your views here.
def register_view(request):
    if request.method == "POST":
        u = request.POST.get("username"); e = request.POST.get("email"); p = request.POST.get("password")
        if User.objects.filter(username=u).exists():
            return render(request, "auth/register.html", {"error": "Username already exists"})
        User.objects.create_user(username=u, email=e, password=p)
        return redirect("/login/")
    return render(request, "auth/register.html")

def login_view(request):
    if request.method == "POST":
        u = request.POST.get("username"); p = request.POST.get("password")
        user = authenticate(request, username=u, password=p)
        if not user:
            return render(request, "auth/login.html", {"error": "Invalid credentials"})
        login(request, user)
        return redirect("/courses/")
    return render(request, "auth/login.html")

def logout_view(request):
    logout(request)
    return redirect("/login/")