# 🚲 BiciSegura

**Sistema de planificación y seguridad de rutas para ciclistas en Bogotá.**

## 📌 Descripción

BiciSegura ayuda a los ciclistas de Bogotá a elegir rutas más seguras. La aplicación combina el mapa de ciclorrutas con los reportes de incidentes de la comunidad para calcular rutas, comparar alternativas según su nivel de seguridad y avisar de peligros durante el recorrido.

## 🎯 Problema

La inseguridad, incluso la percibida, es una de las principales razones por las que las personas usan menos la bicicleta. Las estadísticas oficiales suelen registrar solo los choques formales y dejan por fuera los casi accidentes, y el ciclista casi no tiene información sobre qué tan peligrosa es cada calle o intersección. BiciSegura busca cubrir ese vacío con datos aportados por la propia comunidad ciclista.

## ✨ Funcionalidades principales

**Rol Ciclista**
- Registro, inicio de sesión, recuperación de contraseña y gestión de perfil.
- Cálculo de rutas entre dos puntos, con preferencias (más segura, más rápida, más ciclorrutas).
- Comparación de alternativas con un índice de seguridad por ruta.
- Mapa con ciclorrutas, incidentes y zonas inseguras, con filtros y detalle.
- Reporte de incidentes y confirmación de su estado por parte de otros usuarios.
- Recorrido activo con alertas de peligros cercanos.
- Historial de rutas, puntos y reputación, y gestión de reportes propios.

**Rol Administrador**
- Moderación de reportes denunciados (validar, editar o eliminar).
- Gestión de cuentas de usuarios.
- Tablero de estadísticas del sistema.

## 🛠️ Tecnologías

- **Frontend:** Vue.js + Leaflet
- **Backend:** Python / Django REST API
- **Base de Datos:** PostgreSQL + extensión espacial PostGIS

## 📂 Estructura del repositorio

```text
bicisegura/
├── backend/                   # Lógica de la API REST (Django) y modelos
├── frontend/                  # Interfaz de usuario SPA (Vue.js)
├── docs/                      # Documentos de diseño y arquitectura
│   ├── Workshop_1.pdf      
│   ├── Workshop_2.pdf           
│   ├── Workshop_2_part_1.pdf      
│   └── Workshop_2_part_2.pdf           
└── README.md
```

## 👥 Equipo

- Diego Alejandro Arévalo Guevara
- Brayan Camilo Gamba Herrera
- Andrés Sebastian Sanchez Quintero
- Juan Carlos Manrique Benavides
- Johan Alexander Peña Ortiz