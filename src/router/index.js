import { createRouter, createWebHistory } from 'vue-router';
import Informacion from '@/modules/informacion.vue';
import Login from '@/modules/login.vue';
import Reporte from '@/modules/Reporte.vue';
import Registrar from '@/modules/Registrar.vue';
import Consultar from '@/modules/Consultar.vue';
import Cotizacion from '@/modules/Cotizacion.vue';
import ConsultarCotizaciones from '@/modules/ConsultarCotizaciones.vue';
import CalendarioCotizaciones from '@/modules/CalendarioCotizaciones.vue';
import SeguimientoEventos from '@/modules/SeguimientoEventos.vue';

const routes = [
  {
    path: '/',
    name: 'home',
    component: () => import('../App.vue')
  },
  {
    path: '/login',
    name: 'login',
    component: Login
  },
  {
    path: '/informacion',
    name: 'informacion',
    component: Informacion
  },
  {
    path: '/registrar',
    name: 'registrar',
    component: Registrar
  },
  {
    path: '/consultar',
    name: 'consultar',
    component: Consultar
  },
  {
    path: '/reporte',
    name: 'reporte',
    component: Reporte
  },
  {
    path: '/Cotizacion',
    name: 'Cotizacion',
    component: Cotizacion
  },
  {
    path: '/consultar-cotizaciones',
    name: 'consultar-cotizaciones',
    component: ConsultarCotizaciones
  },
  {
    path: '/calendario-cotizaciones',
    name: 'calendario-cotizaciones',
    component: CalendarioCotizaciones
  },
  {
    path: '/consultar-reportes',
    name: 'consultar-reportes',
    component: () => import('@/modules/ConsultarReportes.vue')
  },
  {
    path: '/crear-evento',
    name: 'crear-evento',
    component: () => import('@/modules/CrearEvento.vue')
  },{

    path:  '/seguimiento',
    name: 'Seguimiento',
    component: SeguimientoEventos
  },
  {
    path: '/alta-articulo',
    name: 'alta-articulo',
    component: () => import('@/modules/Articulos.vue')
  },
  {
    path: '/asignar-imeis',
    name: 'asignar-imeis',
    component: () => import('@/modules/AsignarImeis.vue')
  },
  {
    path: '/articulos-con-imeis',
    name: 'articulos-con-imeis',
    component: () => import('@/modules/ArticulosConImeis.vue')
  },
  {
    path: '/clientes',
    name: 'clientes',
    component: () => import('@/modules/Clientes.vue')
  },
  {
    path: '/ventas',
    name: 'ventas',
    component: () => import('@/modules/Ventas.vue')
  },
  {
    path: '/ubicaciones',
    name: 'Ubicaciones',
    component: () => import('@/modules/Ubicaciones.vue')
  },
  {
    path: '/ubicaciones/:id/imeis',
    name: 'UbicacionImeis',
    component: () => import('@/modules/UbicacionImeis.vue'),
    props: true
  },
  {
    path: '/consultar-ventas',
    name: 'consultar-ventas',
    component: () => import('@/modules/consultarVentas.vue')
  },
  {
    path: '/buscar-imei',
    component: () => import('@/modules/BuscarImei.vue')
  },
  {
    path: '/historico-notas',
    name: 'historico-notas',
    component: () => import('@/modules/HistoricoNotasVenta.vue')
  },

  {
    path: '/usuarios',
    name: 'usuarios',
    component: () => import('@/modules/Usuarios.vue')
  },
  {
    path: '/calendario-asignaciones',
    name: 'calendario-asignaciones',
    component: () => import('@/modules/CalendarioAsignaciones.vue')
  },
  {
    path: '/asignacion/:id',
    name: 'detalle-asignacion',
    component: () => import('@/modules/DetalleAsignacion.vue')
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
