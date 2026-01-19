from django.db import models
from django.utils.text import slugify



class CategoryModel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True)
    
    
    def save(self, *args, **kvargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kvargs)
    
    def __str__(self):
        return self.name
    

class ProductModel(models.Model):
    name = models.CharField(max_length=100)
    slug = models.CharField(max_length=100, unique=True, )
    category = models.ForeignKey(CategoryModel, on_delete=models.CASCADE, related_name='products')

    color = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField(blank=True)
    nmain_imadge = models.ImageField(upload_to='products/main/')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kvargs):
        if not self.slug:
            self.slug = slugify(self.name)
        return super().save(*args, **kvargs)
    
    def __str__(self):
        return self.name


class SizeModel(models.Model):
    name = models.CharField(max_length=20)
    
    def __str__(self):
        return self.name
    

class ProductSizeModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='product_size')
    size = models.ForeignKey(SizeModel, on_delete=models.CASCADE)
    stock = models.PositiveBigIntegerField(default=0)
    
    def __str__(self):
        return f'{self.size.name} ({self.stock} in stock) for {self.product.name}'
    
    
class ProductImageModel(models.Model):
    product = models.ForeignKey(ProductModel, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='products/extra/')
    
