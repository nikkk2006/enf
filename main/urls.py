from django.urls import path
from . import views

# Пространство имен приложения
app_name = 'main'

# URL-шаблоны приложения
urlpatterns = [
    # Главная страница
    path('', views.IndexView.as_view(), name='index'),
    # Каталог всех товаров
    path('catalog/', views.CatalogView.as_view(), name='catalog_all'),
    # Каталог товаров конкретной категории
    path('catalog/<slug:category_slug>/', views.CatalogView.as_view(), name='catalog'),
    # Детальная страница товара
    path('product/<slug:slug>/', views.ProductDetailView.as_view(), name='product_detail')
]