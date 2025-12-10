from django.contrib import admin
from .models import Category, Car, Profile, Order, OrderItem

@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ('brand', 'model', 'year', 'price', 'is_available', 'country')
    list_filter = ('brand', 'year', 'body_type', 'country') # Фильтры в админке [cite: 11]
    search_fields = ('brand', 'model', 'tuning_details')
    prepopulated_fields = {'slug': ('brand', 'model', 'year')} # Авто-заполнение URL

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

class OrderItemInline(admin.TabularInline):
    model = OrderItem
    raw_id_fields = ['car']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'status', 'total_price', 'created_at')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline] # Позволяет видеть товары внутри заказа

admin.site.register(Profile) # Управление бонусами юзеров [cite: 31]