<template>
  <div class="asignar-imeis-container">
    <h2>Asignar IMEIs a Artículo</h2>
    <div class="form-card">
      <div class="form-group">
        <label for="articulo">
          Artículo <span class="required-tooltip" title="Obligatorio">*</span>
        </label>
        <Dropdown
          id="articulo"
          v-model="selectedArticulo"
          :options="articulosFiltrados"
          optionLabel="sku"
          placeholder="Selecciona artículo"
          class="w-full"
        />
      </div>
      <div class="form-group">
        <label for="ubicacionDestino">Ubicación destino</label>
        <Dropdown
          id="ubicacionDestino"
          v-model="ubicacionDestino"
          :options="ubicaciones"
          optionLabel="nombre"
          placeholder="Selecciona ubicación"
          class="w-full"
        />
      </div>
      <div class="form-group">
        <label for="nuevoImei">IMEI:</label>
        <InputText
          id="nuevoImei"
          v-model="nuevoImei"
          placeholder="Escanea o escribe un IMEI y presiona Enter"
          class="w-full"
          :disabled="!selectedArticulo"
          @keydown.enter.prevent="agregarImei"
        />
        <DataTable
          v-if="imeis.length"
          :value="imeis"
          class="imeis-table"
          :rows="5"
          :paginator="imeis.length > 5"
          responsiveLayout="scroll"
          emptyMessage="No hay IMEIs agregados."
        >
          <Column header="#" style="width: 50px;">
            <template #body="slotProps">
              {{ slotProps.index + 1 }}
            </template>
          </Column>
          <Column header="IMEI">
            <template #body="slotProps">
              <span :class="{ 'imei-existente': imeisExistentes.includes(slotProps.data) }">
                {{ slotProps.data }}
              </span>
            </template>
          </Column>
          <Column header="Eliminar" style="width: 70px;">
            <template #body="slotProps">
              <Button icon="pi pi-times" class="p-button-text p-button-danger" @click="eliminarImei(slotProps.index)" />
            </template>
          </Column>
        </DataTable>
      </div>
      <div class="form-actions">
        <Button label="Registrar y asignar IMEIs" icon="pi pi-save" @click="registrarYAsignar" class="p-button-success" :disabled="imeis.length === 0" />
      </div>
    </div>
    <Dialog v-model:visible="showDialog" header="Resultado" :modal="true" :closable="false">
      <p>{{ mensaje }}</p>
      <div class="dialog-actions">
        <Button label="Aceptar" icon="pi pi-check" @click="showDialog = false" autofocus />
      </div>
    </Dialog>
    <Dialog v-model:visible="showWarningDialog" header="Advertencia" :modal="true" :closable="false">
      <p style="white-space: pre-line;">{{ warningMessage }}</p>
      <div class="dialog-actions">
        <Button label="Aceptar" icon="pi pi-check" @click="showWarningDialog = false" autofocus />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { getTodosArticulos } from '@/services/articulosService';
import { registrarYAsignarIMEIsPorNombre, getIMEIs } from '@/services/imeiService';
import { getUbicaciones, asignarImeisUbicacion } from '@/services/ubicacionesService';
import { useToast } from 'primevue/usetoast';

const articulos = ref([]);
const selectedArticulo = ref(null);
const nuevoImei = ref('');
const imeis = ref([]);
const mensaje = ref('');
const showDialog = ref(false);
const showWarningDialog = ref(false);
const warningMessage = ref('');
const imeisExistentes = ref([]);
const ubicaciones = ref([]);
const ubicacionDestino = ref(null);

const toast = useToast();

const articulosFiltrados = computed(() =>
  articulos.value.filter(a => a.tipo && a.tipo.toLowerCase() !== 'servicio')
);

onMounted(async () => {
  articulos.value = await getTodosArticulos();
  ubicaciones.value = await getUbicaciones();
  ubicacionDestino.value = ubicaciones.value[0] || null;
});

const agregarImei = () => {
  const imei = nuevoImei.value.trim();
  if (!imei) return;
  if (imeis.value.includes(imei)) {
    warningMessage.value = `El IMEI "${imei}" ya está en la lista.`;
    showWarningDialog.value = true;
    nuevoImei.value = '';
    return;
  }
  imeis.value.push(imei);
  nuevoImei.value = '';
};

const eliminarImei = (idx) => {
  imeis.value.splice(idx, 1);
};

const registrarYAsignar = async () => {
  if (!selectedArticulo.value || imeis.value.length === 0 || !ubicacionDestino.value) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Selecciona artículo, ubicación y agrega al menos un IMEI.', life: 4000 });
    return;
  }

  // Validar IMEIs existentes en la base de datos
  try {
    const todosIMEIs = await getIMEIs();
    const imeisEnBD = new Set(todosIMEIs.map(i => i.imei));
    imeisExistentes.value = imeis.value.filter(i => imeisEnBD.has(i));
  } catch (e) {
    mensaje.value = 'Error al validar IMEIs existentes en la base de datos.';
    showDialog.value = true;
    toast.add({ severity: 'error', summary: 'Error', detail: mensaje.value, life: 4000 });
    return;
  }

  if (imeisExistentes.value.length > 0) {
    mensaje.value = `Los siguientes IMEIs ya están registrados en el sistema:\n${imeisExistentes.value.join('\n')}\nElimínalos de la lista para continuar.`;
    showDialog.value = true;
    toast.add({ severity: 'warn', summary: 'IMEIs existentes', detail: 'Elimina los IMEIs ya registrados para continuar.', life: 5000 });
    return;
  }

  // Si todo está bien, guardar (alta normal)
  try {
    await registrarYAsignarIMEIsPorNombre(selectedArticulo.value.nombre, imeis.value);
    await asignarImeisUbicacion(ubicacionDestino.value.id, imeis.value);
    mensaje.value = `${imeis.value.length} IMEIs asignados al artículo "${selectedArticulo.value.nombre}" y a la ubicación "${ubicacionDestino.value.nombre}" correctamente.`;
    imeis.value = [];
    imeisExistentes.value = [];
    toast.add({ severity: 'success', summary: 'Éxito', detail: mensaje.value, life: 4000 });
  } catch (e) {
    mensaje.value = 'Ocurrió un error al asignar los IMEIs.';
    toast.add({ severity: 'error', summary: 'Error', detail: mensaje.value, life: 4000 });
  }
  showDialog.value = true;
};
</script>

<style scoped>
.imeis-list {
  margin: 0.5rem 0 0 0;
  padding: 0;
  list-style: none;
}
.imeis-list li {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-bottom: 0.25rem;
}
.asignar-imeis-container {
  /* max-width: 500px; */
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  color: var(--color-text);
}
h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--color-title);
}
.form-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.form-group {
  margin-bottom: 1.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-title);
}
.w-full {
  width: 100%;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
.imei-existente {
  color: #fff;
  background: #d32f2f;
  border-radius: 4px;
  padding: 2px 8px;
}
.imeis-table {
  margin-top: 0.5rem;
  background: var(--color-card, #23232b);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.18);
  border: 1.5px solid #fff3;
  overflow: hidden;
}
</style>