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

const route = useRoute();

const isHomeRoute = computed(() => route.path === '/dashboard');

const items = ref([
  {
    label: 'Inicio',
    icon: 'pi pi-fw pi-home',
    route: '/dashboard'
  }
]);
</script>