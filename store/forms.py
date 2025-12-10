from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Car, Category

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, label="Email")

    class Meta:
        model = User
        fields = ['username', 'email'] # Пароли добавит UserCreationForm автоматически

    # Добавляем CSS классы для темной темы ко всем полям
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields:
            self.fields[field].widget.attrs.update({
                'class': 'form-input', 
                'placeholder': self.fields[field].label
            })

class CarFilterForm(forms.Form):
    # Получаем уникальные значения для марок и стран из БД
    brands = Car.objects.values_list('brand', 'brand').order_by('brand').distinct()
    countries = Car.objects.values_list('country', 'country').order_by('country').distinct()
    
    # 1. Фильтр по Категории (выпадающий список)
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        label="Категория",
        empty_label="Все категории",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )
    
    # 2. Фильтр по Марке (выпадающий список)
    brand = forms.ChoiceField(
        choices=[('', 'Все марки')] + list(brands),
        required=False,
        label="Марка",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )

    # 3. Фильтр по Стране производителя (выпадающий список)
    country = forms.ChoiceField(
        choices=[('', 'Все страны')] + list(countries),
        required=False,
        label="Страна",
        widget=forms.Select(attrs={'class': 'filter-select'})
    )

    # 4. Фильтр по Цене (диапазон)
    price_min = forms.IntegerField(
        required=False,
        label="Цена от",
        widget=forms.NumberInput(attrs={'placeholder': 'Мин. цена', 'class': 'form-input filter-input'})
    )
    price_max = forms.IntegerField(
        required=False,
        label="Цена до",
        widget=forms.NumberInput(attrs={'placeholder': 'Макс. цена', 'class': 'form-input filter-input'})
    )