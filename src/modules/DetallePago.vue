<template>
  <div class="detalle-pago-container">
    <Button icon="pi pi-arrow-left" label="Volver a Pagos" class="p-button-text mb-3" @click="router.push('/pagos')" />

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <div v-else-if="item">
      <div style="display:flex; justify-content:space-between; align-items:center; gap:0.75rem;">
        <h2 class="detalle-title" style="margin-bottom:0;">
          {{ esNota ? 'Nota' : 'Factura' }} #{{ item.id }}
        </h2>
        <div style="display:flex; gap:0.75rem; align-items:center; flex-wrap:wrap;">
          <Button
            v-if="item.reporte_ids && item.reporte_ids.length"
            icon="pi pi-list"
            :label="`Ver Reportes de Servicio (${item.reporte_ids.length})`"
            class="p-button-outlined p-button-info"
            :loading="loadingReportes"
            @click="abrirReportesDialog"
          />
          <Button
            v-if="esEditable"
            icon="pi pi-plus"
            label="Agregar Servicios"
            class="p-button-outlined p-button-success"
            @click="abrirAgregarDialog"
          />
          <Button icon="pi pi-file-pdf" label="Descargar PDF" class="p-button-outlined p-button-danger" @click="descargarPDF" />
        </div>
      </div>

      <div class="detalle-card">
        <div class="detalle-row"><strong>Órdenes:</strong> {{ (item.ordenes || []).join(', ') }}</div>
        <div class="detalle-row"><strong>Cliente:</strong> {{ item.cliente || '-' }}</div>
        <div class="detalle-row"><strong>Total:</strong> {{ item.total != null ? '$' + Number(item.total).toFixed(2) : '-' }}</div>
        <div class="detalle-row"><strong>Fecha:</strong> {{ formatFecha(item.fecha) }}</div>
        <div class="detalle-row"><strong>Lugar de pago:</strong> {{ item.lugar_pago || '-' }}</div>
        <div class="detalle-row">
          <strong>Estatus actual:</strong>
          <span :class="'badge badge-' + badgeClass(item.status)" style="margin-left:0.5rem;">{{ item.status }}</span>
        </div>
      </div>

      <!-- Cambiar estatus y lugar de pago -->
      <div class="cambiar-status">
        <h3>Cambiar estatus y lugar de pago</h3>
        <div class="status-options">
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Estatus:</label>
            <Dropdown
              v-model="nuevoStatus"
              :options="opcionesStatus"
              optionLabel="label"
              optionValue="value"
              placeholder="Seleccionar estatus"
              class="w-full"
            />
          </div>
          <div style="flex: 1; min-width: 200px;">
            <label style="display: block; margin-bottom: 0.5rem; font-weight: bold;">Lugar de pago:</label>
            <Dropdown
              v-model="nuevoLugarPago"
              :options="lugaresDisponibles"
              placeholder="Seleccionar lugar de pago"
              class="w-full"
            />
          </div>
          <Button
            label="Guardar"
            icon="pi pi-save"
            :disabled="(!nuevoStatus || nuevoStatus === item.status) && (!nuevoLugarPago || nuevoLugarPago === item.lugar_pago)"
            @click="cambiarStatusYLugar"
            :loading="saving"
            style="align-self: flex-end;"
          />
        </div>
      </div>

      <!-- Comprobantes de pago -->
      <div class="comprobante-section">
        <h3>Comprobantes de pago</h3>
        <div v-if="item.comprobantes && item.comprobantes.length" class="comprobantes-lista">
          <div v-for="(comp, idx) in item.comprobantes" :key="idx" class="comprobante-item">
            <i class="pi pi-file" style="color:#1976d2;margin-right:0.5rem;"></i>
            <a :href="urlComprobante(comp)" target="_blank" rel="noopener noreferrer" style="color:#1976d2;font-weight:bold;flex:1;">
              {{ nombreArchivo(comp) }}
            </a>
            <Button
              icon="pi pi-trash"
              class="p-button-text p-button-danger p-button-sm"
              :loading="eliminandoComprobante === comp"
              @click="eliminarComprobante(comp)"
              v-tooltip.top="'Eliminar comprobante'"
            />
          </div>
        </div>
        <div v-else style="color:#999;margin-bottom:0.75rem;">No se han cargado comprobantes aún.</div>
        <div class="comprobante-upload">
          <label for="inputComprobante" style="font-weight:bold;display:block;margin-bottom:0.5rem;">Agregar comprobante:</label>
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

      <!-- Observaciones -->
      <div class="observaciones-section">
        <h3>Observaciones</h3>
        <Textarea
          v-model="observacionesTexto"
          rows="4"
          placeholder="Escribe observaciones sobre esta nota..."
          class="w-full"
          style="width:100%;resize:vertical;"
        />
        <Button
          label="Guardar observaciones"
          icon="pi pi-save"
          class="p-button-secondary mt-2"
          :loading="guardandoObs"
          :disabled="observacionesTexto === (item.observaciones || '')"
          @click="guardarObservaciones"
        />
      </div>

      <!-- Detalle de órdenes incluidas -->
      <div v-if="item.detalle_ordenes && item.detalle_ordenes.length" class="ordenes-detalle">
        <h3>Órdenes incluidas</h3>
        <DataTable :value="item.detalle_ordenes" responsiveLayout="scroll">
          <Column field="folio" header="Orden" />
          <Column field="tipo_servicio" header="Tipo" />
          <Column field="nombre_cliente" header="Cliente" />
          <Column field="imei" header="IMEI" />
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

    <!-- Dialog: Lista de Reportes de Servicio -->
    <Dialog
      v-model:visible="reportesDialogVisible"
      :header="`Reportes de Servicio (${reportesList.length})`"
      :modal="true"
      :style="{ width: '750px', maxWidth: '95vw' }"
      :draggable="false"
    >
      <div v-if="reportesList.length === 0" style="text-align:center;padding:1rem;color:#999;">
        Sin reportes cargados.
      </div>
      <DataTable v-else :value="reportesList" responsiveLayout="scroll">
        <Column header="Folio">
          <template #body="{ data }">
            {{ data.folio || `SERVICIO-${String(data.id).padStart(5, '0')}` }}
          </template>
        </Column>
        <Column field="tipo_servicio" header="Tipo de Servicio" />
        <Column field="nombre_cliente" header="Cliente" />
        <Column header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Acciones">
          <template #body="{ data }">
            <div style="display:flex;gap:0.5rem;">
              <Button
                icon="pi pi-file-pdf"
                label="Ver PDF"
                class="p-button-sm p-button-warning"
                :loading="loadingPdf"
                @click="verPDF(data)"
              />
              <Button
                v-if="esEditable"
                icon="pi pi-times"
                label="Quitar"
                class="p-button-sm p-button-danger p-button-outlined"
                :loading="quitando === data.id"
                @click="quitarReporte(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>
    </Dialog>

    <!-- Dialog: PDF de Reporte de Servicio -->
    <Dialog
      v-model:visible="pdfDialogVisible"
      :header="pdfTitle"
      :modal="true"
      :style="{ width: '85vw' }"
      :draggable="false"
      @hide="cerrarPdfDialog"
    >
      <iframe
        v-if="pdfUrl"
        :src="pdfUrl"
        style="width:100%;height:80vh;border:none;"
      />
    </Dialog>

    <!-- Dialog: Agregar Servicios a la nota/factura -->
    <Dialog
      v-model:visible="agregarDialogVisible"
      :header="`Agregar servicios a ${esNota ? 'Nota' : 'Factura'} #${item?.id}`"
      :modal="true"
      :style="{ width: '75vw' }"
      :draggable="false"
    >
      <div v-if="loadingDisponibles" style="text-align:center;padding:2rem;">
        <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
      </div>
      <template v-else>
        <div style="display:flex;gap:0.75rem;flex-wrap:wrap;margin-bottom:1rem;">
          <InputText v-model="filtroAgregarFolio" placeholder="Buscar por folio / OS" style="flex:1;min-width:150px;" />
          <InputText v-model="filtroAgregarCliente" placeholder="Buscar por cliente" style="flex:1;min-width:150px;" />
          <InputText v-model="filtroAgregarTipo" placeholder="Buscar por tipo" style="flex:1;min-width:150px;" />
        </div>
        <p v-if="!reportesDisponiblesFiltrados.length" style="text-align:center;color:var(--color-text-muted,#888);">
          {{ reportesDisponibles.length ? 'Sin resultados para los filtros aplicados.' : 'No hay reportes de servicio disponibles para agregar.' }}
        </p>
        <DataTable
          v-else
          v-model:selection="reportesSeleccionados"
          :value="reportesDisponiblesFiltrados"
          dataKey="id"
          :paginator="reportesDisponiblesFiltrados.length > 10"
          :rows="10"
          selectionMode="multiple"
          size="small"
        >
          <Column selectionMode="multiple" style="width:3rem" />
          <Column field="folio" header="Folio" />
          <Column field="tipo_servicio" header="Tipo" />
          <Column field="nombre_cliente" header="Cliente" />
          <Column field="total" header="Total">
            <template #body="{ data }">{{ data.total != null ? '$' + Number(data.total).toFixed(2) : '-' }}</template>
          </Column>
          <Column field="fecha" header="Fecha">
            <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
          </Column>
        </DataTable>
        <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
          <Button label="Cancelar" class="p-button-text" @click="agregarDialogVisible = false" />
          <Button
            label="Agregar seleccionados"
            icon="pi pi-check"
            class="p-button-success"
            :disabled="!reportesSeleccionados.length"
            :loading="agregando"
            @click="confirmarAgregar"
          />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import { useToast } from 'primevue/usetoast';
