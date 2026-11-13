from django.contrib.gis.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin

class UserManager(BaseUserManager):
    def create_user(self, email, full_name, password=None, **extra_fields):
        if not email:
            raise ValueError('El correo electrónico es obligatorio')
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, full_name, password=None, **extra_fields):
        extra_fields.setdefault('role', User.Role.ADMINISTRATOR)
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, full_name, password, **extra_fields)

class User(AbstractBaseUser, PermissionsMixin):
    class Role(models.TextChoices):
        CYCLIST = 'cyclist', 'Cyclist'
        ADMINISTRATOR = 'administrator', 'Administrator'

    class Status(models.TextChoices):
        ACTIVE = 'active', 'Active'
        SUSPENDED = 'suspended', 'Suspended'
        TERMINATED = 'terminated', 'Terminated'
        
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    full_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=254, unique=True)
    role = models.CharField(max_length=15, choices=Role.choices, default=Role.CYCLIST)
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.ACTIVE)
    
    privacy_consent_at = models.DateTimeField(default=timezone.now)
    failed_login_attempts = models.SmallIntegerField(default=0)
    locked_until = models.DateTimeField(null=True, blank=True)
    
    last_login_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    def __str__(self):
        return f"{self.full_name} ({self.role})"


class IncidentReport(models.Model):
    class Type(models.TextChoices):
        THEFT = 'theft', 'Theft'
        POTHOLE = 'pothole', 'Pothole'
        FLOODING = 'flooding', 'Flooding'
        ROADWORK = 'roadwork', 'Roadwork'
        HARASSMENT = 'harassment', 'Harassment'
        ACCIDENT = 'accident', 'Accident'
        OBSTRUCTION = 'obstruction', 'Obstruction'
        OTHER = 'other', 'Other'

    class Severity(models.TextChoices):
        LOW = 'low', 'Low'
        MEDIUM = 'medium', 'Medium'
        HIGH = 'high', 'High'

    class State(models.TextChoices):
        ACTIVE = 'active', 'Active'
        RESOLVED = 'resolved', 'Resolved'
        EXPIRED = 'expired', 'Expired'
        MODERATED = 'moderated', 'Moderated'

    author = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reports')
    type = models.CharField(max_length=15, choices=Type.choices)
    severity = models.CharField(max_length=6, choices=Severity.choices)
    description = models.TextField()
    
    # Campo espacial para coordenadas GPS
    location = models.PointField(srid=4326)
    address = models.CharField(max_length=255, null=True, blank=True)
    
    state = models.CharField(max_length=10, choices=State.choices, default=State.ACTIVE)
    
    confirmation_count = models.IntegerField(default=0)
    solved_count = models.IntegerField(default=0)
    current_weight = models.DecimalField(max_digits=6, decimal_places=4, default=1.0000)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.get_type_display()} - {self.state}"