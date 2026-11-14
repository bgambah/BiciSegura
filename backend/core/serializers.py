from django.utils import timezone
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import User, IncidentReport, Route, Trip, Bikeway, VOTE_COOLDOWN


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    """Datos del usuario con sesión iniciada (GET /auth/me/)."""
    reports_count = serializers.SerializerMethodField()
    trips_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'role', 'created_at', 'reports_count', 'trips_count']

    def get_reports_count(self, obj):
        return obj.reports.count()

    def get_trips_count(self, obj):
        return obj.trips.count()


class IncidentReportSerializer(GeoFeatureModelSerializer):
    # SerializerMethodField tolera reportes anónimos (author = None).
    author_name = serializers.SerializerMethodField()
    # Voto de quien consulta ('confirm', 'solve' o None) y segundos que faltan para que pueda votar otra vez
    my_vote = serializers.SerializerMethodField()
    vote_wait_s = serializers.SerializerMethodField()

    class Meta:
        model = IncidentReport
        geo_field = 'location'  # Campo espacial que se usa como geometría del mapa
        fields = [
            'id', 'author', 'author_name', 'type', 'severity',
            'description', 'address', 'state', 'confirmation_count',
            'solved_count', 'current_weight', 'created_at', 'my_vote', 'vote_wait_s'
        ]
        read_only_fields = [
            'id', 'author', 'state', 'confirmation_count',
            'solved_count', 'current_weight', 'created_at'
        ]

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else None

    def _my_vote(self, obj):
        return self.context.get('my_votes', {}).get(obj.pk)

    def get_my_vote(self, obj):
        v = self._my_vote(obj)
        return v.kind if v else None

    def get_vote_wait_s(self, obj):
        v = self._my_vote(obj)
        if not v:
            return 0
        return max(0, int((VOTE_COOLDOWN - (timezone.now() - v.updated_at)).total_seconds()))


class RouteSerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Route
        geo_field = 'path'
        fields = ['id', 'kind', 'distance_m', 'duration_s', 'safety_index', 'bikeway_pct', 'origin', 'destination']


class TripSerializer(serializers.ModelSerializer):
    # Segundos de recorrido hasta este momento, sin contar las pausas (el servidor es quien cuenta)
    elapsed_s = serializers.SerializerMethodField()

    class Meta:
        model = Trip
        fields = ['id', 'route', 'name', 'status', 'started_at', 'finished_at', 'elapsed_s']
        read_only_fields = ['id', 'started_at', 'finished_at', 'elapsed_s']

    def get_elapsed_s(self, obj):
        return obj.elapsed_s()


class BikewaySerializer(GeoFeatureModelSerializer):
    class Meta:
        model = Bikeway
        geo_field = 'path'
        fields = ['id', 'name']
