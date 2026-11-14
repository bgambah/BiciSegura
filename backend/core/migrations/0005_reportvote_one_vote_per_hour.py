from django.db import migrations, models
from django.db.models import F


def keep_latest_vote(apps, schema_editor):
    """
    Antes un usuario podía tener "sigue ocurriendo" y "ya se solucionó" en el mismo reporte.
    Ahora solo hay un voto por usuario y reporte: se conserva el más reciente, se marca como
    votado cuando se creó (para que nadie quede bloqueado por la migración) y se recalculan
    los contadores de los reportes con votos.
    """
    ReportVote = apps.get_model('core', 'ReportVote')
    IncidentReport = apps.get_model('core', 'IncidentReport')

    latest = {}
    for vote in ReportVote.objects.order_by('created_at', 'id'):
        latest[(vote.report_id, vote.user_id)] = vote.id
    ReportVote.objects.exclude(id__in=list(latest.values())).delete()
    ReportVote.objects.update(updated_at=F('created_at'))

    for report_id in {report_id for report_id, _ in latest}:
        votes = ReportVote.objects.filter(report_id=report_id)
        IncidentReport.objects.filter(pk=report_id).update(
            confirmation_count=votes.filter(kind='confirm').count(),
            solved_count=votes.filter(kind='solve').count(),
        )


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_trip_accumulated_s_trip_name_trip_resumed_at'),
    ]

    operations = [
        migrations.AddField(
            model_name='reportvote',
            name='updated_at',
            field=models.DateTimeField(null=True),
        ),
        migrations.RunPython(keep_latest_vote, migrations.RunPython.noop),
        migrations.AlterField(
            model_name='reportvote',
            name='updated_at',
            field=models.DateTimeField(auto_now=True),
        ),
        migrations.AlterUniqueTogether(
            name='reportvote',
            unique_together=set(),
        ),
        migrations.AddConstraint(
            model_name='reportvote',
            constraint=models.UniqueConstraint(fields=('report', 'user'), name='one_vote_per_user_per_report'),
        ),
    ]
