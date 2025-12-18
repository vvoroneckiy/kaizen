from django.contrib import admin
from django.utils.html import format_html
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
    list_display = ('id', 'user', 'status_colored', 'total_price', 'created_at', 'action_buttons')
    list_filter = ('status', 'created_at')
    inlines = [OrderItemInline]
    
    # Добавляем действие "Действия" (Actions)
    actions = ['make_completed', 'make_processing']

    # 1. Функция-действие: "Отметить как Выполнен"
    @admin.action(description='Пометить выбранные заказы как "Выполнен"')
    def make_completed(self, request, queryset):
        # Обновляем статус у всех выбранных заказов
        updated = queryset.update(status='shipped')
        self.message_user(request, f'Обновлено заказов: {updated}. Статус: Выполнен.')

    # 2. Функция-действие: "В обработке" (для удобства)
    @admin.action(description='Пометить как "В обработке"')
    def make_processing(self, request, queryset):
        queryset.update(status='processing')
        self.message_user(request, f'Заказы переведены в статус "В обработке".')

    # 3. Красивое отображение статуса цветом
    def status_colored(self, obj):
        colors = {
            'new': 'blue',
            'processing': 'orange',
            'shipped': 'green',
            'cancelled': 'red',
        }
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            colors.get(obj.status, 'black'),
            obj.get_status_display()
        )
    status_colored.short_description = 'Статус'

    # (Опционально) Кнопка прямо в строке, если не хотите через галочки
    def action_buttons(self, obj):
        return format_html(
            '<a class="button" href="/admin/store/order/{}/change/">Редактировать</a>',
            obj.id
        )
    action_buttons.short_description = 'Действие'

admin.site.register(Profile) # Управление бонусами юзеров [cite: 31]