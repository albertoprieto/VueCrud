<template>
  <div>
    <Menubar :model="items">
      <template #item="{ item, props, hasSubmenu }">
        <template v-if="item.separator">
          <hr class="menu-separator" />
        </template>
        <template v-else-if="item.locked">
          <span
            v-bind="props.action"
            class="menu-locked"
          >
            <span :class="item.icon" />
            <span class="ml-2 menu-locked-label">{{ item.label }}</span>
          </span>
        </template>
        <router-link v-else-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
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
      { label: 'Alta artículos', route: '/alta-articulo' },
      { label: 'Asignar IMEIs', route: '/asignar-imeis' },
      { label: 'Ubicaciones', route: '/ubicaciones' },
      { label: 'Historico', route: '/articulos-con-imeis' },
    ]
  },
  {
    label: 'Ventas',
    icon: 'pi pi-fw pi-briefcase',
    items: [
      { label: 'Clientes', route: '/clientes' },
      { label: 'Notas de Venta', route: '/ventas' },
      { label: 'Consultar Ventas', route: '/consultar-ventas' }
    ]
  },
  // {
  //   label: 'Cotizaciones',
  //   icon: 'pi pi-fw pi-dollar',
  //   items: [
  //     { label: 'Crear', route: '/cotizacion' },
  //     { label: 'Consultar', route: '/consultar-cotizaciones' }
  //   ],
  //   locked: true // campo personalizado para el slot
  // },
  // {
  //   label: 'Calendario',
  //   icon: 'pi pi-fw pi-calendar',
  //   route: '/calendario-cotizaciones',
  //   locked: true // campo personalizado para el slot
  // },
  // {
  //   label: 'Seguimiento',
  //   icon: 'pi pi-fw pi-file',
  //   route:'/seguimiento',
  //   locked: true // campo personalizado para el slot
  // },

  {
    label: 'Cerrar',
    icon: 'pi pi-fw pi-sign-out',
    command: handleLogout
  }
]);
</script>

<style scoped>
.menu-separator {
  border: none;
  border-top: 1px solid var(--color-border, #ccc);
  margin: 0.5rem 0;
}
.menu-locked {
  display: flex;
  align-items: center;
  padding: 0.5rem 1rem;
  cursor: not-allowed;
}
.menu-locked-label {
  text-decoration: line-through;
  /* Cambia color según tema */
  color: var(--color-text-locked);
}
:root {
  --color-text-locked: #222;
}
body.dark,
html.dark {
  --color-text-locked: #eee;
}
</style>