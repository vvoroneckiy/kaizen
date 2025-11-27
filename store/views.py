from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .models import Car
from .forms import UserRegistrationForm

def home(request):
    # Получаем 3 последних добавленных авто для "Слайдера/Героя"
    featured_cars = Car.objects.filter(is_available=True).order_by('-created_at')[:3]
    return render(request, 'store/index.html', {'featured_cars': featured_cars})

def catalog(request):
    # Получаем все машины для каталога [cite: 10]
    cars = Car.objects.filter(is_available=True)
    return render(request, 'store/catalog.html', {'cars': cars})

def car_detail(request, slug):
    # Ищем машину по slug, если нет — 404 ошибка
    car = get_object_or_404(Car, slug=slug, is_available=True)
    return render(request, 'store/car_detail.html', {'car': car})

def register_view(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Сразу логиним после регистрации
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'store/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('home')
    else:
        form = AuthenticationForm()
        # Тоже добавим стили для стандартной формы входа
        for field in form.fields:
            form.fields[field].widget.attrs.update({'class': 'form-input'})
            
    return render(request, 'store/login.html', {'form': form})

def logout_view(request):
    logout(request)
    return redirect('home')