from django.contrib import admin
from django.contrib.gis import admin as gis_admin

from .models import User, IncidentReport, ReportVote, Bikeway, Route, Trip


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ('email', 'full_name', 'role', 'status', 'created_at')
    list_filter = ('role', 'status')
    search_fields = ('email', 'full_name')
    # La contraseña no se edita aquí (se guardaría sin cifrar); los usuarios se crean con
    # el registro de la app o con `python manage.py createsuperuser`.
    readonly_fields = ('password',)

    def has_add_permission(self, request):
        return False


@admin.register(IncidentReport)
class IncidentReportAdmin(gis_admin.GISModelAdmin):
    list_display = ('id', 'type', 'severity', 'state', 'confirmation_count', 'solved_count', 'author', 'created_at')
    list_filter = ('state', 'type', 'severity')
    search_fields = ('description', 'address')


@admin.register(Bikeway)
class BikewayAdmin(gis_admin.GISModelAdmin):
    list_display = ('id', 'name')
    search_fields = ('name',)


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ('id', 'kind', 'distance_m', 'duration_s', 'safety_index', 'bikeway_pct', 'created_at')
    list_filter = ('kind',)


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'user', 'route', 'status', 'started_at', 'finished_at')
    list_filter = ('status',)


@admin.register(ReportVote)
class ReportVoteAdmin(admin.ModelAdmin):
    list_display = ('id', 'report', 'user', 'kind', 'created_at', 'updated_at')
    list_filter = ('kind',)
