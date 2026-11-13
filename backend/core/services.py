"""
Lógica de rutas y seguridad de BiciSegura.

IMPORTANTE: las rutas son trazados de prueba (una línea recta y dos en "L" entre
origen y destino), no siguen las calles. Para rutas reales, reemplaza solo
`candidate_paths` por una llamada a un motor como OSRM, OpenRouteService o pgRouting.
El índice de seguridad y el porcentaje de ciclorruta sí se calculan con datos reales
(reportes activos y ciclorrutas cargadas).

Todas las coordenadas van como (lng, lat), el orden de GeoDjango.
"""
import math

SPEED_KMH = 15          # velocidad media supuesta en bicicleta
NEAR_M = 100            # un incidente afecta la ruta si está a menos de esta distancia del trazado
BIKEWAY_NEAR_M = 30     # un punto del trazado va "sobre" una ciclorruta si está a menos de esto
ROUTE_PENALTY = 8       # puntos que resta a la ruta un incidente de peso 1 junto al trazado
ZONE_PENALTY = 10       # puntos que resta a una zona un incidente de peso 1
CELL_DEG = 0.005        # tamaño de celda de las zonas: unos 550 m
SEVERITY_WEIGHT = {'low': 1, 'medium': 2, 'high': 3}

_COS = math.cos(math.radians(4.65))  # latitud de Bogotá, para pasar grados a metros


# --------------------------------------------------------------------------
# Geometría (en metros, con una proyección plana válida para una ciudad)
# --------------------------------------------------------------------------
def _proj(lng, lat):
    return (lng * 111320.0 * _COS, lat * 110540.0)


def _seg_dist(p, a, b):
    """Distancia de un punto a un segmento."""
    (px, py), (ax, ay), (bx, by) = p, a, b
    dx, dy = bx - ax, by - ay
    sq = dx * dx + dy * dy
    t = 0.0 if sq == 0 else max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / sq))
    return math.hypot(px - ax - t * dx, py - ay - t * dy)


def _length_m(coords):
    pts = [_proj(*c) for c in coords]
    return sum(math.dist(a, b) for a, b in zip(pts, pts[1:]))


def _samples(coords, step=50):
    """Puntos del trazado cada ~50 m."""
    pts = [_proj(*c) for c in coords]
    out = [pts[0]]
    for a, b in zip(pts, pts[1:]):
        n = max(1, math.ceil(math.dist(a, b) / step))
        out += [(a[0] + (b[0] - a[0]) * i / n, a[1] + (b[1] - a[1]) * i / n) for i in range(1, n + 1)]
    return out


# --------------------------------------------------------------------------
# Datos desde la base (los imports van dentro para poder probar sin Django)
# --------------------------------------------------------------------------
def _bbox_polygon(bbox):
    from django.contrib.gis.geos import Polygon
    poly = Polygon.from_bbox(bbox)
    poly.srid = 4326
    return poly


def _load_reports(bbox=None):
    """Reportes activos como (lng, lat, peso). El peso sube con la severidad."""
    from .models import IncidentReport
    qs = IncidentReport.objects.filter(state=IncidentReport.State.ACTIVE)
    if bbox:
        qs = qs.filter(location__within=_bbox_polygon(bbox))
    return [
        (p.x, p.y, SEVERITY_WEIGHT.get(sev, 1) * float(w))
        for p, sev, w in qs.values_list('location', 'severity', 'current_weight')
    ]


def _load_bikeway_segments(bbox):
    """Segmentos de ciclorruta del área, ya proyectados y con su caja para descartar rápido."""
    from .models import Bikeway
    t = BIKEWAY_NEAR_M
    segs = []
    for bw in Bikeway.objects.filter(path__intersects=_bbox_polygon(bbox)):
        pts = [_proj(c[0], c[1]) for c in bw.path.coords]
        for a, b in zip(pts, pts[1:]):
            segs.append((a, b, min(a[0], b[0]) - t, max(a[0], b[0]) + t, min(a[1], b[1]) - t, max(a[1], b[1]) + t))
    return segs


