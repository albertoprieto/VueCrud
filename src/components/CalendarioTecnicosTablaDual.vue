<template>
  <div class="vista-dual-container">
    <div class="vista-switcher">
      <Button :label="vista === 'calendario' ? 'Ver como Tabla' : 'Ver como Calendario'"
              icon="pi pi-exchange"
              class="p-button-sm"
              @click="toggleVista" />
    </div>
    <CalendarioTecnicos v-if="vista === 'calendario'" />
    <CalendarioAsignaciones v-else />
  </div>
</template>

<script setup>
import { ref } from 'vue';
import CalendarioTecnicos from '@/components/CalendarioTecnicos.vue';
import CalendarioAsignaciones from '@/modules/CalendarioAsignaciones.vue';
import Button from 'primevue/button';

const vista = ref('calendario');
function toggleVista() {
  vista.value = vista.value === 'calendario' ? 'tabla' : 'calendario';
}
</script>

<style scoped>
.vista-dual-container {
  max-width: 1100px;
  margin: 2rem auto;
}
.vista-switcher {
  display: flex;
  justify-content: flex-end;
  margin-bottom: 1.5rem;
}
</style>
