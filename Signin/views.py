# Create your views here.
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages

def signup_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(f"{username} {password}")
        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already taken')
            return redirect('signup')
        user = User.objects.create_user(username=username, password=password)
        login(request, user)
        return redirect('login')
    return render(request, 'login.html')

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        print(f"{username}...... {password}")

        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return render(request, 'accounts/dashboard.html', {'user': user})
        else:
            messages.error(request, 'Invalid credentials')
            return redirect('login')
    return render(request, 'sign_up.html')

def logout_view(request):
    logout(request)
    return redirect('login')
