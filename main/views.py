from django.shortcuts import render, get_object_or_404
from django.views.generic import TemplateView, DetailView
from django.http import HttpResponse
from django.template.response import TemplateResponse
from django.db.models import Q

from .models import ProductModel

def product_detail(request, product_id):
    # Получаем товар или 404
    product = get_object_or_404(ProductModel, id=product_id)
    
    return render(request, 'main/product_detail.html', {
        'product': product
    })

def product_by_slug(request, slug):
    # По slug
    product = get_object_or_404(ProductModel, slug=slug, available=True)
    
    return render(request, 'main/product_detail.html', {
        'product': product
    })
from .models import CategoryModel, ProductModel, SizeModel



class IndexView(TemplateView):
    template_name = 'main/base.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = CategoryModel.objects.all()
        context['current_category'] = None
        return context
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        if request.headers.get('HX-Request'):
            return TemplateResponse(request, 'main/home_context.html', context)    
        return TemplateResponse(request, self.template_name, context)
    
    
class CatalogView(TemplateView):
    template = 'main/base.html'
    template_name = 'main/base.html'
    FILTER_MAPPING = {
        'color': lambda queryset, value: queryset.filter(color__iexact=value),
        'min_price': lambda queryset, value: queryset.filter(price__gte=value),
        'max_price': lambda queryset, value: queryset.filter(price__lte=value),
        'size': lambda queryset, value: queryset.filter(product_sizes__size__name=value),
    }
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        category_slug = kwargs.get('category_slug')
        categories = CategoryModel.objects.all()
        products = ProductModel.objects.all().order_by('-created_at')
        current_category = None
        
        if category_slug:
            current_category = get_object_or_404(CategoryModel, slug=category_slug)
            products = products.filter(category=current_category)
        query = self.request.GET.get('q')
        if query:
            products = products.filter(Q(name__icontains=query)|Q(description__icontains=query))
        filter_params ={}
        for param, filter_func in self.FILTER_MAPPING.items():
            value = self.request.GET.get(param)
            if value:
                products = filter_func(products, value)
                filter_params[param] = value
            else:
                filter_params[param] = ''
        
        filter_params['q'] = query or ''
        
        context.update({
            'categories': categories,
            'products': products,
            'current_category': current_category, #category_slug
            'filter_params': filter_params,
            'sizes': SizeModel.objects.all(),
            'search_query': query or ''
            })
        
        if self.request.GET.get('show_search') == 'true':
            context['show_search'] = True
        elif self.request.GET.get('reset_search') == 'true':
            context['reset_search'] = True
            
        return context
    
    
    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs) 
        is_htmx = request.headers.get('HX-Request')
        if is_htmx:
            if context.get('show_search'):
                return TemplateResponse(request, 'main/search_input.html', context)
            
            elif context.get('reset_search'):
                return TemplateResponse(request, 'main/search_button.html', context)  # {} -> context   
            
            template = 'main/filter_modal.html' if request.GET.get('show_filters') == 'true' else 'main/catalog.html' 
            return TemplateResponse(request, template, context)
            
            
        if hasattr(self, 'template_name') and self.template_name:
            return TemplateResponse(request, self.template_name, context)
        else:
            # ⚠️ Запасной вариант на случай проблем
            from django.http import HttpResponse
            return HttpResponse("Error: template_name not set", status=500)    
        
    
    
    
class ProductDetailView(DetailView):
        model = ProductModel
        template_name = 'main/product_detail.html'
        slug_field = 'slug'
        slug_url_kwarg = 'slug'
        context_object_name = 'product'
        
        def get_context_data(self, **kwargs):
            context = super().get_context_data(**kwargs)
            product = self.get_object()
            context['categories'] = CategoryModel.objects.all()
            context['related_products'] = ProductModel.objects.filter(
                category = product.category
            ).exclude(id=product.id)[:4]
            context['current_category'] = product.category.slug
            return context
        
        def get(self, request, *args, **kwargs):
            self.object = self.get_object()
            context = self.get_context_data(**kwargs)
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'main/product_detail.html', context)
            
            return TemplateResponse(request, self.template_name, context)
    

        