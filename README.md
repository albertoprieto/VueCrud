# CodeAdmin

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://albertoprieto.github.io/VueCrud/)

CodeAdmin es una aplicación web desarrollada con Vue 3 y Vite. Esta aplicación permite gestionar IMEIs, cotizaciones, reportes y eventos en un calendario. Utiliza PrimeVue para los componentes de la interfaz de usuario y Pinia para la gestión del estado.

## Características

- **Gestión de IMEIs**: Permite registrar y consultar IMEIs en un inventario.
- **Gestión de Cotizaciones**: Permite crear, consultar y calendarizar cotizaciones.
- **Gestión de Reportes**: Permite generar reportes detallados de servicios realizados.
- **Calendario de Cotizaciones**: Visualiza y gestiona eventos relacionados con cotizaciones.
- **Autenticación**: Sistema de login para acceder a la aplicación.

## Tecnologías Utilizadas

- **Vue 3**: Framework de JavaScript para construir interfaces de usuario.
- **Vite**: Herramienta de construcción rápida para proyectos de Vue.
- **PrimeVue**: Biblioteca de componentes de interfaz de usuario para Vue.
- **Pinia**: Biblioteca de gestión del estado para Vue.
- **Vue Router**: Enrutador oficial para Vue.js.
- **Axios**: Cliente HTTP para realizar solicitudes a APIs.
- **CryptoJS**: Biblioteca para criptografía en JavaScript.
- **Luxon**: Biblioteca para manejar fechas y horas en JavaScript.
- **FullCalendar**: Biblioteca para la gestión de calendarios.

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/tu-usuario/codeadmin.git
   cd codeadmin
   ```

## ESTRUCTURA
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