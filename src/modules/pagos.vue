<template>
  <div class="pagos">
    <h1>Pagos</h1>
    <DataTable :value="pagos" responsiveLayout="scroll">
      <Column field="description" header="Descripción"></Column>
      <Column field="date" header="Fecha"></Column>
      <Column header="Estatus">
        <template #body="slotProps">
          <Chip :label="slotProps.data.status" :class="getStatusClass(slotProps.data.status)" />
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button v-if="slotProps.data.status === 'Pendiente de pago'" label="Pagar" @click="pagar(slotProps.data)" />
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Chip from 'primevue/chip';
import Button from 'primevue/button';
import { useRouter } from 'vue-router';
import { usePaymentsStore } from '@/stores/paymentsStore';

const paymentsStore = usePaymentsStore();
const pagos = ref([]);
const router = useRouter();

onMounted(() => {
  pagos.value = paymentsStore.getPayments();
});

const pagar = (rowData) => {
  router.push({ name: 'pago', params: { id: rowData.id } });
};

const getStatusClass = (status) => {
  switch (status) {
    case 'Pendiente de pago':
      return 'status-pendiente';
    case 'Pagado':
      return 'status-pagado';
    case 'Fallido':
      return 'status-fallido';
    default:
      return '';
  }
};
</script>

<style scoped>
.pagos {
  text-align: center;
  margin: 20px;
}
h1 {
  margin-bottom: 20px;
}
.p-datatable {
  margin-top: 20px;
}
.status-pendiente {
  background-color: #ffcc00;
  color: #fff;
}
.status-pagado {
  background-color: #33cc33;
  color: #fff;
}
.status-fallido {
  background-color: #ff3300;
  color: #fff;
}
</style>