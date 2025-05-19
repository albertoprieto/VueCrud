<template>
  <div class="consultar">
    <h2>Consultar IMEIs Registrados</h2>
    <DataTable :value="items" responsiveLayout="scroll">
      <Column field="imei" header="IMEI" />
      <Column field="registeredBy" header="Registrado Por" />
      <Column field="date" header="Fecha de Registro" />
      <Column field="status" header="Estado" /> <!-- Agrega esta línea -->
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { getIMEIs } from '@/services/imeiService';

const items = ref([]);

onMounted(async () => {
  items.value = await getIMEIs();
  console.log(items.value);
  
});
</script>

<style scoped>
.consultar {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}
</style>