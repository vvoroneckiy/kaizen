from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from store import views # Импортируем наши вьюхи

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),       # Главная страница
    path('catalog/', views.catalog, name='catalog'), # Каталог

    path('car/<slug:slug>/', views.car_detail, name='car_detail'), # Детальная страница
    path('register/', views.register_view, name='register'),       # Регистрация
    path('login/', views.login_view, name='login'),                # Вход
    path('logout/', views.logout_view, name='logout'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:car_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('profile/', views.profile_view, name='profile'),   # Личный кабинет
    path('checkout/', views.checkout, name='checkout'), 
]

# Чтобы работали картинки в режиме разработки:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)