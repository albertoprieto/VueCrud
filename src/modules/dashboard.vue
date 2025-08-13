<template>
  <div>
    <Loader v-if="loading" />
    <button class="hamburger" @click="showSidebar = true" aria-controls="main-sidebar" :aria-expanded="showSidebar">
      <span class="pi pi-bars"></span>
    </button>
    <Sidebar
      id="main-sidebar"
      v-model:visible="showSidebar"
      position="left"
      class="mobile-sidebar"
    >
      <template #container="{ closeCallback }">
        <div class="flex flex-column h-full">
          <div class="flex align-items-center justify-content-between px-4 pt-3 flex-shrink-0">
            <span class="font-bold text-xl">Menú</span>
            <button @click="closeCallback" class="p-link p-ml-auto" style="font-size: 1.5rem;">
              <span class="pi pi-times"></span>
            </button>
          </div>
          <nav class="overflow-y-auto flex-1">
            <ul class="list-none p-3 m-0">
              <template v-for="item in items" :key="item.label || item.route">
                <li v-if="item.route">
                  <router-link :to="item.route" class="drawer-link" @click="showSidebar = false">
                    <span :class="item.icon" />
                    <span class="ml-2">{{ item.label }}</span>
                    <span v-if="item.badge" class="menu-badge">{{ item.badge }}</span>
                  </router-link>
                </li>
                <li v-else-if="item.items">
                  <div class="drawer-link drawer-parent">
                    <span :class="item.icon" />
                    <span class="ml-2">{{ item.label }}</span>
                  </div>
                  <ul class="list-none pl-4">
                    <li v-for="sub in item.items" :key="sub.label">
                      <router-link :to="sub.route" class="drawer-link" @click="showSidebar = false">
                        <span :class="sub.icon" />
                        <span class="ml-2">{{ sub.label }}</span>
                        <span v-if="sub.badge" class="menu-badge">{{ sub.badge }}</span>
                      </router-link>
                    </li>
                  </ul>
                </li>
                <li v-else-if="item.command">
                  <a href="#" class="drawer-link" @click.prevent="item.command">
                    <span :class="item.icon" />
                    <span class="ml-2">{{ item.label }}</span>
                  </a>
                </li>
                <li v-else-if="item.separator">
                  <hr class="menu-separator" />
                </li>
              </template>
            </ul>
          </nav>
        </div>
      </template>
    </Sidebar>
    <!-- Menubar normal para escritorio -->
    <Menubar :model="items" class="desktop-menu">
      <template #end>
        <button class="profile-btn profile-btn-onda" @click="showProfileMenu($event)">
          <span class="profile-avatar">
            {{ (user.username || 'U').charAt(0).toUpperCase() }}
          </span>
          <span class="profile-username" style="color:var(--color-title)">{{ user.username || 'Usuario' }}</span>
        </button>
        <OverlayPanel ref="overlayRef" :dismissable="true" style="min-width:240px; background:var(--color-bg); color:var(--color-text);">
          <Card>
            <template #title>
              <div class="profile-card-title" @click="router.push('/dashboard')" style="cursor:pointer;">
                <span class="profile-avatar-lg" style="position:relative;">
                  <img v-if="user.avatarUrl" :src="user.avatarUrl" alt="avatar" class="profile-avatar-img" />
                  <span v-else class="profile-avatar-initial">{{ (user.username || 'U').charAt(0).toUpperCase() }}</span>
                  <span v-if="!user.avatarUrl" class="profile-avatar-generic">
                    <svg width="32" height="32" viewBox="0 0 32 32" fill="none"><circle cx="16" cy="16" r="16" fill="#e0e0e0"/><ellipse cx="16" cy="13" rx="7" ry="7" fill="#bdbdbd"/><ellipse cx="16" cy="26" rx="10" ry="6" fill="#bdbdbd"/></svg>
                  </span>
                </span>
                <div>
                  <div class="profile-real-username" style="color:var(--color-title)">{{ user.username || 'Usuario desconocido' }}</div>
                  <div class="profile-real-perfil" style="color:var(--color-text)">
                    <span class="pi pi-id-card mr-1" />
                    {{ user.perfil || 'Perfil desconocido' }}
                  </div>
                </div>
              </div>
            </template>
            <template #content>
              <Button label="Cerrar Sesión" icon="pi pi-sign-out" class="p-button-text mt-3 w-full" @click="handleLogout" style="color:var(--color-title)" />
            </template>
          </Card>
        </OverlayPanel>
      </template>
      <template #item="{ item, props, hasSubmenu }">
        <template v-if="item.separator">
          <hr class="menu-separator" />
        </template>
        <template v-else-if="item.locked">
          <span v-bind="props.action" class="menu-locked">
            <span :class="item.icon" />
            <span class="ml-2 menu-locked-label">{{ item.label }}</span>
          </span>
        </template>
        <router-link v-else-if="item.route" v-slot="{ href, navigate }" :to="item.route" custom>
          <a v-ripple :href="href" v-bind="props.action" @click="navigate">
            <span :class="item.icon" />
            <span class="ml-2">{{ item.label }}</span>
            <span v-if="item.badge" class="menu-badge">{{ item.badge }}</span>
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
import { ref, computed, watch, nextTick, onMounted } from 'vue';
import Menubar from 'primevue/menubar';
import TieredMenu from 'primevue/tieredmenu';
import Sidebar from 'primevue/sidebar';
import OverlayPanel from 'primevue/overlaypanel';
import Card from 'primevue/card';
import { useRouter, useRoute } from 'vue-router';
import informacion from './informacion.vue';
import { useLoginStore } from '@/stores/loginStore';
import Loader from '@/components/Loader.vue';
import { getCotizacionesPendientes } from '@/services/quotationService';
import { getReportesNuevos } from '@/services/reportesService';