import {
  getNotaById,
  getFacturaById,
  actualizarStatusNota,
  actualizarStatusFactura,
  actualizarLugarPagoNota,
  actualizarLugarPagoFactura,
  actualizarObservacionesNota,
  actualizarObservacionesFactura,
  subirComprobanteNota,
  subirComprobanteFactura,
  eliminarComprobanteNota,
  eliminarComprobanteFactura,
  agregarReportesNota,
  agregarReportesFactura,
  quitarReportesNota,
  quitarReportesFactura,
  getNotas,
  getFacturas
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
const nuevoLugarPago = ref('');
const observacionesTexto = ref('');
const guardandoObs = ref(false);
const archivoSeleccionado = ref(null);
const subiendo = ref(false);
const eliminandoComprobante = ref(null);

// Agregar servicios
const agregarDialogVisible = ref(false);
const reportesDisponibles = ref([]);
const loadingDisponibles = ref(false);
const reportesSeleccionados = ref([]);
const agregando = ref(false);
const filtroAgregarCliente = ref('');
const filtroAgregarFolio = ref('');
const filtroAgregarTipo = ref('');

const reportesDisponiblesFiltrados = computed(() => {
  return reportesDisponibles.value.filter(r => {
    const cliente = filtroAgregarCliente.value.trim().toLowerCase();
    const folio = filtroAgregarFolio.value.trim().toLowerCase();
    const tipo = filtroAgregarTipo.value.trim().toLowerCase();
    if (cliente && !(r.nombre_cliente || '').toLowerCase().includes(cliente)) return false;
    if (folio && !(r.folio || '').toLowerCase().includes(folio)) return false;
    if (tipo && !(r.tipo_servicio || '').toLowerCase().includes(tipo)) return false;
    return true;
  });
});

const esEditable = computed(() => {
  if (!item.value?.status) return false;
  const s = item.value.status.toLowerCase();
  return !['pagado', 'timbrado', 'cancelado'].includes(s);
});

// Reportes de servicio
const reportesDialogVisible = ref(false);
const pdfDialogVisible = ref(false);
const reportesList = ref([]);
const loadingReportes = ref(false);
const pdfUrl = ref('');
const pdfTitle = ref('');
const loadingPdf = ref(false);
const quitando = ref(null);  // ID del reporte que se está quitando

const lugaresDisponibles = [
  'ASP Vianey',
  'ASP Renovaciones',
  'Comercializadora',
  'BBVA PAU',
  'Tecnico',
  'Oficina',
  'Mercadopago'
];

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_URL}${p}`;
}

function nombreArchivo(path) {
  if (!path) return 'comprobante';
  return path.split('/').pop();
}

const opcionesStatusNota = [
  { label: 'Pendiente de pago', value: 'pendiente de pago' },
  { label: 'Pagado', value: 'pagado' },
  { label: 'Cancelado', value: 'cancelado' }
];

const opcionesStatusFactura = [
  { label: 'Pendiente de pago', value: 'pendiente de pago' },
  { label: 'Pagado', value: 'pagado' },
  { label: 'Timbrado', value: 'Timbrado' },
  { label: 'No timbrado', value: 'No timbrado' },
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
    nuevoLugarPago.value = item.value?.lugar_pago || '';
    observacionesTexto.value = item.value?.observaciones || '';
  } catch {
    item.value = null;
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el detalle.', life: 4000 });
  }
  loading.value = false;
}

async function cambiarStatusYLugar() {
  const statusChanged = nuevoStatus.value && nuevoStatus.value !== item.value?.status;
  const lugarChanged = nuevoLugarPago.value && nuevoLugarPago.value !== item.value?.lugar_pago;
  
  if (!statusChanged && !lugarChanged) return;
  
  saving.value = true;
  try {
    if (esNota.value) {
      if (statusChanged) {
        await actualizarStatusNota(id.value, nuevoStatus.value);
        item.value.status = nuevoStatus.value;
      }
      if (lugarChanged) {
        await actualizarLugarPagoNota(id.value, nuevoLugarPago.value);
        item.value.lugar_pago = nuevoLugarPago.value;
      }
    } else {
      if (statusChanged) {
        await actualizarStatusFactura(id.value, nuevoStatus.value);
        item.value.status = nuevoStatus.value;
      }
      if (lugarChanged) {
        await actualizarLugarPagoFactura(id.value, nuevoLugarPago.value);
        item.value.lugar_pago = nuevoLugarPago.value;
      }
    }
    toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Datos actualizados correctamente.', life: 3000 });
    // Si se canceló, recargar para reflejar que reporte_ids quedó vacío
    const cancelado = ['cancelado', 'Cancelado'].includes(nuevoStatus.value);
    if (statusChanged && cancelado) await cargarDetalle();
  } catch (error) {
    console.error(error);
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar los datos.', life: 4000 });
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

async function guardarObservaciones() {
  guardandoObs.value = true;
  try {
    if (esNota.value) {
      await actualizarObservacionesNota(id.value, observacionesTexto.value);
    } else {
      await actualizarObservacionesFactura(id.value, observacionesTexto.value);
    }
    item.value.observaciones = observacionesTexto.value;
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Observaciones guardadas correctamente.', life: 3000 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron guardar las observaciones.', life: 4000 });
  }
  guardandoObs.value = false;
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
    const inputEl = document.getElementById('inputComprobante');
    if (inputEl) inputEl.value = '';
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo subir el comprobante.', life: 4000 });
  }
  subiendo.value = false;
}

async function eliminarComprobante(path) {
  eliminandoComprobante.value = path;
  try {
    if (esNota.value) {
      await eliminarComprobanteNota(id.value, path);
    } else {
      await eliminarComprobanteFactura(id.value, path);
    }
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Comprobante eliminado.', life: 3000 });
    await cargarDetalle();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el comprobante.', life: 4000 });
  }
  eliminandoComprobante.value = null;
}

async function abrirReportesDialog() {
  if (!item.value?.reporte_ids?.length) return;
  loadingReportes.value = true;
  try {
    const results = await Promise.all(
      item.value.reporte_ids.map(rid =>
        axios.get(`${API_URL}/reportes-servicio/${rid}`).then(r => r.data)
      )
    );
    reportesList.value = results;
    reportesDialogVisible.value = true;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los reportes de servicio.', life: 4000 });
  }
  loadingReportes.value = false;
}

async function verPDF(reporte) {
  loadingPdf.value = true;
  try {
    const resp = await axios.get(`${API_URL}/reportes-servicio/${reporte.id}`);
    const merged = { ...reporte, ...resp.data };
    const { generarReporteServicioPDF } = await import('@/components/GeneraReporteServicioPDF.js');
    const url = await generarReporteServicioPDF({ reporte: merged, mode: 'bloburl' });
    if (pdfUrl.value) URL.revokeObjectURL(pdfUrl.value);
    pdfUrl.value = url;
    pdfTitle.value = merged.folio || `Reporte #${merged.id}`;
    pdfDialogVisible.value = true;
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF del reporte.', life: 4000 });
  }
  loadingPdf.value = false;
}

