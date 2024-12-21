# CodeAdmin

[![GitHub Pages](https://img.shields.io/badge/GitHub-Pages-blue?logo=github)](https://albertoprieto.github.io/VueCrud/)

CodeAdmin es una aplicación web desarrollada con Vue 3 y Vite. Esta aplicación permite gestionar pagos, envíos, compras y otros servicios. Utiliza PrimeVue para los componentes de la interfaz de usuario y Pinia para la gestión del estado.

## Características

- **Gestión de Pagos**: Permite visualizar y gestionar pagos pendientes, pagados y fallidos.
- **Monitoreo de Envíos**: Permite rastrear el estado de los envíos.
- **Gestión de Compras**: Permite visualizar las compras realizadas y su estado.
- **Servicios**: Permite visualizar y navegar entre diferentes servicios ofrecidos.
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

## Instalación

1. Clona el repositorio:
   ```sh
   git clone https://github.com/tu-usuario/codeadmin.git
   cd codeadmin

## Estructura del Proyecto

    WelcomeItem.vue
    modules/
        AdminItems.vue
        adquiridos.vue
        adquirir.vue
        dashboard.vue
    home.vue
    informacion.vue
    ServicioDetalle.vue
    router/
        index.js
    services/
    stores/
    views/