from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from .forms import UserRegistrationForm, CarFilterForm
from django.contrib.auth.decorators import login_required
from .models import Car, Cart, CartItem, Order, OrderItem


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

@login_required(login_url='login')
def add_to_cart(request, car_id):
    car = get_object_or_404(Car, id=car_id)
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Получаем тип тюнинга из формы (если метода POST нет, то 'base')
    tuning_choice = request.POST.get('tuning_type', 'base')
    
    # Ищем, есть ли уже такая машина С ТАКИМ ЖЕ тюнингом в корзине
    cart_item, item_created = CartItem.objects.get_or_create(
        cart=cart, 
        car=car,
        tuning_type=tuning_choice # Важно! Разные тюнинги - разные позиции
    )
    
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

def catalog(request):
    # Начинаем с полного списка доступных машин
    cars = Car.objects.filter(is_available=True)
    
    # Инициализируем форму, передавая GET-параметры (если они есть)
    form = CarFilterForm(request.GET)
    
    # Создаем контейнер для фильтрации
    filter_params = {}
    
    if form.is_valid():
        # 1. Фильтр по Категории
        category = form.cleaned_data.get('category')
        if category:
            filter_params['category'] = category
            
        # 2. Фильтр по Марке
        brand = form.cleaned_data.get('brand')
        if brand:
            filter_params['brand__iexact'] = brand # __iexact для нечувствительности к регистру
            
        # 3. Фильтр по Стране
        country = form.cleaned_data.get('country')
        if country:
            filter_params['country__iexact'] = country
            
        # 4. Фильтр по Цене (от)
        price_min = form.cleaned_data.get('price_min')
        if price_min is not None:
            filter_params['price__gte'] = price_min # greater than or equal
            
        # 5. Фильтр по Цене (до)
        price_max = form.cleaned_data.get('price_max')
        if price_max is not None:
            filter_params['price__lte'] = price_max # less than or equal
            
        # Применяем все собранные фильтры к QuerySet
        cars = cars.filter(**filter_params)
        
    return render(request, 'store/catalog.html', {
        'cars': cars,
        'form': form, # Передаем форму в шаблон для отображения
    })

@login_required(login_url='login')
def checkout(request):
    # 1. Получаем корзину
    cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Если корзина пуста, редиректим обратно
    if not cart.items.exists():
        return redirect('cart_detail')

    # 2. Создаем Заказ
    order = Order.objects.create(
        user=request.user,
        total_price=cart.get_total_price(),
        status='new'
    )

    # 3. Переносим товары из Корзины в OrderItem
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            car=item.car,
            price=item.get_cost(), # Берем пересчитанную цену
            tuning_type=item.tuning_type # Переносим тип тюнинга
        )
    
    # 4. Очищаем корзину
    cart.items.all().delete()

    # 5. Редирект в личный кабинет (или на страницу успеха)
    return redirect('profile')

@login_required(login_url='login')
def profile_view(request):
    # Получаем все заказы пользователя, от новых к старым
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    
    # Разделяем на Действующие и Завершенные
    active_orders = orders.filter(status__in=['new', 'processing'])
    history_orders = orders.filter(status__in=['shipped', 'cancelled'])

    return render(request, 'store/profile.html', {
        'active_orders': active_orders,
        'history_orders': history_orders
    })