# --------------------------------------------------------------------------
# Índices
# --------------------------------------------------------------------------
def _safety_index(coords, reports):
    """0 (peligrosa) a 100 (segura): resta puntos por cada incidente a menos de NEAR_M del trazado."""
    pts = [_proj(*c) for c in coords]
    segs = list(zip(pts, pts[1:]))
    penalty = 0.0
    for lng, lat, weight in reports:
        p = _proj(lng, lat)
        if min(_seg_dist(p, a, b) for a, b in segs) <= NEAR_M:
            penalty += weight * ROUTE_PENALTY
    return max(0, round(100 - penalty))


def _bikeway_pct(coords, segs):
    """Porcentaje del trazado que va sobre una ciclorruta."""
    if not segs:
        return 0
    samples = _samples(coords)
    t = BIKEWAY_NEAR_M
    hits = sum(
        1 for p in samples
        if any(x0 <= p[0] <= x1 and y0 <= p[1] <= y1 and _seg_dist(p, a, b) <= t for a, b, x0, x1, y0, y1 in segs)
    )
    return round(100 * hits / len(samples))


# --------------------------------------------------------------------------
# Rutas
# --------------------------------------------------------------------------
def candidate_paths(origin, dest):
    """TRAZADOS DE PRUEBA: una recta y dos en "L". Cambia solo esta función por un motor de rutas real."""
    paths = [[origin, dest]]
    for corner in ((origin[0], dest[1]), (dest[0], origin[1])):
        paths.append([origin, corner, dest] if corner not in (origin, dest) else [origin, dest])
    return paths


def plan_routes(origin, dest, reports=None, bikeway_segs=None):
    """
    origin y dest son (lng, lat). Devuelve {'safest'|'fastest'|'bikeways': {...}} con
    coords, distance_m, duration_s, safety_index y bikeway_pct. Cada tipo recibe un trazado distinto.
    """
    pad = 0.01  # ~1 km alrededor para buscar reportes y ciclorrutas
    bbox = (min(origin[0], dest[0]) - pad, min(origin[1], dest[1]) - pad,
            max(origin[0], dest[0]) + pad, max(origin[1], dest[1]) + pad)
    if reports is None:
        reports = _load_reports(bbox)
    if bikeway_segs is None:
        bikeway_segs = _load_bikeway_segments(bbox)

    cands = []
    for coords in candidate_paths(origin, dest):
        dist = _length_m(coords)
        cands.append({
            'coords': coords,
            'distance_m': round(dist),
            'duration_s': round(dist / (SPEED_KMH / 3.6)),
            'safety_index': _safety_index(coords, reports),
            'bikeway_pct': _bikeway_pct(coords, bikeway_segs),
        })

    fastest = min(cands, key=lambda c: c['distance_m'])
    rest = [c for c in cands if c is not fastest]
    if rest[0]['bikeway_pct'] != rest[1]['bikeway_pct']:
        bikeways = max(rest, key=lambda c: c['bikeway_pct'])
        safest = next(c for c in rest if c is not bikeways)
    else:
        safest = max(rest, key=lambda c: c['safety_index'])
        bikeways = next(c for c in rest if c is not safest)
    return {'safest': safest, 'fastest': fastest, 'bikeways': bikeways}


# --------------------------------------------------------------------------
# Zonas inseguras
# --------------------------------------------------------------------------
def unsafe_zones(threshold=60, reports=None):
    """GeoJSON con las celdas (~550 m) cuyo índice de seguridad es menor que `threshold`."""
    if reports is None:
        reports = _load_reports()
    cells = {}
    for lng, lat, weight in reports:
        c = cells.setdefault((math.floor(lng / CELL_DEG), math.floor(lat / CELL_DEG)), [0.0, 0])
        c[0] += weight
        c[1] += 1
    features = []
    for (i, j), (weight, n) in cells.items():
        index = max(0, round(100 - weight * ZONE_PENALTY))
        if index >= threshold:
            continue
        x0, y0 = round(i * CELL_DEG, 6), round(j * CELL_DEG, 6)
        x1, y1 = round(x0 + CELL_DEG, 6), round(y0 + CELL_DEG, 6)
        features.append({
            'type': 'Feature',
            'geometry': {'type': 'Polygon', 'coordinates': [[[x0, y0], [x1, y0], [x1, y1], [x0, y1], [x0, y0]]]},
            'properties': {'safety_index': index, 'reports': n},
        })
    return {'type': 'FeatureCollection', 'features': features}
