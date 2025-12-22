from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from decimal import Decimal

TUNING_CHOICES = [
    ('base', 'Базовая комплектация'),
    ('standard', 'Standard Tuning (+15%)'),
    ('premium', 'Premium Tuning (+30%)'),
]

# 1. Категории (Марки или классы авто) [cite: 105]
class Category(models.Model):
    name = models.CharField("Название", max_length=100)
    slug = models.SlugField(unique=True, verbose_name="URL-метка")
    image = models.ImageField("Изображение категории", upload_to='categories/', blank=True)

    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

    def __str__(self):
        return self.name

# 2. Товар (Автомобиль) [cite: 103]
class Car(models.Model):
    # Основные поля
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='cars', verbose_name="Категория")
    brand = models.CharField("Марка", max_length=50) # Audi, BMW
    model = models.CharField("Модель", max_length=50) # RS6, M5
    country = models.CharField("Страна производителя", max_length=50, default="Неуказанно")
    slug = models.SlugField(unique=True, verbose_name="URL-метка")
    
    # Спецификации [cite: 15]
    year = models.PositiveIntegerField("Год выпуска")
    color = models.CharField("Цвет", max_length=50)
    body_type = models.CharField("Тип кузова", max_length=50) # Купе, Седан
    mileage = models.PositiveIntegerField("Пробег (км)", default=0)
    engine_power = models.PositiveIntegerField("Мощность (л.с.)") # [cite: 11]
    tuning_details = models.TextField("Описание тюнинга") # [cite: 16]
    
    # Торговые данные
    price = models.DecimalField("Цена", max_digits=12, decimal_places=0)
    description = models.TextField("Общее описание")
    main_image = models.ImageField("Главное фото", upload_to='cars/') # [cite: 54]
    is_available = models.BooleanField("В наличии", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Автомобиль"
        verbose_name_plural = "Автомобили"

    def __str__(self):
        return f"{self.brand} {self.model} ({self.tuning_details[:20]}...)"

# 3. Профиль пользователя (Бонусная система) [cite: 23, 102]
# Мы расширяем стандартного пользователя Django
class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone = models.CharField("Телефон", max_length=20, blank=True)

    def __str__(self):
        return f"Профиль {self.user.username}"

# Автоматическое создание профиля при регистрации
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance) # Приветственные бонусы можно начислить здесь [cite: 25]

# 4. Заказ [cite: 104]
class Order(models.Model):
    STATUS_CHOICES = [
        ('new', 'Новый'),
        ('processing', 'В обработке'),
        ('shipped', 'Доставлен'),
        ('cancelled', 'Отменен'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Покупатель")
    created_at = models.DateTimeField("Дата создания", auto_now_add=True)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='new') # [cite: 30]
    total_price = models.DecimalField("Сумма заказа", max_digits=12, decimal_places=2)
    
    class Meta:
        verbose_name = "Заказ"
        verbose_name_plural = "Заказы"

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    # Новое поле
    tuning_type = models.CharField(max_length=10, choices=TUNING_CHOICES, default='base')

    def __str__(self):
        return f"{self.car.brand} ({self.tuning_type})"

# 5. Корзина
class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)

    def get_total_price(self):
        return sum(item.get_total_item_price() for item in self.items.all())
    
    def get_total_items(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f"Корзина {self.user.username}"

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE)
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    # Новое поле
    tuning_type = models.CharField(max_length=10, choices=TUNING_CHOICES, default='base')

    def get_cost(self):
        base_price = self.car.price
        # Превращаем множители в Decimal (строки '1.15' обязательны для точности)
        if self.tuning_type == 'standard':
            price = base_price * Decimal('1.15')
        elif self.tuning_type == 'premium':
            price = base_price * Decimal('1.30')
        else:
            price = base_price
        return int(price) # Возвращаем цену за 1 шт.
    
    def get_total_item_price(self):
        """Возвращает общую стоимость позиции (цена с тюнингом * количество) [cite: 17, 115]"""
        return self.get_cost() * self.quantity