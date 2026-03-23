<template>
  <div class="detalle-pago-container">
    <Button icon="pi pi-arrow-left" label="Volver a Pagos" class="p-button-text mb-3" @click="router.push('/pagos')" />

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <div v-else-if="item">
      <div style="display:flex; justify-content:space-between; align-items:center;">
        <h2 class="detalle-title" style="margin-bottom:0;">
          {{ esNota ? 'Nota' : 'Factura' }} #{{ item.id }}
        </h2>
        <Button icon="pi pi-file-pdf" label="Descargar PDF" class="p-button-outlined p-button-danger" @click="descargarPDF" />
      </div>

      <div class="detalle-card">
        <div class="detalle-row"><strong>Órdenes:</strong> {{ (item.ordenes || []).join(', ') }}</div>
        <div class="detalle-row"><strong>Cliente:</strong> {{ item.cliente || '-' }}</div>
        <div class="detalle-row"><strong>Total:</strong> {{ item.total != null ? '$' + Number(item.total).toFixed(2) : '-' }}</div>
        <div class="detalle-row"><strong>Fecha:</strong> {{ formatFecha(item.fecha) }}</div>
        <div class="detalle-row">
          <strong>Estatus actual:</strong>
          <span :class="'badge badge-' + badgeClass(item.status)" style="margin-left:0.5rem;">{{ item.status }}</span>
        </div>
      </div>

      <!-- Cambiar estatus -->
      <div class="cambiar-status">
        <h3>Cambiar estatus</h3>
        <div class="status-options">
          <Dropdown
            v-model="nuevoStatus"
            :options="opcionesStatus"
            optionLabel="label"
            optionValue="value"
            placeholder="Seleccionar estatus"
            class="w-full"
          />
          <Button
            label="Guardar"
            icon="pi pi-save"
            :disabled="!nuevoStatus || nuevoStatus === item.status"
            @click="cambiarStatus"
            :loading="saving"
          />
        </div>
      </div>

      <!-- Comprobante de pago -->
      <div class="comprobante-section">
        <h3>Comprobante de pago</h3>
        <div v-if="item.comprobante_path" class="comprobante-actual">
          <i class="pi pi-file" style="color:#1976d2;margin-right:0.5rem;"></i>
          <a :href="urlComprobante" target="_blank" rel="noopener noreferrer" style="color:#1976d2;font-weight:bold;">Ver / Descargar comprobante</a>
        </div>
        <div v-else style="color:#999;margin-bottom:0.75rem;">No se ha cargado comprobante aún.</div>
        <div class="comprobante-upload">
          <label for="inputComprobante" style="font-weight:bold;display:block;margin-bottom:0.5rem;">{{ item.comprobante_path ? 'Reemplazar comprobante:' : 'Cargar comprobante:' }}</label>
          <input id="inputComprobante" type="file" @change="onFileChange" accept="application/pdf,image/*" />
          <Button
            label="Subir comprobante"
            icon="pi pi-upload"
            class="p-button-success mt-2"
            :disabled="!archivoSeleccionado"
            :loading="subiendo"
            @click="subirComprobante"
          />
        </div>
      </div>

      <!-- Detalle de órdenes incluidas -->
      <div v-if="item.detalle_ordenes && item.detalle_ordenes.length" class="ordenes-detalle">
        <h3>Órdenes incluidas</h3>
        <DataTable :value="item.detalle_ordenes" responsiveLayout="scroll">
          <Column field="folio" header="Orden" />
          <Column field="tipo_servicio" header="Tipo" />
          <Column field="nombre_cliente" header="Cliente" />
          <Column field="total" header="Total">
            <template #body="{ data }">
              {{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}
            </template>
          </Column>
        </DataTable>
      </div>
    </div>

    <div v-else style="text-align:center;padding:3rem;">
      <p>No se encontró el registro.</p>
    </div>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';
import { useToast } from 'primevue/usetoast';
import {
  getNotaById,
  getFacturaById,
  actualizarStatusNota,
  actualizarStatusFactura,
  subirComprobanteNota,
  subirComprobanteFactura
} from '@/services/pagosService';
import { generarPagoPDF } from '@/services/PagoPdfService.js';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const tipo = computed(() => route.params.tipo);   // 'nota' | 'factura'
const id = computed(() => route.params.id);
const esNota = computed(() => tipo.value === 'nota');

const item = ref(null);
const loading = ref(false);
const saving = ref(false);
const nuevoStatus = ref('');
const archivoSeleccionado = ref(null);
const subiendo = ref(false);

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
const urlComprobante = computed(() => {
  if (!item.value?.comprobante_path) return '';
  const p = item.value.comprobante_path.startsWith('/') ? item.value.comprobante_path : `/${item.value.comprobante_path}`;
  return `${API_URL}${p}`;
});

const opcionesStatusNota = [
  { label: 'Pendiente de pago', value: 'pendiente de pago' },
  { label: 'Pagado', value: 'pagado' },
  { label: 'Cancelado', value: 'cancelado' }
];

const opcionesStatusFactura = [
  { label: 'Timbrado', value: 'Timbrado' },
  { label: 'Pendiente timbre', value: 'Pendiente timbre' },
  { label: 'Cancelado', value: 'Cancelado' }
];

const opcionesStatus = computed(() => esNota.value ? opcionesStatusNota : opcionesStatusFactura);

function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}