const emit = defineEmits(['logout']);

const router = useRouter();
const route = useRoute();
const loginStore = useLoginStore();

const showSidebar = ref(false);
const overlayRef = ref();
const user = computed(() => loginStore.user || {});

const isHomeRoute = computed(() => route.path === '/dashboard');

const handleLogout = () => {
  loginStore.logout();
  router.push('/login');
  emit('logout');
};

// Datos reactivos para los badges
const cotizacionesPendientes = ref(0);
const reportesNuevos = ref(0);


// Opcional: recargar cuando cambie la ruta o cada cierto tiempo

const items = computed(() => {
  if (user.value.perfil === 'Tecnico') {
    return [
      {
        label: 'Técnicos',
        icon: 'pi pi-fw pi-user-cog',
        items: [
          { label: 'Asignaciones a Técnicos', route: '/calendario-tecnicos', icon: 'pi pi-fw pi-calendar-plus' },
          { label: 'Reportes de Servicio', route: '/consultar-reportes', icon: 'pi pi-fw pi-file-edit', badge: reportesNuevos.value || undefined },
        ]
      },
      {
        label: 'Cerrar Sesión',
        icon: 'pi pi-fw pi-sign-out',
        command: handleLogout
      }
    ];
  }

  return [
    {
      label: 'Inicio',
      icon: 'pi pi-fw pi-home',
      route: '/dashboard'
    },
    {
      label: 'Inventario',
      icon: 'pi pi-fw pi-shopping-cart',
      items: [
        { label: 'Alta artículos', route: '/alta-articulo', icon: 'pi pi-fw pi-plus-circle' },
        { label: 'Asignar IMEIs', route: '/asignar-imeis', icon: 'pi pi-fw pi-barcode' },
        {
          label: 'Transferir IMEIs',
          route: '/transferir-imeis',
          icon: 'pi pi-fw pi-share-alt'
        },
        { label: 'Buscar IMEI', route: '/buscar-imei', icon: 'pi pi-fw pi-search' },
        { label: 'Ubicaciones', route: '/ubicaciones', icon: 'pi pi-fw pi-map-marker' },
      ]
    },
    {
      label: 'Ventas',
      icon: 'pi pi-fw pi-briefcase',
      items: [
        { label: 'Clientes', route: '/clientes', icon: 'pi pi-fw pi-users' },
        { label: 'Cotizador',icon: 'pi pi-fw pi-file-edit',route: '/cotizador'},
        { label: 'Consultar Cotizaciones', route: '/consultar-cotizaciones', icon: 'pi pi-fw pi-list', badge: cotizacionesPendientes.value || undefined },
        { label: 'Crear Orden de Servicio', route: '/ventas', icon: 'pi pi-fw pi-plus', badge: cotizacionesPendientes.value || undefined },
        { label: 'Consultar Orden de Servicio', route: '/historico-notas', icon: 'pi pi-fw pi-file' }
      ]
    },
    {
      label: 'Dinero',
      icon: 'pi pi-fw pi-wallet',
      route: '/dinero'
    },
    {
      label: 'Usuarios',
      icon: 'pi pi-fw pi-users',
      route: '/usuarios'
    },
    {
      label: 'Técnicos',
      icon: 'pi pi-fw pi-user-cog',
      items: [
        { label: 'Asignaciones a Técnicos', route: '/calendario-tecnicos', icon: 'pi pi-fw pi-calendar-plus' },
        { label: 'Reportes de Servicio', route: '/consultar-reportes', icon: 'pi pi-fw pi-file-edit', badge: reportesNuevos.value || undefined },
      ]
    },
    {
      label: 'Cerrar Sesión',
      icon: 'pi pi-fw pi-sign-out',
      command: handleLogout
    }
  ];
});

