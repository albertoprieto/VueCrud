<template>
  <Toast />
  <login v-if="!logged" @session="session"></login>
  <dashboard v-else @logout="handleLogout"></dashboard>
</template>

<script setup>
import { ref } from 'vue';
import login from './modules/login.vue';
import dashboard from './modules/dashboard.vue';

const logged = ref(false)
const session = (event) =>{
  logged.value = event
}
const handleLogout = () => {
  logged.value = false;
}
</script>