function badgeClass(status) {
  if (['pagado', 'Timbrado'].includes(status)) return 'success';
  if (['cancelado', 'Cancelado'].includes(status)) return 'danger';
  return 'warning';
}

async function cargarDetalle() {
  loading.value = true;
  try {
    if (esNota.value) {
      item.value = await getNotaById(id.value);
    } else {
      item.value = await getFacturaById(id.value);
    }
    nuevoStatus.value = item.value?.status || '';
  } catch {
    item.value = null;
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el detalle.', life: 4000 });
  }
  loading.value = false;
}

async function cambiarStatus() {
  if (!nuevoStatus.value || nuevoStatus.value === item.value?.status) return;
  saving.value = true;
  try {
    if (esNota.value) {
      await actualizarStatusNota(id.value, nuevoStatus.value);
    } else {
      await actualizarStatusFactura(id.value, nuevoStatus.value);
    }
    item.value.status = nuevoStatus.value;
    toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Estatus actualizado correctamente.', life: 3000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el estatus.', life: 4000 });
  }
  saving.value = false;
}

async function descargarPDF() {
  if (!item.value) return;
  try {
    await generarPagoPDF(tipo.value, item.value);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF.', life: 4000 });
  }
}

onMounted(() => {
  cargarDetalle();
});

function onFileChange(event) {
  const files = event?.target?.files;
  archivoSeleccionado.value = files && files.length ? files[0] : null;
}

async function subirComprobante() {
  if (!archivoSeleccionado.value) return;
  subiendo.value = true;
  try {
    if (esNota.value) {
      await subirComprobanteNota(id.value, archivoSeleccionado.value);
    } else {
      await subirComprobanteFactura(id.value, archivoSeleccionado.value);
    }
    toast.add({ severity: 'success', summary: 'Subido', detail: 'Comprobante cargado correctamente.', life: 3000 });
    archivoSeleccionado.value = null;
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo subir el comprobante.', life: 4000 });
  }
  subiendo.value = false;
}
</script>

<style scoped>
.detalle-pago-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  max-width: 1200px;
}
.detalle-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-title);
}
.detalle-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: 1.5rem;
  margin-bottom: 2rem;
  border: 1px solid var(--color-border);
}
.detalle-row {
  padding: 0.5rem 0;
  border-bottom: 1px solid var(--color-border);
}
.detalle-row:last-child { border-bottom: none; }
.cambiar-status {
  margin-bottom: 2rem;
}
.cambiar-status h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.status-options {
  display: flex;
  gap: 1rem;
  align-items: center;
  flex-wrap: wrap;
}
.status-options .w-full {
  flex: 1;
  min-width: 200px;
}
.ordenes-detalle h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.comprobante-section {
  margin-bottom: 2rem;
}
.comprobante-section h3 {
  margin-bottom: 0.75rem;
  color: var(--color-title);
}
.comprobante-actual {
  margin-bottom: 0.75rem;
  display: flex;
  align-items: center;
}
.comprobante-upload {
  margin-top: 0.5rem;
}
.mt-2 { margin-top: 0.5rem; }
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: bold;
}
.badge-success { background: #c8e6c9; color: #256029; }
.badge-warning { background: #fff3cd; color: #856404; }
.badge-danger  { background: #f8d7da; color: #721c24; }
.mb-3 { margin-bottom: 1rem; }
</style>
