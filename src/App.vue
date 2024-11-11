<template>
<login v-if="!logged" @session="session"></login>
<dashboard v-else></dashboard>
</template>

<script setup>
import { ref } from 'vue';
import login from './modules/login.vue';
import dashboard from './modules/dashboard.vue';

const logged = ref(false)
const session = (event) =>{
  console.log(event);
  logged.value= event
}
</script>