function cerrarPdfDialog() {
  pdfDialogVisible.value = false;
  if (pdfUrl.value) {
    URL.revokeObjectURL(pdfUrl.value);
    pdfUrl.value = '';
  }
}

async function quitarReporte(reporte) {
  quitando.value = reporte.id;
  try {
    if (esNota.value) {
      await quitarReportesNota(id.value, [reporte.id]);
    } else {
      await quitarReportesFactura(id.value, [reporte.id]);
    }
    reportesList.value = reportesList.value.filter(r => r.id !== reporte.id);
    if (reportesList.value.length === 0) reportesDialogVisible.value = false;
    await cargarDetalle();
    toast.add({ severity: 'success', summary: 'Quitado', detail: `Reporte "${reporte.folio || '#' + reporte.id}" quitado correctamente.`, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo quitar el reporte.', life: 4000 });
  }
  quitando.value = null;
}

async function abrirAgregarDialog() {
  loadingDisponibles.value = true;
  agregarDialogVisible.value = true;
  try {
    const [todosReportes, notas, facturas] = await Promise.all([
      axios.get(`${API_URL}/reportes-servicio-todos`).then(r => r.data),
      getNotas(),
      getFacturas()
    ]);
    const asignados = new Set();
    const currentIds = new Set(item.value?.reporte_ids || []);
    for (const n of notas) {
      for (const rid of (n.reporte_ids || [])) {
        if (esNota.value && n.id === Number(id.value)) continue;
        asignados.add(rid);
      }
    }
    for (const f of facturas) {
      for (const rid of (f.reporte_ids || [])) {
        if (!esNota.value && f.id === Number(id.value)) continue;
        asignados.add(rid);
      }
    }
    reportesDisponibles.value = todosReportes.filter(r => !asignados.has(r.id) && !currentIds.has(r.id));
    reportesSeleccionados.value = [];
    filtroAgregarCliente.value = '';
    filtroAgregarFolio.value = '';
    filtroAgregarTipo.value = '';
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los reportes disponibles.', life: 4000 });
    agregarDialogVisible.value = false;
  }
  loadingDisponibles.value = false;
}

async function confirmarAgregar() {
  if (!reportesSeleccionados.value.length) return;
  agregando.value = true;
  try {
    const nuevos_ids = reportesSeleccionados.value.map(r => r.id);
    if (esNota.value) {
      await agregarReportesNota(id.value, nuevos_ids);
    } else {
      await agregarReportesFactura(id.value, nuevos_ids);
    }
    agregarDialogVisible.value = false;
    reportesSeleccionados.value = [];
    await cargarDetalle();
    toast.add({ severity: 'success', summary: 'Agregado', detail: `Se agregaron ${nuevos_ids.length} servicio(s) correctamente.`, life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudieron agregar los servicios.', life: 4000 });
  }
  agregando.value = false;
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
.observaciones-section {
  margin-bottom: 2rem;
}
.observaciones-section h3 {
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
.comprobantes-lista {
  margin-bottom: 0.75rem;
}
.comprobante-item {
  display: flex;
  align-items: center;
  padding: 0.4rem 0;
  border-bottom: 1px solid var(--color-border);
}
.comprobante-item:last-child {
  border-bottom: none;
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
