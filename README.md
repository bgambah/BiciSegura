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

## 🖼️ Mockups

Los diseños de las pantallas (11 en total) están en la carpeta [`/docs/mockups`](docs/mockups). Las más importantes son:

| # | Pantalla | Propósito |
|---|----------|-----------|
| 01 | Inicio de sesión y registro | Acceso y creación de cuenta |
| 02 | Planear una ruta | Elegir origen, destino y preferencias |
| 03 | Comparar alternativas | Escoger entre rutas según tiempo, distancia y seguridad |
| 04 | Incidentes, filtros y detalle | Ver riesgos en el mapa y confirmar su estado |
| 05 | Reportar un incidente | Aportar información a la comunidad |
| 06 | Recorrido activo y alertas | Navegación con avisos en tiempo real |
| 09 | Administración – Cola de moderación | Revisar y validar reportes |

## 📂 Estructura del repositorio

```
bicisegura/
├── docs/
│   ├── Workshop_1.pdf      # Requerimientos e historias de usuario
│   └── mockups/            # Pantallas de la aplicación
└── README.md
```

## 👥 Equipo

- Diego Alejandro Arévalo Guevara
- Brayan Camilo Gamba Herrera
- Andrés Sebastian Sanchez Quintero
- Juan Carlos Manrique Benavides
- Johan Alexander Peña Ortiz


