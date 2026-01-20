# Функция для получения объекта из БД или возврата 404 ошибки
from django.shortcuts import get_object_or_404
# Классовые представления (Class-Based Views)
from django.views.generic import TemplateView, DetailView
# Класс для возврата HTTP-ответов
from django.http import HttpResponse
# Класс для возврата шаблонных ответов
from django.template.response import TemplateResponse
# Импорт моделей из текущего приложения
from .models import Category, Product, Size
# Импорт Q-объектов для сложных запросов к БД (OR, AND условия)
from django.db.models import Q


# Create your views here.

# Класс представления для главной страницы
class IndexView(TemplateView):
    # Имя шаблона для отображения
    template_name = 'main/base.html'

    # Метод для получения данных контекста
    def get_context_data(self, **kwargs):
        # Получаем контекст из родительского класса
        context = super().get_context_data(**kwargs)
        # Добавляем все категории в контекст
        context['categories'] = Category.objects.all()
        # Устанавливаем текущую категорию как None (главная страница)
        context['current_category'] = None
        return context

    # Метод обработки GET-запроса
    def get(self, request, *args, **kwargs):
        # Получаем контекст с данными
        context = self.get_context_data(**kwargs)
        # Проверяем, является ли запрос HTMX-запросом
        if request.headers.get('HX-Request'):
            # Возвращаем только содержимое (без базового шаблона) для HTMX
            return TemplateResponse(request, 'main/home_content.html', context)
        # Возвращаем полную страницу для обычного запроса
        return TemplateResponse(request, self.template_name, context)

class CatalogView(TemplateView):
    # Шаблон для отображения каталога
    template = 'main/base.html'

    # Сопоставление параметров фильтра с функциями фильтрации
    FILTER_MAPPING = {
        # Фильтр по цвету (без учета регистра)
        'color': lambda queryset, value: queryset.filter(color__iexact=value),
        # Фильтр по минимальной цене
        'min_price': lambda queryset, value: queryset.filter(price__gte=value),
        # Фильтр по максимальной цене
        'max_price': lambda queryset, value: queryset.filter(price__lte=value),
        # Фильтр по размеру
        'size': lambda queryset, value: queryset.filter(product_size__size__name=value)
    }

    def get_context_data(self, **kwargs):
        # Получаем контекст из родительского класса
        context = super().get_context_data(**kwargs)
        # Получаем slug категории из URL
        category_slug = kwargs.get('category_slug')
        # Получаем все категории
        categories = Category.objects.all()
        # Получаем все товары, отсортированные по дате создания (сначала новые)
        products = Product.objects.all().order_by('-created_at')
        
        current_category = None

        # Если указана категория, фильтруем товары по ней
        if category_slug:
            current_category = get_object_or_404(Category, slug=category_slug)
            products = products.filter(category=current_category)
        
        # Получаем поисковый запрос из GET-параметра 'q'
        query = self.request.GET.get('q', '')
        if query:
            # Фильтруем товары по названию или описанию (без учета регистра)
            products = products.filter(
                Q(name__icontains=query) | Q(description__icontains=query)
            )

        # Словарь для хранения параметров фильтра
        filter_params = {}

        # Применяем фильтры из FILTER_MAPPING
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                # Применяем функцию фильтрации к queryset
                products = filter_func(products, value)
                # Сохраняем значение параметра для отображения в форме
                filter_params[param] = value
            else:
                # Если параметр не указан, сохраняем пустую строку
                filter_params[param] = ''

        # Сохраняем поисковый запрос в параметрах фильтра
        filter_params['q'] = query or ''

        # Обновляем контекст с данными для шаблона
        context.update({
            # Все категории для навигации
            'categories': categories,
            # Отфильтрованный список товаров
            'products': products,
            # Текущая категория (если есть)
            'current_category': current_category,
            # Параметры фильтров для сохранения в форме
            'filter_params': filter_params,
            # Все размеры для фильтра по размеру
            'sizes': Size.objects.all(),
            # Поисковый запрос для отображения в поле поиска
            'search_query': query or ''
        })

        # Проверяем специальные флаги для управления UI
        if self.request.GET.get('show_search') == 'true':
            # Флаг для показа поисковой формы
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            # Флаг для сброса поиска
            context['reset_search'] = True

        # Возвращаем контекст с данными
        return context
    
    def get(self, request, *args, **kwargs):
        # Получаем контекст с данными
        context = self.get_context_data(**kwargs)
        
        # Проверяем, является ли запрос HTMX-запросом
        if request.headers.get('HX-Request'):
            # Если нужно показать поисковую форму
            if context.get('show_search'):
                return TemplateResponse(request, 'main/search_input.html', context)
            # Если нужно сбросить поиск и показать кнопку
            elif context.get('reset_search'):
                return TemplateResponse(request, 'main/search_button.html', {})
            
            # Определяем какой шаблон использовать для HTMX-ответа
            # Если запрошен показ фильтров, используем модальное окно
            # Иначе используем основной контент каталога (возможна опечатка в 'mailer')
            template = 'main/filter_modal.html' if request.GET.get('show_filters') == 'true' else 'main/catalog.html'
            return TemplateResponse(request, template, context)
        
        # Возвращаем полную страницу для обычного запроса
        return TemplateResponse(request, self.template_name, context)

class ProductDetailView(DetailView):
    # Модель для отображения детальной информации
    model = Product
    # Основной шаблон страницы
    template_name = 'main/base.html'
    # Поле модели для поиска по slug
    slug_field = 'slug'
    # Имя параметра URL для slug
    slug_url_kwarg = 'slug'

    def get_context_data(self, **kwargs):
        # Получаем базовый контекст
        context = super().get_context_data(**kwargs)
        # Получаем текущий товар
        product = self.get_object()
        # Добавляем все категории для навигации
        context['categories'] = Category.objects.all()
        # Получаем похожие товары (той же категории, исключая текущий)
        context['related_products'] = Product.objects.filter(
            category=product.category
        ).exclude(id=product.id)[:4]  # Ограничиваем 4 товарами
        # Добавляем slug текущей категории
        context['current_category'] = product.category.slug
        return context

    def get(self, request, *args, **kwargs):
        # Получаем объект товара
        self.object = self.get_object()
        # Получаем контекст
        context = self.get_context_data(**kwargs)
        # Проверяем HTMX-запрос
        if request.headers.get('HX-Request'):  # Исправлено: было header.get
            # Возвращаем только контент товара
            return TemplateResponse(request, 'main/product_detail.html', context)
        # Возвращаем полную страницу
        return TemplateResponse(request, self.template_name, context)  # Исправлено: было raise