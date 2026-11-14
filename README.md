# 🚲 BiciSegura

**Sistema de planificación y seguridad de rutas para ciclistas en Bogotá.**

## 📌 Descripción

BiciSegura ayuda a los ciclistas de Bogotá a elegir rutas más seguras. La aplicación combina el mapa de ciclorrutas con los reportes de incidentes de la comunidad para calcular rutas, comparar alternativas según su nivel de seguridad y avisar de peligros durante el recorrido.

## 🎯 Problema

La inseguridad, incluso la percibida, es una de las principales razones por las que las personas usan menos la bicicleta. Las estadísticas oficiales suelen registrar solo los choques formales y dejan por fuera los casi accidentes, y el ciclista casi no tiene información sobre qué tan peligrosa es cada calle o intersección. BiciSegura busca cubrir ese vacío con datos aportados por la propia comunidad ciclista.

## ✨ Funcionalidades principales

**Rol Ciclista**

* Registro, inicio de sesión, recuperación de contraseña y gestión de perfil.

* Cálculo de rutas entre dos puntos, con preferencias (más segura, más rápida, más ciclorrutas).

* Comparación de alternativas con un índice de seguridad por ruta.

* Mapa con ciclorrutas, incidentes y zonas inseguras, con filtros y detalle.

* Reporte de incidentes y confirmación de su estado por parte de otros usuarios.

* Recorrido activo con cronómetro y alertas de peligros cercanos.

* Historial de recorridos (con nombre editable), puntos y reputación, y gestión de reportes propios.

**Rol Administrador**

* Moderación de reportes denunciados (validar, editar o eliminar).

* Gestión de cuentas de usuarios.

* Tablero de estadísticas del sistema.

## 🚧 Estado actual del proyecto

✅ Listo · 🟡 Parcial · ⏳ Pendiente

| Funcionalidad | Estado |
| ----- | ----- |
| Modelos de usuario (con roles), incidentes, votos, recorridos, rutas y ciclorrutas (PostGIS) | ✅ Listo |
| Registro, inicio de sesión (JWT) y cierre de sesión en el frontend | ✅ Listo |
| Modo invitado para pruebas (botón en el login) | 🟡 Temporal: se quita antes de la entrega |
| Diseño responsive (celular y PC), logo y título de la pestaña | ✅ Listo |
| Mapa de Bogotá con incidentes, íconos por tipo y detalle | ✅ Listo |
| Reporte de incidentes haciendo clic en el mapa | ✅ Listo |
| Filtros de incidentes por tipo y fecha | ✅ Listo |
| Confirmar un incidente ("Sigue ocurriendo") o marcarlo como solucionado | ✅ Listo: un voto por usuario, incidente y hora (no las dos opciones a la vez); 3 usuarios distintos lo resuelven |
| Zonas inseguras en el mapa | ✅ Listo |
| Cálculo de rutas con preferencias e índice de seguridad | 🟡 El índice es real, pero los trazados son de prueba (línea recta y "L"), no siguen las calles |
| Comparación de rutas y elección de ruta | ✅ Listo |
| Ciclorrutas en el mapa y porcentaje de ciclorruta por ruta | 🟡 Funciona, pero faltan cargar los datos reales de Bogotá |
| Recorrido activo: cronómetro, pausa, finalizar, renombrar y peligros cercanos | 🟡 Falta el aviso sonoro o por vibración |
| Historial de recorridos y perfil | 🟡 Se puede consultar; falta editar el perfil |
| Recuperación de contraseña | ⏳ Pendiente |
| Reputación y puntos | ⏳ Pendiente |
| Editar o borrar reportes propios; restringir quién puede modificar reportes | ⏳ Pendiente |
| Panel de administración (moderación y estadísticas) | ⏳ Pendiente (por ahora solo el panel de Django en `/admin/`) |

## 🛠️ Tecnologías

* **Frontend:** Vue.js 3 + Leaflet + Vite + Pinia (instalado, aún sin uso) + Axios

* **Backend:** Python / Django REST API + SimpleJWT + GeoDjango

* **Base de Datos:** PostgreSQL + extensión espacial PostGIS (Docker)

