<template>
  <div class="mis-compras">
    <h1>Mis Compras</h1>
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
          <p><strong>Estatus:</strong> <Chip :label="compra.status" :class="getStatusClass(compra.status)" /></p>
        </template>
      </Card>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import Chip from 'primevue/chip';
import { usePurchasesStore } from '@/stores/purchasesStore';

const purchasesStore = usePurchasesStore();
const purchases = ref([]);

onMounted(() => {
  purchases.value = purchasesStore.getPurchases();
});

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
    default:
      return '';
  }
};
</script>

<style scoped>
.mis-compras {
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
</style>