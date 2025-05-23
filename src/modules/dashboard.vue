<template>
  <div>
    <Menubar :model="items">
      <template #item="{ item, props, hasSubmenu }">
        <router-link v-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
          <a v-ripple :href="href" v-bind="props.action" @click="navigate">
            <span :class="item.icon" />
            <span class="ml-2">{{ item.label }}</span>
          </a>
        </router-link>
        <a v-else-if="item.command" v-ripple href="#" v-bind="props.action" @click.prevent="item.command">
          <span :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
        </a>
        <a v-else v-ripple :href="item.url" :target="item.target" v-bind="props.action">
          <span :class="item.icon" />
          <span class="ml-2">{{ item.label }}</span>
          <span v-if="hasSubmenu" class="pi pi-fw pi-angle-down ml-2" />
        </a>
      </template>
    </Menubar>
    <router-view></router-view>
    <informacion v-if="isHomeRoute" />
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Menubar from 'primevue/menubar';
import { useRouter, useRoute } from 'vue-router';
import informacion from './informacion.vue';
import { useLoginStore } from '@/stores/loginStore';

const emit = defineEmits(['logout']);

const router = useRouter();
const route = useRoute();
const loginStore = useLoginStore();

const isHomeRoute = computed(() => route.path === '/dashboard');

const handleLogout = () => {
  loginStore.logout();
  router.push('/login');
  emit('logout');
};

const items = ref([
  {
    icon: 'pi pi-fw pi-home',
    route: '/dashboard'
  },
  {
    label: 'Inventario',
    icon: 'pi pi-fw pi-shopping-cart',
    items: [
      { label: 'IMEIS', route: '/registrar' },
      { label: 'Alta artículos', route: '/alta-articulo' },
      { label: 'Consultar y asignar', route: '/consultar' }
    ]
  },
  {
    label: 'Cotizaciones',
    icon: 'pi pi-fw pi-dollar',
    items: [
      { label: 'Crear', route: '/cotizacion' },
      { label: 'Consultar', route: '/consultar-cotizaciones' }
    ]
  },
  {
    label: 'Calendario',
    icon: 'pi pi-fw pi-calendar',
    route: '/calendario-cotizaciones'
  },
  {
    label: 'Seguimiento',
    icon: 'pi pi-fw pi-file',
    route:'/seguimiento'
  },
  {
    label: 'Cerrar',
    icon: 'pi pi-fw pi-sign-out',
    command: handleLogout
  }
]);
</script>