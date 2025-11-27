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
]

# Чтобы работали картинки в режиме разработки:
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)