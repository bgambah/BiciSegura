import json

from django.contrib.gis.geos import LineString
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from core.models import Bikeway

NAME_KEYS = ('name', 'nombre', 'NOMBRE', 'Name', 'NOM_CICLO', 'nom_via')


class Command(BaseCommand):
    help = 'Carga ciclorrutas desde un archivo GeoJSON (LineString o MultiLineString).'

    def add_arguments(self, parser):
        parser.add_argument('archivo', help='Ruta del archivo .geojson')
        parser.add_argument('--srid', type=int, default=4326,
                            help='Sistema de coordenadas del archivo (por defecto 4326, lat/lng).')
        parser.add_argument('--clear', action='store_true', help='Borra las ciclorrutas existentes antes de cargar.')

    def handle(self, *args, **opts):
        try:
            with open(opts['archivo'], encoding='utf-8-sig') as f:
                data = json.load(f)
        except (OSError, ValueError) as e:
            raise CommandError(f'No se pudo leer el archivo: {e}')

        features = data.get('features', [data] if data.get('type') == 'Feature' else [])
        bikeways, skipped = [], 0
        for feat in features:
            geom = feat.get('geometry') or {}
            lines = {'LineString': [geom.get('coordinates')],
                     'MultiLineString': geom.get('coordinates')}.get(geom.get('type'))
            if not lines:
                skipped += 1
                continue
            props = feat.get('properties') or {}
            name = next((str(props[k]) for k in NAME_KEYS if props.get(k)), '')[:150]
            for coords in lines:
                pts = [(c[0], c[1]) for c in coords or []]  # descarta la altura (z)
                if len(pts) < 2:
                    skipped += 1
                    continue
                line = LineString(pts, srid=opts['srid'])
                if opts['srid'] != 4326:
                    line.transform(4326)
                bikeways.append(Bikeway(name=name, path=line))

        with transaction.atomic():
            if opts['clear']:
                Bikeway.objects.all().delete()
            Bikeway.objects.bulk_create(bikeways, batch_size=500)

        self.stdout.write(self.style.SUCCESS(f'{len(bikeways)} tramos cargados, {skipped} omitidos.'))
