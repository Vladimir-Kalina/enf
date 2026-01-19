from django.contrib import admin
from .models import CategoryModel, SizeModel, ProductModel, \
    ProductImageModel, ProductSizeModel
    

class ProductImageInline(admin.TabularInline):
    model = ProductImageModel
    extra = 1
    
class ProductSizeInline(admin.TabularInline):
    model = ProductSizeModel
    extra = 1
    
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'color', 'price']
    list_filter = ['category', 'color']
    search_fields = ['name', 'color', 'description']
    prepopulated_fields = {'slug': ('name',)}
    inlines = [ProductImageInline, ProductSizeInline]
    
    
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}
    
class SizeAdmin(admin.ModelAdmin):
    list_display = ['name']
    

admin.site.register(CategoryModel ,CategoryAdmin)
admin.site.register(SizeModel ,SizeAdmin)
admin.site.register(ProductModel ,ProductAdmin)