<template>
  <div class="clientes-container">
    <h2 class="clientes-title">Clientes</h2>
    <div class="clientes-card">
      <Button label="Agregar Cliente" icon="pi pi-plus" @click="openModal" class="mb-2" />
      <DataTable :value="clientes">
        <Column field="nombre" header="Nombre" />
        <Column field="telefono" header="Teléfonos">
          <template #body="slotProps">
            <ul>
              <li v-for="(tel, idx) in slotProps.data.telefonos" :key="idx">{{ tel }}</li>
            </ul>
          </template>
        </Column>
        <Column field="correo" header="Correo" />
        <Column field="direccion" header="Dirección" />
        <Column header="Usuarios">
          <template #body="slotProps">
            <ul>
              <li v-for="(u, idx) in slotProps.data.usuarios" :key="idx">{{ u }}</li>
            </ul>
          </template>
        </Column>
        <Column header="Plataformas">
          <template #body="slotProps">
            <ul>
              <li v-for="(p, idx) in slotProps.data.plataformas" :key="idx">{{ p }}</li>
            </ul>
          </template>
        </Column>
        <Column header="Acciones">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" class="p-button-text" @click="editCliente(slotProps.data)" />
            <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="handleDeleteCliente(slotProps.data.id)" />
          </template>
        </Column>
      </DataTable>
    </div>
    <!-- Modal para agregar/editar cliente -->
    <Dialog v-model:visible="showModal" :header="form.id ? 'Editar Cliente' : 'Nuevo Cliente'" :modal="true" :closable="true" class="clientes-dialog">
      <div class="form-group">
        <label for="nombre">Nombre:</label>
        <InputText id="nombre" v-model="form.nombre" class="w-full" />
      </div>
      <div class="form-group">
        <label>Teléfonos:</label>
        <div v-for="(tel, idx) in form.telefonos" :key="idx" style="display:flex;gap:0.5rem;align-items:center;">
          <InputText v-model="form.telefonos[idx]" class="w-full" />
          <Button icon="pi pi-minus" class="p-button-text p-button-danger" @click="removeTelefono(idx)" v-if="form.telefonos.length > 1" />
        </div>
        <Button icon="pi pi-plus" class="p-button-text" @click="addTelefono" />
      </div>
      <div class="form-group">
        <label for="correo">Correo:</label>
        <InputText id="correo" v-model="form.correo" class="w-full" />
      </div>
      <div class="form-group">
        <label for="direccion">Dirección:</label>
        <InputText id="direccion" v-model="form.direccion" class="w-full" />
      </div>
      <div class="form-group">
        <label>Usuarios:</label>
        <div v-for="(u, idx) in form.usuarios" :key="idx" style="display:flex;gap:0.5rem;align-items:center;">
          <InputText v-model="form.usuarios[idx]" class="w-full" />
          <Button icon="pi pi-minus" class="p-button-text p-button-danger" @click="removeUsuario(idx)" v-if="form.usuarios.length > 1" />
        </div>
        <Button icon="pi pi-plus" class="p-button-text" @click="addUsuario" />
      </div>
      <div class="form-group">
        <label>Plataformas:</label>
        <div v-for="(p, idx) in form.plataformas" :key="idx" style="display:flex;gap:0.5rem;align-items:center;">
          <InputText v-model="form.plataformas[idx]" class="w-full" />
          <Button icon="pi pi-minus" class="p-button-text p-button-danger" @click="removePlataforma(idx)" v-if="form.plataformas.length > 1" />
        </div>
        <Button icon="pi pi-plus" class="p-button-text" @click="addPlataforma" />
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
const form = ref({
  id: null,
  nombre: '',
  telefonos: [''],
  correo: '',
  direccion: '',
  usuarios: [''],
  plataformas: ['']
});

const loadClientes = async () => {
  clientes.value = await getClientes();
};

onMounted(loadClientes);

const openModal = () => {
  form.value = {
    id: null,
    nombre: '',
    telefonos: [''],
    correo: '',
    direccion: '',
    usuarios: [''],
    plataformas: ['']
  };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveCliente = async () => {
  if (!form.value.nombre) return;
  // Limpia arrays vacíos
  form.value.telefonos = form.value.telefonos.filter(t => t);
  form.value.usuarios = form.value.usuarios.filter(u => u);
  form.value.plataformas = form.value.plataformas.filter(p => p);
  if (form.value.id) {
    await updateCliente(form.value.id, form.value);
  } else {
    await addCliente(form.value);
  }
  showModal.value = false;
  await loadClientes();
};

const editCliente = (cliente) => {
  form.value = {
    id: cliente.id,
    nombre: cliente.nombre,
    telefonos: cliente.telefonos?.length ? [...cliente.telefonos] : [''],
    correo: cliente.correo,
    direccion: cliente.direccion,
    usuarios: cliente.usuarios?.length ? [...cliente.usuarios] : [''],
    plataformas: cliente.plataformas?.length ? [...cliente.plataformas] : ['']
  };
  showModal.value = true;
};

const handleDeleteCliente = async (id) => {
  await deleteCliente(id);
  await loadClientes();
};

const addTelefono = () => form.value.telefonos.push('');
const removeTelefono = (idx) => form.value.telefonos.splice(idx, 1);
const addUsuario = () => form.value.usuarios.push('');
const removeUsuario = (idx) => form.value.usuarios.splice(idx, 1);
const addPlataforma = () => form.value.plataformas.push('');
const removePlataforma = (idx) => form.value.plataformas.splice(idx, 1);
</script>

<style scoped>
.clientes-container {
  max-width: 900px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
}
.clientes-title {
  margin-bottom: 2rem;
  color: var(--color-title);
  text-align: center;
}
.clientes-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.form-group {
  margin-bottom: 1rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
.clientes-dialog :deep(.p-dialog-content) {
  background: var(--color-card);
  padding: 1.5rem 1rem;
  border-radius: 12px;
}
.clientes-dialog :deep(.p-dialog-header) {
  background: var(--color-bg);
  color: var(--color-title);
  border-bottom: 1px solid #e0e0e0;
  border-radius: 12px 12px 0 0;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 1rem 1.5rem;
}
.mb-2 {
  margin-bottom: 1rem;
}
.w-full {
  width: 100%;
}
</style>