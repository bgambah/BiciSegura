from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RegisterUserView, IncidentReportViewSet

router = DefaultRouter()
# Esto crea automáticamente las rutas para /reports/
router.register(r'reports', IncidentReportViewSet, basename='report')

urlpatterns = [
    # Rutas de autenticación (JWT)
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # Rutas de la API
    path('', include(router.urls)),
]