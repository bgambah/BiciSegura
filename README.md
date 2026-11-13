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

* Recorrido activo con alertas de peligros cercanos.

* Historial de rutas, puntos y reputación, y gestión de reportes propios.

**Rol Administrador**

* Moderación de reportes denunciados (validar, editar o eliminar).

* Gestión de cuentas de usuarios.

* Tablero de estadísticas del sistema.

## 🚧 Estado actual del proyecto

| Funcionalidad | Estado |
| ----- | ----- |
| Modelos de usuario (con roles) e incidentes (con ubicación en PostGIS) | ✅ Listo |
| Registro de usuarios y autenticación JWT (API) | ✅ Listo (sin pantallas en el frontend aún) |
| Mapa de Bogotá con incidentes existentes | ✅ Listo |
| Reporte de incidentes haciendo clic en el mapa | ✅ Listo |
| Íconos distintos por tipo de incidente | ✅ Listo |
| Login, registro y perfil en el frontend | ⏳ Pendiente |
| Cálculo de rutas e índice de seguridad | ⏳ Pendiente |
| Ciclorrutas, filtros y zonas inseguras | ⏳ Pendiente |
| Confirmación de reportes, reputación e historial | ⏳ Pendiente |
| Recorrido activo con alertas | ⏳ Pendiente |
| Panel de administración (moderación y estadísticas) | ⏳ Pendiente |

## 🛠️ Tecnologías

* **Frontend:** Vue.js 3 + Leaflet + Vite + Pinia + Axios

* **Backend:** Python / Django REST API + SimpleJWT + GeoDjango

* **Base de Datos:** PostgreSQL + extensión espacial PostGIS (Docker)

## 📂 Estructura del repositorio

```text
bicisegura/
├── backend/                   # Backend API (Django REST Framework)
│   ├── bicisegura_api/        # Configuración principal (settings, urls globales)
│   ├── core/                  # App principal
│   │   ├── migrations/        # Migraciones de la base de datos
│   │   ├── models.py          # User e IncidentReport
│   │   ├── serializers.py     # Serializadores (registro y reportes en GeoJSON)
│   │   ├── views.py           # Vistas de la API
│   │   └── urls.py            # Rutas de la API
│   └── manage.py              # Script de ejecución de Django
├── frontend/                  # Interfaz de usuario (Vue.js 3 + Vite)
│   ├── src/                   # Código fuente
│   │   ├── assets/
│   │   │   └── markers/       # Íconos SVG de los marcadores (theft, accident, pothole, default)
│   │   ├── router/            # Configuración de navegación (Vue Router)
│   │   ├── views/             # Vistas/Pantallas (HomeView.vue: mapa y reportes)
│   │   ├── App.vue            # Componente raíz
│   │   └── main.js            # Punto de entrada
│   └── package.json           # Dependencias y scripts de Node
├── docs/                      # Documentos de diseño y arquitectura
│   ├── Workshop_1.pdf
│   ├── Workshop_2.pdf
│   ├── Workshop_2_part_1.pdf
│   └── Workshop_2_part_2.pdf
├── docker-compose.yml         # Base de datos PostGIS
├── .gitignore                 # Exclusiones de Git (venv, node_modules, __pycache__)
└── README.md                  # Documentación principal
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

La API queda disponible en `http://127.0.0.1:8000/api/`. Para entrar al panel de Django (`/admin/`), crea un administrador con `python manage.py createsuperuser`.

**Solo en Windows:** `settings.py` carga GDAL y GEOS desde OSGeo4W. Si tu instalación está en otra ruta, define la variable de entorno `OSGEO4W_ROOT`, y verifica que el número de `gdal313.dll` en `settings.py` coincida con el de la carpeta `bin` de tu instalación.

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

1. Abre el mapa en `http://localhost:5173`.
2. Haz clic en cualquier punto del mapa.
3. Elige el tipo de incidente, la severidad y escribe una descripción.
4. Pulsa **Enviar Reporte**: el incidente aparece en el mapa con el ícono de su tipo.

## 🗺️ Rutas y Endpoints (API)

Todas las peticiones utilizan el prefijo `/api/`.

| Método | Endpoint | Descripción |
| ----- | ----- | ----- |
| `POST` | `/api/auth/register/` | Registra un nuevo usuario |
| `POST` | `/api/auth/login/` | Autenticación de usuario (JWT) |
| `POST` | `/api/auth/refresh/` | Renueva un token JWT expirado |
| `GET` | `/api/reports/` | Lista incidentes activos (GeoJSON) |
| `POST` | `/api/reports/` | Crea un nuevo reporte |
| `GET` `PUT` `PATCH` `DELETE` | `/api/reports/<id>/` | Consulta, edita o elimina un reporte |

> **Nota de desarrollo:** por ahora los endpoints de reportes permiten el acceso sin autenticación para facilitar las pruebas. Esto se restringirá cuando el frontend incorpore el inicio de sesión.

### Ejemplos de peticiones

**Registro** (`POST /api/auth/register/`):

```json
{
  "full_name": "Nombre Apellido",
  "email": "correo@ejemplo.com",
  "password": "minimo8caracteres"
}
```

**Login** (`POST /api/auth/login/`): se autentica con el correo.

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

**Valores válidos:**

| Campo | Valores |
| ----- | ----- |
| `type` | `theft`, `pothole`, `flooding`, `roadwork`, `harassment`, `accident`, `obstruction`, `other` |
| `severity` | `low`, `medium`, `high` |

> El formulario del frontend ofrece por ahora `theft`, `accident` y `pothole`. Para los demás tipos se usa el ícono por defecto.

## 🎨 Íconos de los marcadores

Los íconos están en `frontend/src/assets/markers/`:

| Archivo | Tipo de incidente |
| ----- | ----- |
| `theft.svg` | Robo |
| `accident.svg` | Accidente |
| `pothole.svg` | Peligro en la vía / Hueco |
| `default.svg` | Cualquier otro tipo |

Para usar tus propias imágenes, reemplaza los archivos conservando el nombre (o cambia los `import` en `HomeView.vue` si usas otro formato) y ajusta `iconSize` e `iconAnchor` si el tamaño no es 32×42 px.

## 👥 Equipo

* Diego Alejandro Arévalo Guevara

* Brayan Camilo Gamba Herrera

* Andrés Sebastian Sanchez Quintero

* Juan Carlos Manrique Benavides

* Johan Alexander Peña Ortiz