* **Mapa y direcciones:** OpenStreetMap (mapa base y búsqueda de direcciones con Nominatim)

## 📂 Estructura del repositorio

```text
bicisegura/
├── backend/                       # Backend API (Django REST Framework)
│   ├── bicisegura_api/            # Configuración principal (settings, urls globales)
│   ├── core/                      # App principal
│   │   ├── migrations/            # Migraciones de la base de datos
│   │   ├── management/
│   │   │   └── commands/
│   │   │       └── load_bikeways.py   # Carga ciclorrutas desde un GeoJSON
│   │   ├── models.py              # User, IncidentReport, ReportVote, Bikeway, Route y Trip
│   │   ├── serializers.py         # Serializadores (usuarios, reportes, rutas y recorridos)
│   │   ├── services.py            # Cálculo de rutas, índice de seguridad y zonas inseguras
│   │   ├── views.py               # Vistas de la API
│   │   ├── urls.py                # Rutas de la API
│   │   └── admin.py               # Modelos en el panel de Django (/admin/)
│   └── manage.py                  # Script de ejecución de Django
├── frontend/                      # Interfaz de usuario (Vue.js 3 + Vite)
│   ├── public/
│   │   ├── logo.svg               # Logo de la cabecera
│   │   └── favicon.svg            # Ícono de la pestaña del navegador
│   ├── src/                       # Código fuente
│   │   ├── assets/
│   │   │   └── markers/           # Íconos SVG de los marcadores (7 archivos)
│   │   ├── lib/
│   │   │   ├── api.js             # Cliente de la API (token, errores y formatos)
│   │   │   └── map.js             # Mapa Leaflet, tipos de incidente e íconos
│   │   ├── router/                # Navegación (Vue Router) y guardia de sesión
│   │   ├── views/                 # Pantallas
│   │   │   ├── LoginView.vue          # Inicio de sesión y registro
│   │   │   ├── RutasView.vue          # Planificador: origen, destino y preferencia
│   │   │   ├── ElegirRutaView.vue     # Comparar rutas e iniciar recorrido
│   │   │   ├── RecorridoView.vue      # Recorrido activo: cronómetro, nombre y peligros
│   │   │   ├── IncidentesView.vue     # Incidentes, zonas inseguras y ciclorrutas
│   │   │   ├── ReportarView.vue       # Reportar un incidente
│   │   │   └── PerfilView.vue         # Perfil e historial de recorridos
│   │   ├── App.vue                # Componente raíz (cabecera y menú)
│   │   ├── style.css              # Estilos globales
│   │   └── main.js                # Punto de entrada
│   ├── index.html                 # Página base (título de la pestaña)
│   └── package.json               # Dependencias y scripts de Node
├── docs/                          # Documentos de diseño y arquitectura
│   ├── Workshop_1.pdf
│   ├── Workshop_2.pdf
│   ├── Workshop_2_part_1.pdf
│   └── Workshop_2_part_2.pdf
├── docker-compose.yml             # Base de datos PostGIS
├── .gitignore                     # Exclusiones de Git (venv, node_modules, __pycache__)
└── README.md                      # Documentación principal
```

## ⚙️ Instalación y Configuración Local

### Requisitos previos

