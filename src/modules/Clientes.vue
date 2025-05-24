<template>
  <div>
    <h2>Clientes</h2>
    <Button label="Agregar Cliente" @click="openModal" />
    <DataTable :value="clientes">
      <Column field="nombre" header="Nombre" />
      <Column field="telefono" header="Teléfono" />
      <Column field="correo" header="Correo" />
      <Column field="direccion" header="Dirección" />
      <Column header="Acciones">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" @click="editCliente(slotProps.data)" />
          <Button icon="pi pi-trash" @click="handleDeleteCliente(slotProps.data.id)" />
        </template>
      </Column>
    </DataTable>
    <!-- Modal para agregar/editar cliente -->
    <Dialog v-model:visible="showModal" :header="form.id ? 'Editar Cliente' : 'Nuevo Cliente'" :modal="true" :closable="true">
      <div class="form-group">
        <label for="nombre">Nombre:</label>
        <InputText id="nombre" v-model="form.nombre" class="w-full" />
      </div>
      <div class="form-group">
        <label for="telefono">Teléfono:</label>
        <InputText id="telefono" v-model="form.telefono" class="w-full" />
      </div>
      <div class="form-group">
        <label for="correo">Correo:</label>
        <InputText id="correo" v-model="form.correo" class="w-full" />
      </div>
      <div class="form-group">
        <label for="direccion">Dirección:</label>
        <InputText id="direccion" v-model="form.direccion" class="w-full" />
      </div>
      <div class="modal-actions">
        <Button label="Guardar" icon="pi pi-save" @click="saveCliente" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="closeModal" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import { getClientes, addCliente, updateCliente, deleteCliente } from '@/services/clientesService';

const clientes = ref([]);
const showModal = ref(false);
const form = ref({ id: null, nombre: '', telefono: '', correo: '', direccion: '' });

const loadClientes = async () => {
  clientes.value = await getClientes();
};

onMounted(loadClientes);

const openModal = () => {
  form.value = { id: null, nombre: '', telefono: '', correo: '', direccion: '' };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveCliente = async () => {
  if (!form.value.nombre) return;
  if (form.value.id) {
    await updateCliente(form.value.id, form.value);
  } else {
    await addCliente(form.value);
  }
  showModal.value = false;
  await loadClientes();
};

const editCliente = (cliente) => {
  form.value = { ...cliente };
  showModal.value = true;
};

const handleDeleteCliente = async (id) => {
  await deleteCliente(id);
  await loadClientes();
};
</script>

<style scoped>
.form-group {
  margin-bottom: 1rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
</style>