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

## 🛠️ Tecnologías

* **Frontend:** Vue.js + Leaflet + Vite + Pinia

* **Backend:** Python / Django REST API + SimpleJWT

* **Base de Datos:** PostgreSQL + extensión espacial PostGIS (Docker)

## 📂 Estructura del repositorio

```text
bicisegura/
├── backend/                   # Backend API (Django REST Framework)
│   ├── bicisegura_api/        # Configuración principal (settings, urls globales)
│   ├── core/                  # App principal (models, views, serializers, urls)
│   └── manage.py              # Script de ejecución de Django
├── frontend/                  # Interfaz de usuario (Vue.js 3 + Vite)
│   ├── src/                   # Código fuente
│   │   ├── router/            # Configuración de navegación (Vue Router)
│   │   ├── views/             # Vistas/Pantallas (HomeView.vue, etc.)
│   │   ├── App.vue            # Componente raíz
│   │   └── main.js            # Punto de entrada
│   └── package.json           # Dependencias y scripts de Node
├── docs/                      # Documentos de diseño y arquitectura
│   ├── Workshop_1.pdf      
│   ├── Workshop_2.pdf           
│   ├── Workshop_2_part_1.pdf      
│   └── Workshop_2_part_2.pdf           
├── .gitignore                 # Exclusiones de Git (venv, node_modules)
└── README.md                  # Documentación principal
```

## ⚙️ Instalación y Configuración Local

### 1. Base de Datos (Docker)

Levanta el contenedor con PostGIS:

```bash
docker run --name bicisegura_db -e POSTGRES_USER=postgres -e POSTGRES_PASSWORD=postgres -e POSTGRES_DB=bicisegura -p 5433:5432 -d postgis/postgis
```

### 2. Backend (Django)

```powershell
cd backend
python -m venv venv
.\venv\Scripts\activate
pip install django djangorestframework djangorestframework-gis psycopg2 django-cors-headers djangorestframework-simplejwt
python manage.py makemigrations
python manage.py migrate
python manage.py runserver
```

### 3. Frontend (Vue.js)

```powershell
cd frontend
npm install
npm run dev
```

## 🗺️ Rutas y Endpoints (API)

Todas las peticiones utilizan el prefijo `/api/`.

| Método | Endpoint | Descripción | 
| ----- | ----- | ----- | 
| `POST` | `/api/auth/register/` | Registra un nuevo usuario | 
| `POST` | `/api/auth/login/` | Autenticación de usuario (JWT) | 
| `POST` | `/api/auth/refresh/` | Renueva un token JWT expirado | 
| `GET` | `/api/reports/` | Lista incidentes activos (GeoJSON) | 
| `POST` | `/api/reports/` | Crea un nuevo reporte | 

## 👥 Equipo

* Diego Alejandro Arévalo Guevara

* Brayan Camilo Gamba Herrera

* Andrés Sebastian Sanchez Quintero

* Juan Carlos Manrique Benavides

* Johan Alexander Peña Ortiz