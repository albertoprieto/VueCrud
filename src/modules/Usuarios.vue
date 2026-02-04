<template>
  <div class="tecnicos-container">
    <h2 class="tecnicos-title">Usuarios</h2>
    <div class="tecnicos-actions">
      <Button label="Agregar Usuario" icon="pi pi-plus" @click="abrirModal" />
    </div>
    <DataTable :value="tecnicos" class="tecnicos-table" :loading="loading">
      <template #loading>
        <DataTableLoader text="Cargando usuarios..." />
      </template>
      <Column field="consecutivo" header="N" />
      <Column field="username" header="Usuario" />
      <Column field="perfil" header="Perfil" />
      <Column header="Acciones">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" class="p-button-text" @click="editarTecnico(slotProps.data)" />
          <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="eliminarTecnico(slotProps.data.id)" />
        </template>
      </Column>
      <Column v-if="esElpepe" field="ultima_sesion" header="Fecha">
        <template #body="slotProps">
          {{ formatearFecha(slotProps.data.ultima_sesion) }}
        </template>
      </Column>

    </DataTable>
    <Dialog v-model:visible="showModal" :header="editando ? 'Editar Técnico' : 'Nuevo Técnico'" :modal="true">
      <div class="form-group">
        <label>Usuario</label>
        <InputText v-model="form.username" class="w-full" />
      </div>
      <div class="form-group">
        <label>Contraseña</label>
        <InputText v-model="form.password" type="password" class="w-full" />
      </div>
      <div class="form-group">
        <label>Perfil</label>
        <Dropdown v-model="form.perfil" :options="['User', 'Admin', 'Tecnico', 'Vendedor', 'Cliente']" placeholder="Selecciona perfil" class="w-full" />
      </div>
      <div class="modal-actions">
        <Button label="Guardar" icon="pi pi-save" @click="guardarTecnico" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="showModal = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import DataTable from 'primevue/datatable';
import DataTableLoader from '@/components/DataTableLoader.vue';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import { useToast } from 'primevue/usetoast';
import { getUsuarios, addUsuario, updateUsuario, deleteUsuario } from '@/services/usuariosService';
import { useLoginStore } from '@/stores/loginStore';

const toast = useToast();
const loginStore = useLoginStore();
const esElpepe = computed(() => loginStore.user?.username === 'elpepe');

const tecnicos = ref([]);
const loading = ref(true);
const showModal = ref(false);
const editando = ref(false);
const form = ref({ id: null, username: '', password: '', perfil: '' });

const formatearFecha = (fecha) => {
  if (!fecha) return '-';
  // Agregar 'Z' para indicar que la fecha viene en UTC
  const fechaUTC = fecha.endsWith('Z') ? fecha : fecha + 'Z';
  const d = new Date(fechaUTC);
  return d.toLocaleString('es-MX', { 
    dateStyle: 'short', 
    timeStyle: 'short' 
  });
};

const cargarTecnicos = async () => {
  loading.value = true;
  tecnicos.value = await getUsuarios();
  loading.value = false;
  console.log(loginStore.user);
  
};

onMounted(cargarTecnicos);

function abrirModal() {
  form.value = { id: null, username: '', password: '', perfil: '' };
  editando.value = false;
  showModal.value = true;
}

function editarTecnico(tecnico) {
  form.value = { ...tecnico, password: '' };
  editando.value = true;
  showModal.value = true;
}

async function guardarTecnico() {
  if (!form.value.username || !form.value.perfil) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Usuario y perfil son obligatorios.', life: 4000 });
    return;
  }
  try {
    if (editando.value) {
      await updateUsuario(form.value.id, form.value);
      toast.add({ severity: 'success', summary: 'Usuario actualizado', detail: 'El usuario se actualizó correctamente.', life: 3000 });
    } else {
      await addUsuario(form.value);
      toast.add({ severity: 'success', summary: 'Usuario agregado', detail: 'El usuario se agregó correctamente.', life: 3000 });
    }
    showModal.value = false;
    await cargarTecnicos();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al guardar el usuario.', life: 4000 });
  }
}

async function eliminarTecnico(id) {
  try {
    await deleteUsuario(id);
    await cargarTecnicos();
    toast.add({ severity: 'success', summary: 'Usuario eliminado', detail: 'El usuario se eliminó correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al eliminar el usuario.', life: 4000 });
  }
}
</script>

<style scoped>
.tecnicos-container {
  /* max-width: 700px; */
  margin: 2rem auto;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
  color: var(--color-text);
}
.tecnicos-title {
  color: var(--color-title, #ff4081);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: bold;
}
.tecnicos-actions {
  margin-bottom: 1rem;
  display: flex;
  justify-content: flex-end;
}
.tecnicos-table {
  margin-bottom: 2rem;
  background: var(--color-card);
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  padding: 1.5rem;
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
</style>