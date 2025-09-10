<template>
  <div class="ubicaciones">
    <h2>Ubicaciones (Bodegas)</h2>
    <Button label="Agregar Ubicación" icon="pi pi-plus" @click="showModal = true" />
    <DataTable :value="ubicaciones" :loading="loading">
      <Column field="nombre" header="Nombre" />
      <Column field="encargado" header="Encargado" />
      <Column field="telefonos" header="Teléfonos">
        <template #body="slotProps">
          <span v-if="slotProps.data.telefonos && slotProps.data.telefonos.length">
            {{ slotProps.data.telefonos.join(', ') }}
          </span>
          <span v-else>-</span>
        </template>
      </Column>
      <!-- <Column field="correo" header="Correo" /> -->
      <!-- <Column field="direccion" header="Dirección" />
      <Column field="capacidad_maxima" header="Capacidad Máxima" />
      <Column field="estado" header="Estado">
        <template #body="slotProps">
          <span :class="['estado-chip', slotProps.data.estado]">
            {{ slotProps.data.estado === 'inactiva' ? 'Inactiva' : 'Activa' }}
          </span>
        </template>
      </Column> -->
      <Column header="IMEIs asignados">
        <template #body="slotProps">
          <span
            :class="{
              'alerta-capacidad': slotProps.data.capacidad_maxima && (imeisPorUbicacion[slotProps.data.id] || 0) >= slotProps.data.capacidad_maxima,
              'alerta-inactiva': slotProps.data.estado === 'inactiva'
            }"
          >
            {{ imeisPorUbicacion[slotProps.data.id] || 0 }}
            <span v-if="slotProps.data.capacidad_maxima">
              / {{ slotProps.data.capacidad_maxima }}
            </span>
            <span v-if="slotProps.data.capacidad_maxima && (imeisPorUbicacion[slotProps.data.id] || 0) >= slotProps.data.capacidad_maxima" class="alerta-text">
              (¡Llena!)
            </span>
            <span v-if="slotProps.data.estado === 'inactiva'" class="alerta-text">
              (Inactiva)
            </span>
          </span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" class="p-button-text" @click="editUbicacion(slotProps.data)" />
          <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDelete(slotProps.data.id)" />
          <Button label="Ver IMEIs" class="p-button-text p-button-info" @click="verImeis(slotProps.data)" />
        </template>
      </Column>
    </DataTable>
    <Dialog v-model:visible="showModal" :header="editando ? 'Editar Ubicación' : 'Nueva Ubicación'" :modal="true" class="ubicaciones-dialog">
      <div>
        <InputText v-model="form.nombre" placeholder="Nombre" class="mb-2 w-full" />
        <InputText v-model="form.encargado" placeholder="Encargado" class="mb-2 w-full" />
        <div class="mb-2">
          <label>Teléfonos:</label>
          <div v-for="(tel, idx) in form.telefonos" :key="idx" class="input-row">
            <InputText v-model="form.telefonos[idx]" class="w-full" />
            <Button icon="pi pi-minus" class="p-button-text p-button-danger" @click="removeTelefono(idx)" v-if="form.telefonos.length > 1" />
          </div>
          <Button icon="pi pi-plus" class="p-button-text" @click="addTelefono" />
        </div>
        <InputText v-model="form.correo" placeholder="Correo" class="mb-2 w-full" />
        <InputText v-model="form.direccion" placeholder="Dirección" class="mb-2 w-full" />
        <!-- <InputText v-model="form.capacidad_maxima" type="number" min="1" placeholder="Capacidad máxima" class="mb-2 w-full" />
        <Dropdown v-model="form.estado" :options="estados" optionLabel="value" placeholder="Estado" class="mb-2 w-full" />
        <Textarea v-model="form.descripcion" placeholder="Descripción" class="w-full" /> -->
      </div>
      <template #footer>
        <Button label="Cancelar" @click="showModal = false" />
        <Button label="Guardar" @click="guardarUbicacion" />
      </template>
    </Dialog>
    <Dialog v-model:visible="showConfirmDelete" header="Confirmar" :modal="true" class="ubicaciones-dialog">
      <span>¿Eliminar esta ubicación?</span>
      <template #footer>
        <Button label="Cancelar" @click="showConfirmDelete = false" />
        <Button label="Eliminar" class="p-button-danger" @click="eliminarUbicacion" />
      </template>
    </Dialog>
    <Dialog v-model:visible="showResultDialog" header="Resultado" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ resultMessage }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="showResultDialog = false" class="mt-3" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getUbicaciones, addUbicacion, updateUbicacion, deleteUbicacion } from '@/services/ubicacionesService';
