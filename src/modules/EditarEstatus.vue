<template>
  <div class="editar-estatus">
    <h1>Editar Estatus de Compras y Pagos</h1>
    <div class="card-container">
      <Card v-for="compra in purchases" :key="compra.id" class="compra-card">
        <template #header>
          <img :src="compra.image" alt="Image" class="compra-image"/>
        </template>
        <template #title>
          <h2>{{ compra.name }}</h2>
        </template>
        <template #content>
          <p>{{ compra.description }}</p>
          <p><strong>Estatus Actual de Compra:</strong> <Chip :label="compra.status" :class="getStatusClass(compra.status)" /></p>
          <div class="p-field">
            <label for="status">Nuevo Estatus de Compra</label>
            <Dropdown id="status" v-model="compra.newStatus" :options="statusOptions" optionLabel="label" optionValue="value" placeholder="Selecciona un estatus" />
          </div>
          <p v-if="compra.payment"><strong>Estatus Actual de Pago:</strong> <Chip :label="compra.payment.status" :class="getStatusClass(compra.payment.status)" /></p>
          <div v-if="compra.payment" class="p-field">
            <label for="paymentStatus">Nuevo Estatus de Pago</label>
            <Dropdown id="paymentStatus" v-model="compra.payment.newStatus" :options="paymentStatusOptions" optionLabel="label" optionValue="value" placeholder="Selecciona un estatus" />
          </div>
        </template>
        <template #footer>
          <Button label="Actualizar Estatus" @click="updateStatus(compra)" />
        </template>
      </Card>
    </div>
    <Dialog header="Confirmación" v-model:visible="dialogVisible" modal>
      <p>Cambio de estatus realizado con éxito.</p>
      <Button label="Aceptar" @click="dialogVisible = false" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Card from 'primevue/card';
import Dropdown from 'primevue/dropdown';
import Chip from 'primevue/chip';
import Dialog from 'primevue/dialog';
import { usePurchasesStore } from '@/stores/purchasesStore';
import { usePaymentsStore } from '@/stores/paymentsStore';

const purchasesStore = usePurchasesStore();
const paymentsStore = usePaymentsStore();
const purchases = ref([]);
const dialogVisible = ref(false);

const statusOptions = [
  { label: 'Pendiente', value: 'Pendiente' },
  { label: 'En revisión', value: 'En revisión' },
  { label: 'Preparando pedido', value: 'Preparando pedido' },
  { label: 'En camino', value: 'En camino' },
  { label: 'Entregado', value: 'Entregado' }
];

const paymentStatusOptions = [
  { label: 'Pendiente de pago', value: 'Pendiente de pago' },
  { label: 'Pagado', value: 'Pagado' },
  { label: 'Fallido', value: 'Fallido' }
];

onMounted(() => {
  loadPurchases();
});

const loadPurchases = () => {
  purchases.value = purchasesStore.getPurchases().map(purchase => {
    const payment = paymentsStore.getPaymentById(purchase.id);
    return {
      ...purchase,
      newStatus: purchase.status,
      payment: payment ? { ...payment, newStatus: payment.status } : null
    };
  });
};

const updateStatus = (compra) => {
  purchasesStore.updateStatus(compra.id, compra.newStatus);
  if (compra.payment) {
    paymentsStore.updateStatus(compra.payment.id, compra.payment.newStatus);
  }
  dialogVisible.value = true;
  loadPurchases();
};

const getStatusClass = (status) => {
  switch (status) {
    case 'Pendiente':
      return 'status-pendiente';
    case 'En revisión':
      return 'status-en-revision';
    case 'Preparando pedido':
      return 'status-preparando-pedido';
    case 'En camino':
      return 'status-en-camino';
    case 'Entregado':
      return 'status-entregado';
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
.editar-estatus {
  text-align: center;
  margin-top: 20px;
}
.card-container {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 20px;
  margin-top: 20px;
}
.compra-card {
  width: 300px;
}
.compra-image {
  width: 100%;
  height: auto;
}
.p-field {
  margin-bottom: 1rem;
}
button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
.status-pendiente {
  background-color: #ffcc00;
  color: #fff;
}
.status-en-revision {
  background-color: #ff9900;
  color: #fff;
}
.status-preparando-pedido {
  background-color: #ff6600;
  color: #fff;
}
.status-en-camino {
  background-color: #3399ff;
  color: #fff;
}
.status-entregado {
  background-color: #33cc33;
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