* [Docker Desktop](https://www.docker.com/products/docker-desktop/)
* Python 3.12 o superior
* Node.js y npm
* Librerías GDAL/GEOS para GeoDjango (en Windows, mediante [OSGeo4W](https://trac.osgeo.org/osgeo4w/))

### 1. Base de Datos (Docker)

Desde la raíz del proyecto, levanta el contenedor con PostGIS:

```bash
docker compose up -d
```

Esto crea la base `bicisegura_db` (usuario `postgres`, contraseña `bici_admin`) en el puerto `5433`.

> Si antes creaste un contenedor llamado `bicisegura_db` con otro comando, elimínalo primero con `docker rm -f bicisegura_db`.

### 2. Backend (Django)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install django djangorestframework djangorestframework-gis psycopg2-binary django-cors-headers djangorestframework-simplejwt
python manage.py migrate
python manage.py runserver
```

La API queda disponible en `http://127.0.0.1:8000/api/`. Las migraciones ya están en el repositorio, así que basta con `migrate`. Si cambias los modelos, ejecuta antes `python manage.py makemigrations core`.

Para entrar al panel de Django (`/admin/`), crea un administrador con `python manage.py createsuperuser`.

**Solo en Windows:** `settings.py` carga GDAL y GEOS desde OSGeo4W. Si tu instalación está en otra ruta, define la variable de entorno `OSGEO4W_ROOT`, y verifica que el número de `gdal313.dll` en `settings.py` coincida con el de la carpeta `bin` de tu instalación.

#### Cargar las ciclorrutas

Las ciclorrutas no vienen incluidas. Para verlas en el mapa y para que cuenten en el cálculo de rutas, carga un archivo GeoJSON (por ejemplo, los datos abiertos de IDECA):

```powershell
python manage.py load_bikeways archivo.geojson
```

Opciones: `--srid <código>` si el archivo no está en latitud y longitud (EPSG:4326), y `--clear` para reemplazar las ciclorrutas existentes.

#### Variables de entorno (opcionales)

Si no se definen, se usan los valores de desarrollo local.

| Variable | Descripción | Valor por defecto |
| ----- | ----- | ----- |
| `DJANGO_SECRET_KEY` | Clave secreta de Django | clave de desarrollo |
| `DJANGO_DEBUG` | Modo depuración (`True` / `False`) | `True` |
| `DJANGO_ALLOWED_HOSTS` | Hosts permitidos, separados por coma | vacío |
| `DB_NAME` | Nombre de la base de datos | `bicisegura_db` |
| `DB_USER` | Usuario de la base de datos | `postgres` |
| `DB_PASSWORD` | Contraseña de la base de datos | `bici_admin` |
| `DB_HOST` | Host de la base de datos | `localhost` |
| `DB_PORT` | Puerto de la base de datos | `5433` |
| `OSGEO4W_ROOT` | Ruta de OSGeo4W (solo Windows) | ruta local del desarrollador |

> Para cualquier despliegue fuera de tu equipo, define estas variables y no uses los valores por defecto.

### 3. Frontend (Vue.js)

```powershell
cd frontend
npm install
npm run dev
```

Abre `http://localhost:5173`. El backend debe estar corriendo, ya que el frontend consume la API en `http://127.0.0.1:8000`.

### 4. Probar la aplicación

1. Abre `http://localhost:5173`. La app te lleva al inicio de sesión: regístrate con tu correo o usa **Entrar sin iniciar sesión (solo pruebas)**.
2. En **Rutas**, marca el origen y el destino tocando el mapa (o escribe una dirección) y elige la preferencia. Pulsa **Buscar rutas**.
3. En **Elige tu ruta**, compara tiempo, distancia e índice de seguridad, y pulsa **Iniciar recorrido**.
4. Durante el recorrido puedes ver el cronómetro, pausar, reanudar, cambiarle el nombre y finalizar.
5. En **Incidentes**, filtra por tipo y fecha, toca un marcador para ver el detalle y revisa las pestañas de zonas inseguras y ciclorrutas. Con sesión iniciada puedes confirmar un incidente o marcarlo como solucionado.
6. En **Reportar**, toca el mapa, elige el tipo de incidente, la severidad y escribe una descripción.
7. En **Perfil** ves tus datos y el historial de recorridos. Tocar un recorrido lo abre y permite renombrarlo.

> Confirmar y solucionar incidentes exigen sesión. En modo invitado esos botones aparecen desactivados.

## 🖥️ Pantallas del frontend

| Ruta | Pantalla |
| ----- | ----- |
| `/login` | Inicio de sesión y registro (entrar al login cierra la sesión) |
| `/` | Rutas: planificador |
| `/elegir` | Elige tu ruta: comparar alternativas |
| `/recorrido/:id` | Recorrido activo o finalizado |
| `/incidentes` | Incidentes, zonas inseguras y ciclorrutas |
| `/reportar` | Reportar un incidente |
| `/perfil` | Perfil e historial de recorridos |

## 🗺️ Rutas y Endpoints (API)

Todas las peticiones utilizan el prefijo `/api/`. Cuando se indica sesión, se envía el encabezado `Authorization: Bearer <token>`.

**Autenticación y usuario**

| Método | Endpoint | Sesión | Descripción |
| ----- | ----- | ----- | ----- |
| `POST` | `/api/auth/register/` | No | Registra un nuevo usuario |
| `POST` | `/api/auth/login/` | No | Autenticación de usuario (JWT) |
| `POST` | `/api/auth/refresh/` | No | Renueva un token JWT expirado |
| `GET` | `/api/auth/me/` | Sí | Datos del usuario, con su número de reportes y recorridos |

**Reportes de incidentes**

| Método | Endpoint | Sesión | Descripción |
| ----- | ----- | ----- | ----- |
| `GET` | `/api/reports/` | No | Lista incidentes activos (GeoJSON). Filtros: `type` (varios, separados por coma), `severity` y `days` |
| `POST` | `/api/reports/` | Opcional | Crea un reporte. Con sesión queda asociado al autor |
| `GET` `PUT` `PATCH` `DELETE` | `/api/reports/<id>/` | No | Consulta, edita o elimina un reporte |
| `GET` | `/api/reports/nearby/?lat=&lng=&radius=` | No | Incidentes cercanos, del más próximo al más lejano (radio en metros: 300 por defecto, máximo 5000) |
| `POST` | `/api/reports/<id>/confirm/` | Sí | "Sigue ocurriendo". Un voto por usuario, reporte y hora: si ya votó (con cualquiera de las dos opciones) responde `429` con `retry_after_s` |
| `POST` | `/api/reports/<id>/solve/` | Sí | "Ya se solucionó". Misma regla de una hora. Con 3 usuarios distintos el reporte pasa a resuelto |

**Rutas, recorridos, zonas y ciclorrutas**

| Método | Endpoint | Sesión | Descripción |
| ----- | ----- | ----- | ----- |
| `POST` | `/api/routes/search/` | No | Devuelve 3 rutas (más segura, más rápida, más ciclorrutas) con distancia, tiempo e índice de seguridad. La preferida va primero |
| `GET` | `/api/routes/<id>/` | No | Detalle de una ruta |
| `POST` | `/api/trips/` | Opcional | Inicia un recorrido sobre una ruta |
| `GET` | `/api/trips/` | Sí | Historial de recorridos del usuario |
| `GET` | `/api/trips/<id>/` | No | Detalle de un recorrido |
| `PATCH` | `/api/trips/<id>/` | Dueño | Pausa, reanuda o finaliza el recorrido (`status`) y cambia su nombre (`name`) |
| `GET` | `/api/zones/unsafe/?threshold=60` | No | Celdas de unos 550 m con índice de seguridad bajo (GeoJSON) |
| `GET` | `/api/bikeways/?bbox=` | No | Ciclorrutas (GeoJSON). `bbox` = `minLng,minLat,maxLng,maxLat` |

> **Votos:** cada usuario tiene un solo voto vigente por reporte. Pasada una hora puede votar otra vez y, si elige la otra opción, su voto se cambia (nunca cuenta en las dos). Los reportes devuelven `my_vote` (`confirm`, `solve` o `null`) y `vote_wait_s` (segundos que faltan para poder votar de nuevo).

> **Nota de desarrollo:** por ahora los reportes y los recorridos de invitados se pueden crear y modificar sin autenticación para facilitar las pruebas. Esto se restringirá antes de la entrega. Los recorridos que pertenecen a un usuario solo los modifica su dueño.

### Ejemplos de peticiones

**Registro** (`POST /api/auth/register/`):

```json
{
  "full_name": "Nombre Apellido",
  "email": "correo@ejemplo.com",
  "password": "minimo8caracteres"
}
```

**Login** (`POST /api/auth/login/`): se autentica con el correo y devuelve `access` y `refresh`.

```json
{
  "email": "correo@ejemplo.com",
  "password": "minimo8caracteres"
}
```

**Crear reporte** (`POST /api/reports/`): usa formato GeoJSON, con las coordenadas en orden `[longitud, latitud]`.

```json
{
  "type": "Feature",
  "geometry": { "type": "Point", "coordinates": [-74.0817, 4.6097] },
  "properties": {
    "type": "theft",
    "severity": "high",
    "description": "Descripción del incidente"
  }
}
```

**Buscar rutas** (`POST /api/routes/search/`): `preference` es opcional (`safest` por defecto). Devuelve un GeoJSON con tres rutas; cada una trae `kind`, `distance_m`, `duration_s`, `safety_index` (0 a 100) y `bikeway_pct`.

```json
{
  "origin": { "lat": 4.6097, "lng": -74.0817 },
  "destination": { "lat": 4.6486, "lng": -74.0620 },
  "preference": "safest"
}
```

**Iniciar un recorrido** (`POST /api/trips/`) con el `id` de una de las rutas devueltas:

```json
{ "route": 12 }
```

**Pausar, reanudar o finalizar** (`PATCH /api/trips/<id>/`) con `paused`, `active` o `finished`. Un recorrido finalizado no se puede reabrir:

```json
{ "status": "paused" }
```

**Renombrar** (`PATCH /api/trips/<id>/`), durante o después del recorrido. Vacío vuelve a "Recorrido N":

```json
{ "name": "Casa a la U" }
```

La respuesta de un recorrido incluye `elapsed_s`: los segundos transcurridos sin contar las pausas.

**Valores válidos:**

| Campo | Valores |
| ----- | ----- |
| `type` | `theft`, `pothole`, `flooding`, `roadwork`, `harassment`, `accident`, `obstruction`, `other` |
| `severity` | `low`, `medium`, `high` |
| `preference` | `safest`, `fastest`, `bikeways` |
| `status` (recorrido) | `active`, `paused`, `finished` |

> El formulario del frontend ofrece `theft`, `pothole`, `accident`, `roadwork`, `flooding` y `other`. Los tipos `harassment` y `obstruction` aún no tienen botón ni ícono propio: usan el ícono por defecto.

### Cómo se calcula la seguridad

* **Índice de seguridad de una ruta:** va de 0 (peligrosa) a 100 (segura). Cada incidente activo a menos de 100 m del trazado le resta puntos, más cuanto mayor sea su severidad.
* **Zonas inseguras:** el mapa se divide en celdas de unos 550 m. Aparece como insegura la celda cuyo índice baja del umbral (60 por defecto).
* **Trazados:** por ahora son de prueba (una línea recta y dos en "L" entre origen y destino). Para rutas reales, basta con reemplazar la función `candidate_paths` de `backend/core/services.py` por una llamada a un motor como OSRM, OpenRouteService o pgRouting.

## 🎨 Íconos de los marcadores

Los íconos están en `frontend/src/assets/markers/`:

| Archivo | Tipo de incidente |
| ----- | ----- |
| `theft.svg` | Robo |
| `accident.svg` | Accidente |
| `pothole.svg` | Peligro en la vía / Bache |
| `roadwork.svg` | Obra |
| `flooding.svg` | Inundación |
| `other.svg` | Otro |
| `default.svg` | Cualquier tipo sin ícono propio |

Para usar tus propias imágenes, reemplaza los archivos conservando el nombre (o cambia los `import` en `frontend/src/lib/map.js` si usas otro formato) y ajusta `iconSize` e `iconAnchor` en ese mismo archivo si el tamaño no es 32×42 px. Si agregas tipos nuevos al modelo, añade su ícono en `ICONS` y su botón en `TYPES`.

## 🖼️ Logo y título

* El logo de la cabecera es `frontend/public/logo.svg`. Para cambiarlo, reemplaza ese archivo conservando el nombre; se ajusta a 40 px de alto en celular y 48 px en PC.
* El título de la pestaña del navegador está en `frontend/index.html` (`<title>`).
* El ícono de la pestaña es `frontend/public/favicon.svg`.

## 👥 Equipo

* Diego Alejandro Arévalo Guevara

* Brayan Camilo Gamba Herrera

* Andrés Sebastian Sanchez Quintero

* Juan Carlos Manrique Benavides

* Johan Alexander Peña Ortiz
