<template>
  <div class="ubicaciones">
    <h2>Ubicaciones (Bodegas)</h2>
    <Button label="Agregar Ubicación" icon="pi pi-plus" @click="showModal = true" />
    <DataTable :value="ubicaciones" :loading="loading">
      <Column field="nombre" header="Nombre" />
      <Column field="descripcion" header="Descripción" />
      <Column header="IMEIs asignados">
        <template #body="slotProps">
          {{ imeisPorUbicacion[slotProps.data.id] || 0 }}
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
    <Dialog v-model:visible="showModal" :header="editando ? 'Editar Ubicación' : 'Nueva Ubicación'" :modal="true">
      <div>
        <InputText v-model="form.nombre" placeholder="Nombre" class="mb-2 w-full" />
        <Textarea v-model="form.descripcion" placeholder="Descripción" class="w-full" />
      </div>
      <template #footer>
        <Button label="Cancelar" @click="showModal = false" />
        <Button label="Guardar" @click="guardarUbicacion" />
      </template>
    </Dialog>
    <Dialog v-model:visible="showConfirmDelete" header="Confirmar" :modal="true">
      <span>¿Eliminar esta ubicación?</span>
      <template #footer>
        <Button label="Cancelar" @click="showConfirmDelete = false" />
        <Button label="Eliminar" class="p-button-danger" @click="eliminarUbicacion" />
      </template>
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

const router = useRouter();
const ubicaciones = ref([]);
const loading = ref(true);
const showModal = ref(false);
const showConfirmDelete = ref(false);
const editando = ref(false);
const form = ref({ id: null, nombre: '', descripcion: '' });
const ubicacionToDelete = ref(null);
const imeisPorUbicacion = ref({});

const cargarUbicaciones = async () => {
  loading.value = true;
  ubicaciones.value = await getUbicaciones();
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

const guardarUbicacion = async () => {
  if (editando.value) {
    await updateUbicacion(form.value.id, form.value);
  } else {
    await addUbicacion(form.value);
  }
  showModal.value = false;
  await cargarUbicaciones();
  form.value = { id: null, nombre: '', descripcion: '' };
  editando.value = false;
};

const editUbicacion = (ubicacion) => {
  form.value = { ...ubicacion };
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
  await cargarUbicaciones();
};

const verImeis = (ubicacion) => {
  router.push({ name: 'UbicacionImeis', params: { id: ubicacion.id } });
};

onMounted(cargarUbicaciones);
</script>