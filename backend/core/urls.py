from django.urls import path, include
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import (
    RegisterUserView, MeView, IncidentReportViewSet, TripViewSet,
    RouteSearchView, RouteDetailView, UnsafeZonesView, BikewayListView,
)

router = DefaultRouter()
# Esto crea automáticamente las rutas de /reports/ (incluye nearby, confirm y solve) y /trips/
router.register(r'reports', IncidentReportViewSet, basename='report')
router.register(r'trips', TripViewSet, basename='trip')

urlpatterns = [
    # Rutas de autenticación (JWT)
    path('auth/register/', RegisterUserView.as_view(), name='register'),
    path('auth/login/', TokenObtainPairView.as_view(), name='login'),
    path('auth/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('auth/me/', MeView.as_view(), name='me'),

    # Rutas, zonas y ciclorrutas
    path('routes/search/', RouteSearchView.as_view(), name='route_search'),
    path('routes/<int:pk>/', RouteDetailView.as_view(), name='route_detail'),
    path('zones/unsafe/', UnsafeZonesView.as_view(), name='unsafe_zones'),
    path('bikeways/', BikewayListView.as_view(), name='bikeways'),

    # Reportes y recorridos (router)
    path('', include(router.urls)),
]
