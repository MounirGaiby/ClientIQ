from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.db import models


class TenantUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user
    
    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_admin', True)
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=150, blank=True)
    last_name = models.CharField(max_length=150, blank=True)
    is_admin = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(blank=True, null=True)
    phone_number = models.CharField(max_length=20, blank=True)
    job_title = models.CharField(max_length=100, blank=True)
    department = models.CharField(max_length=100, blank=True)
    preferences = models.JSONField(default=dict, blank=True)
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    objects = TenantUserManager()
    
    @property
    def is_staff(self):
        return False
    
    @property 
    def is_superuser(self):
        return False
    
    class Meta:
        verbose_name = "Tenant User"
        verbose_name_plural = "Tenant Users"
        ordering = ['email']
    
    def __str__(self):
        admin_status = " (Admin)" if self.is_admin else ""
        return f"{self.email}{admin_status}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def save(self, *args, **kwargs):
        self.email = self.email.lower()
        super().save(*args, **kwargs)
    
    def has_perm(self, perm, obj=None):
        if not self.is_active:
            return False
        if self.is_admin:
            return True
        return super().has_perm(perm, obj)
    
    def has_perms(self, perm_list, obj=None):
        if not self.is_active:
            return False
        if self.is_admin:
            return True
        return super().has_perms(perm_list, obj)
    
    def has_module_perms(self, app_label):
        if not self.is_active:
            return False
        if self.is_admin:
            tenant_apps = ['users', 'contacts', 'leads']
            return app_label in tenant_apps
        return False
