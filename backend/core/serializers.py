from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from .models import User, IncidentReport


class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ['id', 'full_name', 'email', 'password', 'role', 'created_at']
        read_only_fields = ['id', 'role', 'created_at']

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)


class IncidentReportSerializer(GeoFeatureModelSerializer):
    # SerializerMethodField tolera reportes anónimos (author = None).
    # Con ReadOnlyField(source='author.full_name') DRF lanzaba SkipField
    # al intentar leer el nombre de un autor inexistente.
    author_name = serializers.SerializerMethodField()

    class Meta:
        model = IncidentReport
        geo_field = 'location'  # Campo espacial que se usa como geometría del mapa
        fields = [
            'id', 'author', 'author_name', 'type', 'severity',
            'description', 'address', 'state', 'confirmation_count',
            'solved_count', 'current_weight', 'created_at'
        ]
        read_only_fields = [
            'id', 'author', 'state', 'confirmation_count',
            'solved_count', 'current_weight', 'created_at'
        ]

    def get_author_name(self, obj):
        return obj.author.full_name if obj.author else None