from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver

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
    bonus_points = models.DecimalField("Бонусный счет", max_digits=10, decimal_places=2, default=0) # [cite: 24]

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
    car = models.ForeignKey(Car, on_delete=models.CASCADE, verbose_name="Автомобиль")
    price = models.DecimalField("Цена на момент покупки", max_digits=12, decimal_places=2)

    def __str__(self):
        return f"{self.car.brand} {self.car.model}"