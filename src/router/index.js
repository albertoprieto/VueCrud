import { createRouter, createWebHistory } from 'vue-router';
import Informacion from '@/modules/informacion.vue';
import Login from '@/modules/login.vue';
import Reporte from '@/modules/reporte.vue';
import Registrar from '@/modules/registrar.vue';
import Consultar from '@/modules/consultar.vue';
import Cotizacion from '@/modules/cotizacion.vue';
import ConsultarCotizaciones from '@/modules/ConsultarCotizaciones.vue';
import CalendarioCotizaciones from '@/modules/CalendarioCotizaciones.vue';

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
  }
];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
