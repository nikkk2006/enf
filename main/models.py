from django.db import models
from django.utils.text import slugify # Импортируем функцию slugify для создания slug из строки


# Create your models here.
class Category(models.Model):  

    # Название категории
    name = models.CharField(max_length=100)
    
    # URL-адреса категории (уникальное для избежания дублирования)
    slug = models.CharField(max_length=100, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:                   # Если slug не указан
            self.slug = slugify(self.name)  # Создаем slug из названия
        super().save(*args, **kwargs)       # Вызываем родительский метод save

    def __str__(self):
        return self.name
    
class Size(models.Model):
    # Поле для названия размера (например: "S", "M", "L", "XL" или "42", "44", "46")
    name = models.CharField(max_length=20)

    def __str__(self):
        # Возвращаем название размера при преобразовании объекта в строку
        return self.name

class Product(models.Model):
    # Название товара
    name = models.CharField(max_length=100)
    
    # Уникальный идентификатор для URL (например: "iphone-15-pro-max")
    slug = models.CharField(max_length=100, unique=True)
    
    # Связь с моделью Category, CASCADE - удаление товаров при удалении категории
    # related_name позволяет обращаться к товарам категории через category.products.all()
    category = models.ForeignKey(Category, on_delete=models.CASCADE,
                                 related_name='products')
    
    # Цвет товара
    color = models.CharField(max_length=100)
    
    # Цена товара (10 цифр всего, 2 после запятой)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Описание товара (может быть пустым)
    description = models.TextField(blank=True)
    
    # Основное изображение товара, загружается в папку 'products/main/'
    main_image = models.ImageField(upload_to='products/main/')
    
    # Дата создания (автоматически при создании)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Дата обновления (автоматически при каждом сохранении)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        # Если slug не указан, создаем его из названия товара
        if not self.slug:
            self.slug = slugify(self.name)
        # Вызываем оригинальный метод save
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class ProductSize(models.Model):
    # Связь с моделью Product, CASCADE - удаление размеров при удалении товара
    # related_name позволяет обращаться к размерам товара через product.product_size.all()
    product = models.ForeignKey('Product', on_delete=models.CASCADE,
                                related_name='product_sizes')
    
    # Связь с моделью Size (предположительно содержит названия размеров: S, M, L и т.д.)
    size = models.ForeignKey(Size, on_delete=models.CASCADE)
    
    # Количество товара данного размера на складе (не может быть отрицательным)
    stock = models.PositiveIntegerField(default=0)

    def __str__(self):
        # Строковое представление для удобного отображения в админке и дебаге
        return f"{self.size.name} ({self.stock} in stock) for {self.product.name}"
    
class ProductImage(models.Model):
    """
    Данный класс хранит детальные изображения для товара, т.е. когда я нажму
    на сам товар в каталоге, я перейду в детальный просмотр товара, где
    будет несколько фотографий по этому товару. 
    """
    # Связь с моделью Product, CASCADE - удаление изображений при удалении товара
    # related_name позволяет обращаться к изображениям товара через product.images.all()
    product = models.ForeignKey(Product, on_delete=models.CASCADE,
                                related_name='images')
    
    # Дополнительное изображение товара, загружается в папку 'products/extra/'
    image = models.ImageField(upload_to='products/extra/')