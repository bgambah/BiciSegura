from datetime import timedelta

from django.contrib.gis.db.models.functions import Distance
from django.contrib.gis.geos import LineString, Point, Polygon
from django.contrib.gis.measure import D
from django.db.models import F
from django.utils import timezone
from rest_framework import viewsets, generics, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import User, IncidentReport, ReportVote, Route, Trip, Bikeway
from .serializers import (
    UserRegistrationSerializer, UserSerializer, IncidentReportSerializer,
    RouteSerializer, TripSerializer, BikewaySerializer,
)
from .services import plan_routes, unsafe_zones

SOLVE_THRESHOLD = 3  # con 3 usuarios que marquen "ya se solucionó", el reporte se resuelve


class RegisterUserView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]


class MeView(generics.RetrieveAPIView):
    """GET /api/auth/me/"""
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        return self.request.user


class IncidentReportViewSet(viewsets.ModelViewSet):
    # Solo mostramos los reportes activos por defecto
    queryset = IncidentReport.objects.filter(state=IncidentReport.State.ACTIVE).order_by('-created_at')
    serializer_class = IncidentReportSerializer

    # Por ahora permitimos que cualquiera los vea y los cree para facilitar las pruebas
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            p = self.request.query_params  # ?type=theft,pothole&severity=high&days=7
            if p.get('type'):
                qs = qs.filter(type__in=p['type'].split(','))
            if p.get('severity'):
                qs = qs.filter(severity__in=p['severity'].split(','))
            if p.get('days', '').isdigit():
                qs = qs.filter(created_at__gte=timezone.now() - timedelta(days=int(p['days'])))
        return qs

    def perform_create(self, serializer):
        # Si el usuario inició sesión, lo asociamos como autor del reporte
        author = self.request.user if self.request.user.is_authenticated else None
        serializer.save(author=author)

    @action(detail=False, methods=['get'])
    def nearby(self, request):
        """GET /api/reports/nearby/?lat=&lng=&radius=  (radio en metros, por defecto 300, máx. 5000)"""
        try:
            lat = float(request.query_params['lat'])
            lng = float(request.query_params['lng'])
            radius = min(float(request.query_params.get('radius', 300)), 5000)
        except (KeyError, ValueError):
            return Response({'detail': 'Se requieren lat y lng numéricos.'}, status=400)
        pt = Point(lng, lat, srid=4326)
        qs = (self.get_queryset().filter(location__distance_lte=(pt, D(m=radius)))
              .annotate(distance=Distance('location', pt)).order_by('distance'))
        return Response(self.get_serializer(qs, many=True).data)

    def _vote(self, request, kind):
        report = self.get_object()
        _, created = ReportVote.objects.get_or_create(report=report, user=request.user, kind=kind)
        if not created:
            return Response({'detail': 'Ya registraste esta acción en este reporte.'}, status=409)
        field = 'confirmation_count' if kind == ReportVote.Kind.CONFIRM else 'solved_count'
        IncidentReport.objects.filter(pk=report.pk).update(**{field: F(field) + 1})
        report.refresh_from_db()
        if report.solved_count >= SOLVE_THRESHOLD and report.state == IncidentReport.State.ACTIVE:
            report.state = IncidentReport.State.RESOLVED
            report.save(update_fields=['state'])
        return Response(self.get_serializer(report).data)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def confirm(self, request, pk=None):
        """POST /api/reports/<id>/confirm/  ("Sigue ocurriendo")"""
        return self._vote(request, ReportVote.Kind.CONFIRM)

    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def solve(self, request, pk=None):
        """POST /api/reports/<id>/solve/  ("Ya se solucionó")"""
        return self._vote(request, ReportVote.Kind.SOLVE)


def _point(data):
    lat, lng = float(data['lat']), float(data['lng'])
    if not (-90 <= lat <= 90 and -180 <= lng <= 180):
        raise ValueError('coordenadas fuera de rango')
    return (lng, lat)


class RouteSearchView(APIView):
    """POST /api/routes/search/  {origin:{lat,lng}, destination:{lat,lng}, preference?: safest|fastest|bikeways}"""
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        try:
            origin, dest = _point(request.data['origin']), _point(request.data['destination'])
        except (KeyError, TypeError, ValueError):
            return Response({'detail': 'Se requieren origin y destination con lat y lng válidos.'}, status=400)
        user = request.user if request.user.is_authenticated else None
        routes = [
            Route.objects.create(
                kind=kind, origin=Point(*origin, srid=4326), destination=Point(*dest, srid=4326),
                path=LineString(c['coords'], srid=4326), distance_m=c['distance_m'], duration_s=c['duration_s'],
                safety_index=c['safety_index'], bikeway_pct=c['bikeway_pct'], created_by=user)
            for kind, c in plan_routes(origin, dest).items()
        ]
        preferred = request.data.get('preference', 'safest')
        routes.sort(key=lambda r: r.kind != preferred)  # la preferida va primero
        return Response(RouteSerializer(routes, many=True).data)


class RouteDetailView(generics.RetrieveAPIView):
    """GET /api/routes/<id>/"""
    queryset = Route.objects.all()
    serializer_class = RouteSerializer
    permission_classes = [permissions.AllowAny]


class TripViewSet(viewsets.ModelViewSet):
    """POST /api/trips/ inicia; PATCH /api/trips/<id>/ {status} pausa, reanuda o finaliza; GET lista el historial propio."""
    queryset = Trip.objects.all().order_by('-started_at')
    serializer_class = TripSerializer
    permission_classes = [permissions.AllowAny]  # para pruebas, igual que los reportes
    http_method_names = ['get', 'post', 'patch', 'head', 'options']

    def get_queryset(self):
        qs = super().get_queryset()
        if self.action == 'list':
            user = self.request.user
            return qs.filter(user=user) if user.is_authenticated else qs.none()
        return qs

    def perform_create(self, serializer):
        user = self.request.user if self.request.user.is_authenticated else None
        serializer.save(user=user)

    def perform_update(self, serializer):
        done = serializer.validated_data.get('status') == Trip.Status.FINISHED
        serializer.save(finished_at=timezone.now() if done else None)


class UnsafeZonesView(APIView):
    """GET /api/zones/unsafe/?threshold=60"""
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        t = request.query_params.get('threshold', '60')
        return Response(unsafe_zones(int(t) if t.isdigit() else 60))


class BikewayListView(generics.ListAPIView):
    """GET /api/bikeways/?bbox=minLng,minLat,maxLng,maxLat"""
    queryset = Bikeway.objects.all()
    serializer_class = BikewaySerializer
    permission_classes = [permissions.AllowAny]
    pagination_class = None

    def get_queryset(self):
        qs = super().get_queryset()
        bbox = self.request.query_params.get('bbox')
        if bbox:
            try:
                qs = qs.filter(path__intersects=Polygon.from_bbox([float(v) for v in bbox.split(',')]))
            except (ValueError, TypeError):
                pass
        return qs
