from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required
from django.urls import reverse
from django.http import HttpResponse
from django.template.response import TemplateResponse
from .forms import CustomUserCreationForm, CustomUserLoginForm, CustomUserUpdateForm
from .models import CustomUser
from django.contrib import messages
from main.models import ProductModel




# def register(request):
#     if request.method == 'POST':
#         form = CustomUserCreationForm(request.POST)
#         if form.is_valid():
#             user = form.save()
#             login(request=request, user=user, backend='django.contrib.auth.backends.ModelBackend')
            
#             return redirect('main:index')
#         else:
#             form = CustomUserCreationForm()
#         return render(request, 'users/register.html', {'form': form})

def register(request):
    # Для GET-запроса или если форма не валидна
    form = CustomUserCreationForm()
    
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(
                request=request, 
                user=user, 
                backend='django.contrib.auth.backends.ModelBackend'
            )
            return redirect('main:index')
        # Если форма не валидна, форма УЖЕ содержит данные и ошибки
    
    # Рендерим шаблон с формой (для GET или невалидного POST)
    return render(request, 'users/register.html', {'form': form})


# def login_view(request):
#     if request.method == 'POST':
#         form = CustomUserLoginForm(request=request, data=request.POST)
#         if form.is_valid():
#             user = form.get_user()
#             login(request=request, user=user, backend='django.contrib.auth.backends.ModelBackend')
#             return redirect('main:index')
        
#         else:
#             form = CustomUserLoginForm()
#     else:
#             form = CustomUserLoginForm()
      
#     return render(request, 'users/login.html', {'form': form})
# def login_view(request):
#     print("=== LOGIN VIEW ===")
#     print(f"Request method: {request.method}")
#     print(f"User before: {request.user}")
#     print(f"Authenticated before: {request.user.is_authenticated}")
    
#     if request.method != 'POST':
#         form = CustomUserLoginForm()
#         print("GET request - showing form")
#         return render(request, 'users/login.html', {'form': form})
    
#     form = CustomUserLoginForm(request=request, data=request.POST)
#     print(f"Form valid: {form.is_valid()}")
    
#     if form.is_valid():
#         user = form.get_user()
#         print(f"Got user: {user}, ID: {user.id}")
        
#         login(request=request, user=user)
#         print(f"After login - User: {request.user}")
#         print(f"After login - Authenticated: {request.user.is_authenticated}")
#         print(f"Session key: {request.session.session_key}")
        
#         if request.headers.get('HX-Request') == 'true':
#             response = HttpResponse()
#             response['HX-Redirect'] = '/'
#             return response
        
#         return redirect('main:index')
    
#     print(f"Form errors: {form.errors}")
#     return render(request, 'users/login.html', {'form': form})
def login_view(request):
    # GET запрос - пустая форма
    if request.method != 'POST':
        form = CustomUserLoginForm()
        return render(request, 'users/login.html', {'form': form})
    
    # POST запрос
    form = CustomUserLoginForm(request=request, data=request.POST)
    
    # Если форма валидна - логиним
    if form.is_valid():
        user = form.get_user()
        login(request=request, user=user, backend='django.contrib.auth.backends.ModelBackend')
        print(f'user {user} login()+')
        return redirect('main:index')
    
    # Если невалидна - показываем форму С ОШИБКАМИ
    return render(request, 'users/login.html', {'form': form})
        
@login_required(login_url='/users/login/')
def profile_view(request):
    if request.method == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            if request.headers.get('HX-Request') == 'true':
                response = HttpResponse()
                response['HX-Redirect'] = '/users/profile/'  # или reverse('users:profile')
                return response
    else:
        form = CustomUserUpdateForm(instance=request.user)
        
    recommented_products = ProductModel.objects.all().order_by('id')[:3]
    
    return TemplateResponse(request, 'users/profile.html', {
        'form': form,
        'user': request.user,
        'recommented_products': recommented_products
    })
        
@login_required(login_url='/users/login/')
def account_details(request):
    user = CustomUser.objects.get(id=request.user.id)
    return TemplateResponse(request, 'users/partials/account_details.html', {'user': user})

@login_required(login_url='/users/login/')
def edit_account_details(request):
    form = CustomUserUpdateForm(instance=request.user)
    return TemplateResponse(request, 'users/partials/edit_account_details.html', {
        'user':request.user,
        'form':form
    })
    

@login_required(login_url='/users/login')
def update_account_details(request):
    if request.method  == 'POST':
        form = CustomUserUpdateForm(request.POST, instance=request.user)
        if form.is_valid():
            user = form.save(commit=False)
            user.clean()
            user.save()
            updated_user = CustomUser.objects.get(id=user.id)
            request.user = updated_user
            if request.headers.get('HX-Request'):
                return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
            return TemplateResponse(request, 'users/partials/account_details.html', {'user': updated_user})
        else:
            return TemplateResponse(request, 'users/partials/edit_account_details.html', {'user': request.user, 'form':form})
        
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect': reverse('users:profile')})
    return redirect('users:profile')


def logout_view(request):
    logout(request)
    if request.headers.get('HX-Request'):
        return HttpResponse(headers={'HX-Redirect':reverse('main:index')})
    return redirect('main:index')
    
    
            
        
            

