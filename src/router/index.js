import { createRouter, createWebHistory } from 'vue-router';

import Adquirir from '@/modules/adquirir.vue';
import Adquiridos from '@/modules/adquiridos.vue';
import Pagos from '@/modules/pagos.vue';
import Informacion from '@/modules/informacion.vue';
import Login from '@/modules/login.vue';
import Envio from '@/modules/Envios.vue';
import Servicios from '@/modules/Servicios.vue';
import ServicioDetalle from '@/modules/ServicioDetalle.vue';
import Agregar from '@/modules/AdminItems.vue';
import EditarEstatus from '@/modules/EditarEstatus.vue';
import MisCompras from '@/modules/MisCompras.vue';
import Pago from '@/modules/Pago.vue';


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
    path: '/about',
    name: 'about',
    component: () => import('../views/AboutView.vue')
  },
  {
    path: '/adquirir',
    name: 'adquirir',
    component: Adquirir
  },
  {
    path: '/agregar',
    name: 'agregar',
    component: Agregar
  },
  {
    path: '/adquiridos',
    name: 'adquiridos',
    component: Adquiridos
  },
  { path: '/mis-compras', component: MisCompras },

  { path: '/editar-estatus/', component: EditarEstatus },
  {
    path: '/pagos',
    name: 'pagos',
    component: Pagos
  },
  { path: '/pago/:id', name: 'pago', component: Pago },

  {
    path: '/informacion',
    name: 'informacion',
    component: Informacion
  }
  ,
  {
    path: '/envios',
    name: 'envios',
    component: Envio
  },
  { path: '/servicios', component: Servicios },
  { path: '/servicio/:id', component: ServicioDetalle, props: true }


];

const router = createRouter({
  history: createWebHistory(),
  routes
});

export default router;
