from django.contrib import admin
from .models import Category, Size, Product, \
    ProductImage, ProductSize


# Register your models here.

# Встроенный администратор для изображений товара
class ProductImageInline(admin.TabularInline):
    model = ProductImage  # Связанная модель
    extra = 1  # Количество пустых форм для добавления новых записей

# Встроенный администратор для размеров товара
class ProductSizeInline(admin.TabularInline):
    model = ProductSize  # Связанная модель
    extra = 1  # Количество пустых форм для добавления новых записей

# Настройка отображения модели Product в административной панели
class ProductAdmin(admin.ModelAdmin):
    # Поля, отображаемые в списке товаров
    list_display = ['name', 'category', 'color', 'price']
    
    # Фильтры в правой части админки
    list_filter = ['category', 'color']
    
    # Поля, по которым можно выполнять поиск
    search_fields = ['name', 'color', 'description']
    
    # Поля, которые автоматически заполняются на основе других полей
    prepopulated_fields = {'slug': ('name',)}  # slug создается из name
    
    # Встроенные формы для связанных моделей
    inlines = [ProductImageInline, ProductSizeInline]

# Настройка отображения модели Category в административной панели
class CategoryAdmin(admin.ModelAdmin):
    # Поля, отображаемые в списке категорий
    list_display = ['name', 'slug']
    
    # Автоматическое заполнение slug на основе имени категории
    prepopulated_fields = {'slug': ('name',)}

# Настройка отображения модели Size в административной панели
class SizeAdmin(admin.ModelAdmin):
    # Поля, отображаемые в списке размеров
    list_display = ['name']


# Регистрация модели Category с кастомизацией CategoryAdmin
admin.site.register(Category, CategoryAdmin)
# Регистрация модели Size с кастомизацией SizeAdmin
admin.site.register(Size, SizeAdmin)
# Регистрация модели Product с кастомизацией ProductAdmin
admin.site.register(Product, ProductAdmin)