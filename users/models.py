from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.html import strip_tags
from django.utils.translation import gettext_lazy as _


class CustomUserManager(BaseUserManager):
    
    def create_user(self, email, first_name, last_name, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set.')
        email = self.normalize_email(email=email)
        
        # Автоматически генерируем username
        if 'username' not in extra_fields or not extra_fields.get('username'):
            username_base = email.split('@')[0]
            username = username_base
            counter = 1
            
            while self.model.objects.filter(username=username).exists():
                username = f"{username_base}_{counter}"
                counter += 1
            
            extra_fields['username'] = username
        
        user = self.model(
            email=email, 
            first_name=first_name, 
            last_name=last_name, 
            **extra_fields
        )
        
        user.set_password(password)
        user.save(using=self._db)
        return user
        
    def create_superuser(self, email, first_name, last_name, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(email, first_name, last_name, password, **extra_fields)


class CustomUser(AbstractUser):
    # ЯВНО переопределяем поле username с null=True
    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        blank=True,
        null=True,  # ← ЭТО КРИТИЧЕСКИ ВАЖНО!
        help_text=_('Required. 150 characters or fewer.'),
    )
    
    email = models.EmailField(unique=True, max_length=254)
    first_name = models.CharField(max_length=50)
    last_name = models.CharField(max_length=50)
    company = models.CharField(max_length=100, blank=True, null=True)
    address1 = models.CharField(max_length=254, blank=True, null=True)
    address2 = models.CharField(max_length=254, blank=True, null=True)
    city = models.CharField(max_length=100, blank=True, null=True)
    country = models.CharField(max_length=100, blank=True, null=True)
    province = models.CharField(max_length=100, blank=True, null=True)
    postal_code = models.CharField(max_length=100, blank=True, null=True)
    phone = models.CharField(max_length=150, unique=True, blank=True, null=True)
    
    objects = CustomUserManager()
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    def __str__(self):
        return self.email
    
    def clean(self):
        for field in ['company', 'address1', 'address2', 'city', 
                      'country', 'province', 'postal_code', 'phone']:
            value = getattr(self, field)
            if value:
                setattr(self, field, strip_tags(value))
    
    def save(self, *args, **kwargs):
        # Автоматически генерируем username перед сохранением
        if not self.username and self.email:
            username_base = self.email.split('@')[0]
            username = username_base
            counter = 1
            
            while CustomUser.objects.filter(username=username).exclude(id=self.id).exists():
                username = f"{username_base}_{counter}"
                counter += 1
            
            self.username = username
        
        self.clean()
        super().save(*args, **kwargs)