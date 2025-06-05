# CodeAdmin

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://albertoprieto.github.io/VueCrud/)

**CodeAdmin** es una aplicación web integral para la gestión operativa y comercial de empresas de rastreo GPS. Desarrollada con Vue 3 y Vite, permite administrar IMEIs, cotizaciones, ventas, reportes de servicio, agenda de técnicos y mucho más. Utiliza PrimeVue para la interfaz y Pinia para la gestión del estado.

---

## Características principales

- **Gestión de IMEIs**: Registro, consulta, asignación y transferencia de IMEIs en inventario.
- **Gestión de Cotizaciones**: Crear, consultar, calendarizar y dar seguimiento a cotizaciones.
- **Gestión de Ventas**: Generación de notas de venta, historial, edición y descarga en PDF.
- **Gestión de Reportes de Servicio**: Registro y edición de reportes detallados de instalaciones y servicios.
- **Agenda y Calendario**: Visualización y asignación de eventos, instalaciones y servicios a técnicos.
- **Gestión de Clientes**: Registro, edición y consulta de clientes, teléfonos, plataformas y usuarios asociados.
- **Gestión de Técnicos y Usuarios**: Control de accesos, roles y asignaciones.
- **Inventario de Artículos**: Control de stock, existencias, transferencias y reportes de inventario.
- **Panel de indicadores**: Visualización de ventas, instalaciones, stock y alertas operativas.
- **Autenticación segura**: Login con OAuth2/JWT.
- **Exportación de datos**: Descarga de reportes e inventario en Excel/PDF.
- **Notificaciones y feedback visual**: Toasts, loaders y validaciones en toda la app.

---

## Tecnologías Utilizadas

- **Vue 3**: Framework de JavaScript para construir interfaces de usuario.
- **Vite**: Herramienta de construcción rápida para proyectos de Vue.
- **PrimeVue**: Biblioteca de componentes de interfaz de usuario para Vue.
- **Pinia**: Biblioteca de gestión del estado para Vue.
- **Vue Router**: Enrutador oficial para Vue.js.
- **Axios**: Cliente HTTP para realizar solicitudes a APIs.
- **Python FastAPI**: Backend API RESTful.
- **MySQL**: Base de datos relacional.
- **pdfmake**: Generación de PDFs en el frontend.
- **FullCalendar**: Biblioteca para la gestión de calendarios.
- **CryptoJS**: Biblioteca para criptografía en JavaScript.
- **Luxon**: Biblioteca para manejar fechas y horas en JavaScript.

---

## Instalación

1. Clona el repositorio:
   ```sh
   git clone 
   cd codeadmin
   ```

2. Instala las dependencias:
   ```sh
   npm install
   ```

3. Crea y configura tu archivo `.env` con las variables necesarias (ver `.env.example` si existe).

4. Inicia el servidor de desarrollo:
   ```sh
   npm run dev
   ```

5. El backend (FastAPI) debe estar corriendo y configurado para conectarse a tu base de datos MySQL.

---

## Estructura del proyecto

```
src/
├── App.vue
├── assets/
│   ├── base.css
│   └── main.css
├── components/
│   ├── HelloWorld.vue
│   ├── icons/
│   └── TheWelcome.vue
├── modules/
│   ├── CalendarioCotizaciones.vue
│   ├── Consultar.vue
│   ├── ConsultarCotizaciones.vue
│   ├── ConsultarReportes.vue
│   ├── Cotizacion.vue
│   ├── CrearEvento.vue
│   ├── dashboard.vue
│   ├── home.vue
│   ├── informacion.vue
│   ├── login.vue
│   ├── Registrar.vue
│   └── Reporte.vue
├── router/
│   └── index.js
├── services/
│   └── DataAPI.js
├── stores/
│   ├── acquiredStore.js
│   ├── counter.js
│   ├── eventosStore.js
│   ├── itemStore.js
│   ├── loginStore.js
│   ├── paymentsStore.js
│   ├── purchasesStore.js
│   ├── quotationStore.js
│   └── reportesStore.js
├── views/
│   ├── AboutView.vue
│   └── HomeView.vue
└── main.js
```

---

## Contribución

Abrir un issue para discutir cambios importantes antes de hacer un PR.


---
