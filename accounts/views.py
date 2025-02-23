from django.contrib.auth import authenticate, login, logout
from django.shortcuts import render, redirect
from django.contrib import messages

from accounts.forms import SignUpForm, LoginForm


from django.contrib.auth.models import User
from schoolmock_app.models import *
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)  # Создаем объект пользователя, но пока не сохраняем его
            role = form.cleaned_data.get('role')

            # Устанавливаем статус is_staff, если роль TEACHER
            if role == Profile.TEACHER:
                user.is_staff = True

            user.save()  # Сохраняем пользователя

            # Создаем запись в модели Student
            Profile.objects.create(
                user=user,
                name=user.first_name,  # Или другое поле формы
                surname=user.last_name,  # Или другое поле формы
                role=role,
                school="",  # Предусмотрите возможность ввода школы
                classroom=""  # Или задайте значение по умолчанию
            )

            # Аутентификация пользователя
            login(request, user)
            return redirect('test-view')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})

from django.views.decorators.csrf import csrf_exempt
@csrf_exempt
def login_view(request):
    if request.method == 'POST':
        form = LoginForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, "Siz hozir login qildingiz!",)
            return redirect('test-view')
    else:
        form = LoginForm()
    return render(request, 'accounts/login.html', {'form': form})


def logout_view(request):
    logout(request)
    messages.success(request, "Siz hozir logout qildingiz!")
    return redirect('login')