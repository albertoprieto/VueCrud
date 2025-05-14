<template>
  <div class="consultar">
    <h2>Consultar IMEIs Registrados</h2>
    <DataTable :value="items" responsiveLayout="scroll">
      <Column field="imei" header="IMEI" />
      <Column field="registeredBy" header="Registrado Por" />
      <Column field="date" header="Fecha de Registro" />
    </DataTable>
  </div>
</template>

<script setup>
import { useItemsStore } from '@/stores/itemStore';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';

const itemsStore = useItemsStore();
const items = itemsStore.items;
</script>

<style scoped>
.consultar {
  max-width: 800px;
  margin: 0 auto;
  text-align: center;
}
</style>