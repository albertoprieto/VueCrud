<template>
  <div class="admin-items">
    <h1>Administrar Items</h1>
    <Button label="Agregar Item" @click="openNewItemDialog" />
    <DataTable :value="items" responsiveLayout="scroll">
      <Column field="name" header="Nombre"></Column>
      <Column field="image" header="Imagen"></Column>
      <Column field="description" header="Descripción"></Column>
      <Column field="price" header="Precio"></Column>
      <Column field="urlpago" header="URL de Pago"></Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button label="Editar" @click="editItem(slotProps.data)" />
          <Button label="Eliminar" @click="deleteItem(slotProps.data)" />
        </template>
      </Column>
    </DataTable>

    <Dialog header="Agregar Item" v-model:visible="addDialogVisible" modal>
      <div class="p-field">
        <label for="name">Nombre</label>
        <InputText id="name" v-model="newItem.name" />
      </div>
      <div class="p-field">
        <label for="imagen">Imagen</label>
        <InputText id="imagen" v-model="newItem.image" />
      </div>
      <div class="p-field">
        <label for="description">Descripción</label>
        <InputText id="description" v-model="newItem.description" />
      </div>
      <div class="p-field">
        <label for="price">Precio</label>
        <InputText id="price" v-model="newItem.price" />
      </div>
      <div class="p-field">
        <label for="urlpago">URL de Pago</label>
        <InputText id="urlpago" v-model="newItem.urlpago" />
      </div>
      <Button label="Agregar" @click="addItem" />
      <Button label="Cancelar" @click="addDialogVisible = false" />
    </Dialog>

    <Dialog header="Editar Item" v-model:visible="editDialogVisible" modal>
      <div class="p-field">
        <label for="name">Nombre</label>
        <InputText id="name" v-model="selectedItem.name" />
      </div>
      <div class="p-field">
        <label for="imagen">Imagen</label>
        <InputText id="imagen" v-model="selectedItem.image" />
      </div>
      <div class="p-field">
        <label for="description">Descripción</label>
        <InputText id="description" v-model="selectedItem.description" />
      </div>
      <div class="p-field">
        <label for="price">Precio</label>
        <InputText id="price" v-model="selectedItem.price" />
      </div>
      <div class="p-field">
        <label for="urlpago">URL de Pago</label>
        <InputText id="urlpago" v-model="selectedItem.urlpago" />
      </div>
      <Button label="Actualizar" @click="updateItem" />
      <Button label="Cancelar" @click="editDialogVisible = false" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import { useItemsStore } from '@/stores/itemStore';

const itemsStore = useItemsStore();
const items = itemsStore.items;
const addDialogVisible = ref(false);
const editDialogVisible = ref(false);
const newItem = ref({ name: '', image: '' , description: '', price: '', urlpago: '' });
const selectedItem = ref(null);

const openNewItemDialog = () => {
  newItem.value = { name: '', image: '', description: '', price: '', urlpago: '' };
  addDialogVisible.value = true;
};

const addItem = () => {
  itemsStore.addItem(newItem.value);
  newItem.value = { name: '', image: '', description: '', price: '', urlpago: '' };
  addDialogVisible.value = false;
};

const editItem = (item) => {
  selectedItem.value = { ...item };
  editDialogVisible.value = true;
};

const updateItem = () => {
  itemsStore.updateItem(selectedItem.value);
  editDialogVisible.value = false;
};

const deleteItem = (item) => {
  itemsStore.deleteItem(item.id);
};

</script>

<style scoped>
.admin-items {
  text-align: center;
  margin: 20px;
}
.p-datatable {
  margin-top: 20px;
}
.p-field {
  margin-bottom: 1rem;
}
.p-button {
  margin-right: 0.5rem;
}
</style>