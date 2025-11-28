from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm
from django.contrib.auth.decorators import login_required
from .models import Car, Cart, CartItem

def home(request):
    # Получаем 3 последних добавленных авто для "Слайдера/Героя"
    featured_cars = Car.objects.filter(is_available=True).order_by('-created_at')[:3]
    return render(request, 'store/index.html', {'featured_cars': featured_cars})

def catalog(request):
    # Получаем все машины для каталога [cite: 10]
    cars = Car.objects.filter(is_available=True)
    return render(request, 'store/catalog.html', {'cars': cars})

def car_detail(request, slug):
    car = get_object_or_404(Car, slug=slug, is_available=True)
    
    # Ищем авто той же категории, исключая текущую машину, берем 3 штуки
    related_cars = Car.objects.filter(category=car.category, is_available=True).exclude(id=car.id)[:3]
    
    return render(request, 'store/car_detail.html', {
        'car': car,
        'related_cars': related_cars
    })

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

@login_required(login_url='login') # Только для авторизованных
def add_to_cart(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    # Получаем или создаем корзину для пользователя
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Проверяем, есть ли уже этот авто в корзине
    cart_item, item_created = CartItem.objects.get_or_create(cart=cart, car=car)
    
    if not item_created:
        cart_item.quantity += 1
        cart_item.save()
    
    return redirect('cart_detail')

@login_required(login_url='login')
def cart_detail(request):
    # Получаем корзину, если нет - создаем пустую (на всякий случай)
    cart, created = Cart.objects.get_or_create(user=request.user)
    return render(request, 'store/cart.html', {'cart': cart})

@login_required(login_url='login')
def remove_from_cart(request, item_id):
    item = get_object_or_404(CartItem, id=item_id, cart__user=request.user)
    item.delete()
    return redirect('cart_detail')