const loading = ref(false);

watch(
  () => route.path,
  async () => {
    loading.value = true;
    await nextTick();
    loading.value = false;
  }
);

function showProfileMenu(event) {
  overlayRef.value.toggle(event);
}
</script>

<style scoped>
.drawer-link {
  display: flex;
  align-items: center;
  padding: 0.75rem 1rem;
  border-radius: 0.5rem;
  color: var(--color-text);
  text-decoration: none;
  transition: background 0.2s;
  font-size: 1rem;
}
.drawer-link:hover {
  background: var(--color-card);
}
.drawer-parent {
  font-weight: bold;
  margin-top: 1rem;
}
.menu-badge {
  background: var(--color-title);
  color: var(--color-bg);
  border-radius: 1rem;
  padding: 0 0.5rem;
  font-size: 0.8rem;
  margin-left: 0.5rem;
  vertical-align: middle;
}
.menu-separator {
  border: none;
  border-top: 1px solid var(--color-border);
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
  color: var(--color-border);
}
.hamburger {
  display: none;
  background: none;
  border: none;
  font-size: 2rem;
  margin: 1rem;
}
.mobile-sidebar {
  width: 100vw !important;
  max-width: 320px;
}
.mobile-menu {
  width: 100%;
  min-width: 220px;
}
.profile-btn {
  background: none;
  border: none;
  cursor: pointer;
  margin-left: 1rem;
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.2rem 0.7rem 0.2rem 0.2rem;
  border-radius: 2rem;
  transition: background 0.2s, box-shadow 0.2s;
}
.profile-btn-onda {
  background: var(--color-card, #f7f7fa);
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  border: 1px solid var(--color-border, #e0e0e0);
  color: var(--color-text, #222);
  transition: background 0.2s, color 0.2s, box-shadow 0.2s;
}
.profile-btn:hover, .profile-btn-onda:hover {
  background: var(--color-primary, var(--color-title, #1976d2));
  color: var(--color-on-primary, var(--color-bg, #fff));
  box-shadow: 0 4px 16px rgba(0,0,0,0.12);
}
.profile-avatar {
  background: var(--color-primary, var(--color-title, #1976d2));
  color: var(--color-on-primary, var(--color-bg, #fff));
  border-radius: 50%;
  width: 2rem;
  height: 2rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.1rem;
  box-shadow: 0 1px 4px rgba(0,0,0,0.10);
  transition: background 0.2s, color 0.2s;
}
.profile-avatar-lg {
  background: var(--color-primary, var(--color-title, #1976d2));
  color: var(--color-on-primary, var(--color-bg, #fff));
  border-radius: 50%;
  width: 3rem;
  height: 3rem;
  display: flex;
  align-items: center;
  justify-content: center;
  font-weight: bold;
  font-size: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  transition: background 0.2s, color 0.2s;
}
.profile-real-username {
  font-size: 1.1rem;
  font-weight: bold;
  color: var(--color-primary, var(--color-title, #1976d2));
}
.profile-real-perfil {
  font-size: 0.95rem;
  color: var(--color-text);
  display: flex;
  align-items: center;
  gap: 0.3rem;
  margin-top: 0.1rem;
}
@media (max-width: 768px) {
  .desktop-menu {
    display: none;
  }
  .hamburger {
    display: block;
  }
}
@media (min-width: 769px) {
  .hamburger {
    display: none;
  }
}
</style>