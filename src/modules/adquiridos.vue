<template>
  <div class="adquiridos">
    <h1>Carrito de Compras</h1>
    <div class="card-container">
      <Card v-for="item in acquiredItems" :key="item.id" class="item-card">
        <template #header>
          <img :src="item.image" alt="Image" class="item-image"/>
        </template>
        <template #title>
          <h2>{{ item.name }}</h2>
        </template>
        <template #content>
          <p>{{ item.description }}</p>
          <p><strong>Precio:</strong> {{ item.price }}</p>
        </template>
        <template #footer>
          <Button label="Eliminar" @click="confirmEliminar(item)" />
          <Button label="Pagar" @click="confirmPagar(item)" />
        </template>
      </Card>
    </div>
    <Dialog header="Confirmar Eliminación" v-model:visible="dialogEliminarVisible" modal>
      <p>¿Estás seguro de que deseas eliminar este ítem?</p>
      <Button severity="danger" label="Sí" @click="eliminarItem" />
      <Button label="No" @click="dialogEliminarVisible = false" />
    </Dialog>
    <Dialog header="Confirmar Pago" v-model:visible="dialogPagarVisible" modal>
      <p>¿Estás seguro de que deseas pagar por este ítem?</p>
      <Button severity="info" label="Sí" @click="pagarItem" />
      <Button label="No" @click="dialogPagarVisible = false" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useRouter } from 'vue-router';
import { useAcquiredStore } from '@/stores/acquiredStore';
import { usePurchasesStore } from '@/stores/purchasesStore';
import { usePaymentsStore } from '@/stores/paymentsStore';

const router = useRouter();
const acquiredStore = useAcquiredStore();
const purchasesStore = usePurchasesStore();
const paymentsStore = usePaymentsStore();
const acquiredItems = acquiredStore.getItems();
const dialogEliminarVisible = ref(false);
const dialogPagarVisible = ref(false);
const selectedItem = ref(null);

const confirmEliminar = (item) => {
  selectedItem.value = item;
  dialogEliminarVisible.value = true;
};

const eliminarItem = () => {
  acquiredStore.removeItem(selectedItem.value.id);
  dialogEliminarVisible.value = false;
};

const confirmPagar = (item) => {
  selectedItem.value = item;
  dialogPagarVisible.value = true;
};

const pagarItem = () => {
  purchasesStore.addPurchase({ ...selectedItem.value, status: 'En revisión' });
  paymentsStore.addPayment({ itemId: selectedItem.value.id, image: selectedItem.value.image, description: selectedItem.value.description, amount: selectedItem.value.price, status: 'Pendiente de pago', mercadoPagoUrl: selectedItem.value.mercadoPagoUrl || 'https://mpago.la/2iNHic4' });
  acquiredStore.removeItem(selectedItem.value.id);
  dialogPagarVisible.value = false;
  router.push('/pagos');
};
</script>

<style scoped>
.adquiridos {
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
.item-card {
  width: 300px;
}
.item-image {
  width: 100%;
  height: auto;
}
button {
  padding: 10px 20px;
  font-size: 16px;
  cursor: pointer;
}
</style>