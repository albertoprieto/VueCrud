<template>
  <Toast />
  <login v-if="!logged" @session="session"></login>
  <dashboard v-else @logout="handleLogout"></dashboard>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import login from './modules/login.vue';
import dashboard from './modules/dashboard.vue';
import { useLoginStore } from '@/stores/loginStore';

const loginStore = useLoginStore();
const logged = ref(false);

// Restaurar sesión al cargar la app
onMounted(() => {
  if (loginStore.restoreSession()) {
    logged.value = true;
  }
});

const session = (event) => {
  logged.value = event;
};

const handleLogout = () => {
  loginStore.logout();
  logged.value = false;
};
</script>
