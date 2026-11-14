from datetime import timedelta

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


# ---------------------------------------------------------------------------
# Rutas, recorridos, ciclorrutas y votos sobre reportes
# ---------------------------------------------------------------------------
from django.conf import settings


VOTE_COOLDOWN = timedelta(hours=1)  # cada usuario puede votar una vez por hora en cada reporte


class ReportVote(models.Model):
    """
    Voto vigente de un usuario sobre un reporte: "sigue ocurriendo" o "ya se solucionó".
    Hay uno solo por usuario y reporte (no puede tener las dos opciones a la vez). Pasada
    una hora puede votar otra vez: el voto se actualiza, así que un usuario cuenta una sola vez.
    """
    class Kind(models.TextChoices):
        CONFIRM = 'confirm', 'Sigue ocurriendo'
        SOLVE = 'solve', 'Ya se solucionó'

    report = models.ForeignKey(IncidentReport, on_delete=models.CASCADE, related_name='votes')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='votes')
    kind = models.CharField(max_length=7, choices=Kind.choices)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # hora del último voto (para el límite de 1 hora)

    class Meta:
        constraints = [models.UniqueConstraint(fields=['report', 'user'], name='one_vote_per_user_per_report')]


class Bikeway(models.Model):
    """Tramo de ciclorruta (se carga con: python manage.py load_bikeways archivo.geojson)."""
    name = models.CharField(max_length=150, blank=True)
    path = models.LineStringField(srid=4326)

    def __str__(self):
        return self.name or f'Ciclorruta {self.pk}'


class Route(models.Model):
    class Kind(models.TextChoices):
        SAFEST = 'safest', 'Más segura'
        FASTEST = 'fastest', 'Más rápida'
        BIKEWAYS = 'bikeways', 'Más ciclorrutas'

    kind = models.CharField(max_length=8, choices=Kind.choices)
    origin = models.PointField(srid=4326)
    destination = models.PointField(srid=4326)
    path = models.LineStringField(srid=4326)
    distance_m = models.IntegerField()
    duration_s = models.IntegerField()
    safety_index = models.SmallIntegerField()   # 0 (peligrosa) a 100 (segura)
    bikeway_pct = models.SmallIntegerField(default=0)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='routes')
    created_at = models.DateTimeField(auto_now_add=True)


class Trip(models.Model):
    class Status(models.TextChoices):
        ACTIVE = 'active', 'En marcha'
        PAUSED = 'paused', 'En pausa'
        FINISHED = 'finished', 'Finalizado'

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='trips')
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='trips')
    name = models.CharField(max_length=100, blank=True)  # nombre que le pone la persona (vacío = "Recorrido N")
    status = models.CharField(max_length=8, choices=Status.choices, default=Status.ACTIVE)
    started_at = models.DateTimeField(auto_now_add=True)
    finished_at = models.DateTimeField(null=True, blank=True)
    # Cronómetro: segundos en marcha ya cerrados (sin pausas) y desde cuándo corre el tramo activo
    accumulated_s = models.PositiveIntegerField(default=0)
    resumed_at = models.DateTimeField(null=True, blank=True)

    def elapsed_s(self, now=None):
        """Segundos de recorrido sin contar las pausas."""
        total = self.accumulated_s
        if self.status == self.Status.ACTIVE:
            total += int(((now or timezone.now()) - (self.resumed_at or self.started_at)).total_seconds())
        return max(0, total)