import { getIMEIs } from '@/services/imeiService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Dropdown from 'primevue/dropdown';

const router = useRouter();
const ubicaciones = ref([]);
const loading = ref(true);
const showModal = ref(false);
const showConfirmDelete = ref(false);
const showResultDialog = ref(false);
const resultMessage = ref('');
const imeisPorUbicacion = ref({});
const form = ref({
  id: null,
  nombre: '',
  encargado: '',
  telefonos: [''],
  correo: '',
  direccion: '',
  capacidad_maxima: '',
  estado: 'activa',
  descripcion: ''
});
const editando = ref(false);
const estados = [
  { label: 'Activa', value: 'activa' },
  { label: 'Inactiva', value: 'inactiva' }
];

const guardarUbicacion = async () => {
  form.value.telefonos = form.value.telefonos.filter(t => t);
  if (form.value.capacidad_maxima) {
    form.value.capacidad_maxima = Number(form.value.capacidad_maxima);
  }
  try {
    if (editando.value) {
      await updateUbicacion(form.value.id, form.value);
      resultMessage.value = 'Ubicación actualizada correctamente.';
    } else {
      await addUbicacion(form.value);
      resultMessage.value = 'Ubicación agregada correctamente.';
    }
    showResultDialog.value = true;
    showModal.value = false;
    await cargarUbicaciones();
  } catch (e) {
    resultMessage.value = 'Error al guardar la ubicación: ' + (e?.response?.data?.message || e.message || e);
    showResultDialog.value = true;
  }
  form.value = {
    id: null,
    nombre: '',
    encargado: '',
    telefonos: [''],
    correo: '',
    direccion: '',
    capacidad_maxima: '',
    estado: 'activa',
    descripcion: ''
  };
  editando.value = false;
};

const addTelefono = () => form.value.telefonos.push('');
const removeTelefono = (idx) => form.value.telefonos.splice(idx, 1);

const cargarUbicaciones = async () => {
  loading.value = true;
  ubicaciones.value = await getUbicaciones();
  //
  // Trae todos los IMEIs y cuenta por ubicacion_id
  const imeis = await getIMEIs();
  const conteo = {};
  imeis.forEach(i => {
    if (i.ubicacion_id != null) {
      conteo[i.ubicacion_id] = (conteo[i.ubicacion_id] || 0) + 1;
    }
  });
  imeisPorUbicacion.value = conteo;
  loading.value = false;
};

const editUbicacion = (ubicacion) => {
  form.value = {
    ...ubicacion,
    telefonos: ubicacion.telefonos?.length ? [...ubicacion.telefonos] : ['']
  };
  showModal.value = true;
  editando.value = true;
};

const confirmDelete = (id) => {
  ubicacionToDelete.value = id;
  showConfirmDelete.value = true;
};

const eliminarUbicacion = async () => {
  await deleteUbicacion(ubicacionToDelete.value);
  showConfirmDelete.value = false;
  showResultDialog.value = true;
  resultMessage.value = 'Ubicación eliminada correctamente.';
  await cargarUbicaciones();
};

const verImeis = (ubicacion) => {
  router.push({ name: 'UbicacionImeis', params: { id: ubicacion.id } });
};

onMounted(cargarUbicaciones);
</script>

<style scoped>
.ubicaciones {
  /* max-width: 900px; */
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
}
h2 {
  margin-bottom: 2rem;
  color: var(--color-title);
}
.p-button {
  margin-right: 0.5rem;
}
.p-button:last-child {
  margin-right: 0;
}
.ubicaciones-dialog :deep(.p-dialog-content) {
  background: var(--color-card);
  padding: 1.5rem 1rem;
  border-radius: 12px;
}
.ubicaciones-dialog :deep(.p-dialog-header) {
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
.input-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.5rem;
}
.estado-chip {
  padding: 0.2em 0.7em;
  border-radius: 8px;
  font-size: 0.95em;
  font-weight: bold;
  background: #e0e0e0;
  color: #333;
}
.estado-chip.activa {
  background: #c8e6c9;
  color: #388e3c;
}
.estado-chip.inactiva {
  background: #ffcdd2;
  color: #c62828;
}
.alerta-capacidad {
  color: #d32f2f;
  font-weight: bold;
}
.alerta-inactiva {
  color: #c62828;
  font-weight: bold;
}
.alerta-text {
  font-size: 0.85em;
  margin-left: 0.5em;
}
</style>