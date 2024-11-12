<template>
  <div class="adquirir">
    <h1>Agregar a Carrito</h1>
    <div class="card-container">
      <Card v-for="item in items" :key="item.id" class="item-card">
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
          <Button label="Agregar" @click="adquirirItem(item)" />
        </template>
      </Card>
    </div>
    <Dialog header="Éxito" v-model:visible="dialogVisible" modal>
      <p>{{ dialogMessage }}</p>
      <Button label="Aceptar" @click="dialogVisible = false" />
      <Button severity="success" label="Ir a carrito" @click="pagar(event)" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Card from 'primevue/card';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useRouter } from 'vue-router';
import { useItemsStore } from '@/stores/itemStore';
import { useAcquiredStore } from '@/stores/acquiredStore';

const itemsStore = useItemsStore();
const acquiredStore = useAcquiredStore();
const items = itemsStore.items;
const dialogVisible = ref(false);
const dialogMessage = ref('');
const router = useRouter();

onMounted(() => {
  console.log('Componente Adquirir montado');
});

const adquirirItem = (item) => {
  const itemExists = acquiredStore.getItems().some(acquiredItem => acquiredItem.id === item.id);
  if (itemExists) {
    dialogMessage.value = 'El artículo ya está en tu carrito';
  } else {
    acquiredStore.addItem(item);
    dialogMessage.value = 'Item agregado con éxito';
  }
  dialogVisible.value = true;
};

const pagar = (event) => {
  console.log('Proceso de pago iniciado', event);
  router.push('/adquiridos');
};
</script>

<style scoped>
.adquirir {
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