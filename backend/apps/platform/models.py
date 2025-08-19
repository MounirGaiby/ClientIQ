from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models


class SuperUserManager(BaseUserManager):
    """Manager for platform super users"""
    
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_readonly', False)  # Full admin by default
        extra_fields.setdefault('is_active', True)
        
        return self.create_user(email, password, **extra_fields)


class SuperUser(AbstractBaseUser):
    """
    Platform super users who can access Django admin.
    These users exist only in the public schema and manage the platform.
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_active = models.BooleanField(default=True)
    is_readonly = models.BooleanField(
        default=False,
        help_text="If True, can only view Django admin (no edit/delete permissions)"
    )
    date_joined = models.DateTimeField(auto_now_add=True)
    last_login = models.DateTimeField(null=True, blank=True)
    
    objects = SuperUserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = 'Platform Super User'
        verbose_name_plural = 'Platform Super Users'
    
    def __str__(self):
        return f"{self.email} (Platform Admin)"
    
    def get_full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        return self.first_name
    
    def has_perm(self, perm, obj=None):
        """
        Platform super users have all permissions unless readonly
        """
        if self.is_readonly:
            # Readonly users can only view, not add/change/delete
            return perm.endswith('_view') or 'view' in perm
        return True
    
    def has_perms(self, perm_list, obj=None):
        """
        Platform super users have all permissions unless readonly
        """
        if self.is_readonly:
            return all(self.has_perm(perm, obj) for perm in perm_list)
        return True
    
    def has_module_perms(self, app_label):
        """
        Platform super users have access to all modules
        """
        return True
    
    @property
    def is_staff(self):
        """All platform users can access Django admin"""
        return True
    
    @property
    def is_superuser(self):
        """All platform users are superusers unless readonly"""
        return not self.is_readonly
