<template>
  <div class="consultar-reportes-container">
    <h2 class="consultar-reportes-title">Consultar Reportes de Servicio</h2>
    <DataTable :value="reportes" responsiveLayout="scroll" :loading="loading">
      <Column field="tipo_servicio" header="Tipo" />
      <Column field="nombre_cliente" header="Cliente" />
      <Column field="so_folio" header="SO">
        <template #body="slotProps">
          {{ obtenerSO(slotProps.data) }}
        </template>
      </Column>
      <Column field="fecha" header="Fecha">
        <template #body="slotProps">
          {{ formatearFecha(slotProps.data.fecha) }}
        </template>
      </Column>
      <Column field="subtotal" header="Subtotal">
        <template #body="slotProps">
          {{ slotProps.data.subtotal ? '$' + Number(slotProps.data.subtotal).toFixed(2) : '-' }}
        </template>
      </Column>
      <Column field="forma_pago" header="Forma de pago" />
      <Column field="pagado" header="¿Pagado?">
        <template #body="slotProps">
          <span :style="{ color: slotProps.data.pagado ? '#28a745' : '#d32f2f', fontWeight: 'bold' }">
            {{ slotProps.data.pagado ? 'Sí' : 'No' }}
          </span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button
            icon="pi pi-pencil"
            class="p-button-sm p-button-info"
            label="Editar"
            @click="abrirEditar(slotProps.data)"
          />
          <Button
            icon="pi pi-trash"
            class="p-button-sm p-button-danger ml-2"
            label="Eliminar"
            @click="confirmarEliminarReporte(slotProps.data)"
          />
          <Button
            icon="pi pi-file-pdf"
            class="p-button-sm p-button-success ml-2"
            label="Orden de venta"
            @click="descargarOrdenVenta(slotProps.data)"
          />
          <Button
            icon="pi pi-file-pdf"
            class="p-button-sm p-button-warning ml-2"
            label="Reporte de servicio"
            @click="descargarReporteServicio(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>

    <!-- Dialogo PDF -->
    <Dialog v-model:visible="showDialog" header="Nota de Venta" :modal="true" class="historico-dialog">
      <NotaVentaPDF
        v-if="ventaSeleccionada && clienteSeleccionado && articulosSeleccionados.length"
        :venta="ventaSeleccionada"
        :cliente="clienteSeleccionado"
        :articulos="articulosSeleccionados"
        :empresa="empresa"
        :venta-registrada="true"
      />
      <Button label="Cerrar" icon="pi pi-times" @click="showDialog = false" class="mt-3" />
    </Dialog>

    <!-- Dialogo Editar Reporte -->
    <Dialog v-model:visible="showEditDialog" header="Editar Reporte de Servicio" :modal="true">
      <form @submit.prevent="guardarEdicion">
        <div v-if="reporteEditando">
          <div class="form-group" v-for="(value, key) in camposReporte" :key="key">
            <label :for="key">{{ value.label }}</label>
            <template v-if="value.type === 'textarea'">
              <textarea v-model="reporteEditando[key]" class="w-full" :id="key" />
            </template>
            <template v-else-if="value.type === 'select'">
              <select v-model="reporteEditando[key]" class="w-full" :id="key">
                <option :value="true">Sí</option>
                <option :value="false">No</option>
              </select>
            </template>
            <template v-else>
              <input v-model="reporteEditando[key]" class="w-full" :id="key" />
            </template>
          </div>
        </div>
        <div class="modal-actions">
          <Button label="Guardar" icon="pi pi-save" type="submit" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showEditDialog = false" type="button" />
        </div>
      </form>
    </Dialog>

    <!-- Dialogo Confirmar Eliminación -->
    <Dialog v-model:visible="showConfirmDeleteDialog" header="Confirmar Eliminación" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Seguro que deseas eliminar este reporte?</span>
      </div>
      <div class="modal-actions">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" @click="eliminarReporteConfirmado" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showConfirmDeleteDialog = false" />
      </div>
    </Dialog>

    <!-- Dialogo Mensaje -->
    <Dialog v-model:visible="showMessageDialog" header="Mensaje" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ messageDialogText }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="showMessageDialog = false" class="mt-3" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import NotaVentaPDF from '@/components/NotaVentaPDF.vue';
import axios from 'axios';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';
import { getVentas, getDetalleVenta } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { useToast } from 'primevue/usetoast';
import { generarReporteServicioPDF } from '@/services/reporteServicioPdfService.js';

const API_URL = `${import.meta.env.VITE_API_URL}/reportes-servicio`;

const toast = useToast();

const reportes = ref([]);
const loading = ref(false);

const showDialog = ref(false);
const showEditDialog = ref(false);
const reporteEditando = ref(null);

const showConfirmDeleteDialog = ref(false);
const reporteAEliminar = ref(null);

const ventaSeleccionada = ref(null);
const clienteSeleccionado = ref(null);
const articulosSeleccionados = ref([]);
const empresa = {
  nombre: 'GPSubicacion.com',
  direccion: 'Guadalajara',
  rfc: 'RFC123456'
};

let asignaciones = [];

const showMessageDialog = ref(false);
const messageDialogText = ref('');

// Campos para edición dinámica
const camposReporte = {
  tipo_servicio: { label: 'Tipo de Servicio' },
  lugar_instalacion: { label: 'Lugar/Centro de instalación' },
  marca: { label: 'Marca' },
  submarca: { label: 'Submarca' },
  modelo: { label: 'Modelo' },
  placas: { label: 'Placas' },
  color: { label: 'Color' },
  numero_economico: { label: 'Número económico' },
  equipo_plan: { label: 'Equipo/Plan' },
  imei: { label: 'IMEI' },
  serie: { label: 'Serie' },
  accesorios: { label: 'Accesorios' },
  sim_proveedor: { label: 'SIM Proveedor' },
  sim_serie: { label: 'SIM Serie' },
  sim_instalador: { label: 'SIM Instalador' },
  sim_telefono: { label: 'SIM Teléfono' },
  bateria: { label: 'Batería' },
  ignicion: { label: 'Ignición' },
  corte: { label: 'Corte bomba/switch' },
  ubicacion_corte: { label: 'Ubicación corte' },
  observaciones: { label: 'Observaciones', type: 'textarea' },
  plataforma: { label: 'Plataforma' },
  usuario: { label: 'Usuario' },
  subtotal: { label: 'Subtotal' },
  total: { label: 'Total' },
  forma_pago: { label: 'Forma de pago' },
  pagado: { label: '¿Pagado?', type: 'select' },
  nombre_cliente: { label: 'Nombre del cliente' },
  firma_cliente: { label: 'Firma del cliente' },
  nombre_instalador: { label: 'Nombre del instalador' },
  firma_instalador: { label: 'Firma del instalador' }
};

async function cargarReportes() {
  loading.value = true;
  try {
    const res = await axios.get(`${API_URL}-todos`);
    reportes.value = res.data;
    asignaciones = await getAsignacionesTecnicos();
  } catch (e) {
    reportes.value = [];
    asignaciones = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al cargar los reportes.', life: 4000 });
    messageDialogText.value = 'Error al cargar los reportes.';
    showMessageDialog.value = true;
  }
  loading.value = false;
}

async function mostrarNota(reporte) {
  loading.value = true;
  const asignacion = asignaciones.find(a => a.id == reporte.asignacion_id);
  if (!asignacion || !asignacion.venta_id) {
    loading.value = false;
    toast.add({ severity: 'warn', summary: 'No encontrada', detail: 'No se encontró la nota de venta relacionada.', life: 4000 });
    messageDialogText.value = 'No se encontró la nota de venta relacionada.';
    showMessageDialog.value = true;
    return;
  }
  const ventas = await getVentas();
  const venta = ventas.find(v => v.id == asignacion.venta_id);
  if (!venta) {
    loading.value = false;
    toast.add({ severity: 'warn', summary: 'No encontrada', detail: 'No se encontró la nota de venta.', life: 4000 });
    messageDialogText.value = 'No se encontró la nota de venta.';
    showMessageDialog.value = true;
    return;
  }
  ventaSeleccionada.value = venta;
  const clientes = await getClientes();
  clienteSeleccionado.value = clientes.find(c => c.id === venta.cliente_id) || {};
  const articulos = await getTodosArticulos();
  const detalle = await getDetalleVenta(venta.id);
  articulosSeleccionados.value = detalle.map(item => {
    const art = articulos.find(a => a.id === item.articulo_id) || {};
    return {
      ...item,
      sku: art.sku,
      nombre: art.nombre
    };
  });
  showDialog.value = true;
  loading.value = false;
}

// Editar
function abrirEditar(reporte) {
  reporteEditando.value = { ...reporte };
  showEditDialog.value = true;
}

async function guardarEdicion() {
  if (!reporteEditando.value) return;
  loading.value = true;
  try {
    await axios.put(`${API_URL}/${reporteEditando.value.id}`, reporteEditando.value);
    await cargarReportes();
    showEditDialog.value = false;
    toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Reporte actualizado correctamente.', life: 3000 });
    messageDialogText.value = 'Reporte actualizado correctamente.';
    showMessageDialog.value = true;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al guardar los cambios.', life: 4000 });
    messageDialogText.value = 'Error al guardar los cambios.';
    showMessageDialog.value = true;
  }
  loading.value = false;
}

// Eliminar con confirmación en Dialog
function confirmarEliminarReporte(reporte) {
  reporteAEliminar.value = reporte;
  showConfirmDeleteDialog.value = true;
}
async function eliminarReporteConfirmado() {
  if (!reporteAEliminar.value) return;
  loading.value = true;
  try {
    await axios.delete(`${API_URL}/${reporteAEliminar.value.id}`);
    await cargarReportes();
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Reporte eliminado correctamente.', life: 3000 });
    messageDialogText.value = 'Reporte eliminado correctamente.';
    showMessageDialog.value = true;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al eliminar el reporte.', life: 4000 });
    messageDialogText.value = 'Error al eliminar el reporte.';
    showMessageDialog.value = true;
  }
  showConfirmDeleteDialog.value = false;
  loading.value = false;
}

async function descargarOrdenVenta(reporte) {
  loading.value = true;
  try {
    const asignacion = asignaciones.find(a => a.id == reporte.asignacion_id);
    if (!asignacion || !asignacion.venta_id) {
      loading.value = false;
      toast.add({ severity: 'warn', summary: 'No encontrada', detail: 'No se encontró la nota de venta relacionada.', life: 4000 });
      messageDialogText.value = 'No se encontró la nota de venta relacionada.';
      showMessageDialog.value = true;
      return;
    }
    const ventas = await getVentas();
    const venta = ventas.find(v => v.id == asignacion.venta_id);
    if (!venta) {
      loading.value = false;
      toast.add({ severity: 'warn', summary: 'No encontrada', detail: 'No se encontró la nota de venta.', life: 4000 });
      messageDialogText.value = 'No se encontró la nota de venta.';
      showMessageDialog.value = true;
      return;
    }
    const clientes = await getClientes();
    const cliente = clientes.find(c => c.id === venta.cliente_id) || {};
    const articulos = await getTodosArticulos();
    const detalle = await getDetalleVenta(venta.id);
    const articulosSeleccionados = detalle.map(item => {
      const art = articulos.find(a => a.id === item.articulo_id) || {};
      return {
        ...item,
        sku: art.sku,
        nombre: art.nombre
      };
    });
    await generarNotaVentaPDF({
      venta,
      cliente,
      articulos: articulosSeleccionados,
      empresa
    });
  } finally {
    loading.value = false;
  }
}

async function descargarReporteServicio(reporte) {
  loading.value = true;
  try {
    const asignacion = asignaciones.find(a => a.id == reporte.asignacion_id);
    let venta = null;
    let cliente = null;
    if (asignacion && asignacion.venta_id) {
      const ventas = await getVentas();
      venta = ventas.find(v => v.id == asignacion.venta_id);
      const clientes = await getClientes();
      cliente = venta ? (clientes.find(c => c.id === venta.cliente_id) || {}) : {};
    }
    await generarReporteServicioPDF({
      reporte,
      venta,
      cliente,
      empresa
    });
  } finally {
    loading.value = false;
  }
}

function formatearFecha(fecha) {
  if (!fecha) return '';
  const d = new Date(fecha);
  const dia = String(d.getDate()).padStart(2, '0');
  const mes = String(d.getMonth() + 1).padStart(2, '0');
  const anio = d.getFullYear();
  return `${dia}/${mes}/${anio}`;
}

function obtenerSO(reporte) {
  // Busca la asignación y la venta asociada para obtener el folio SO
  const asignacion = asignaciones.find(a => a.id == reporte.asignacion_id);
  if (asignacion && asignacion.venta_id && Array.isArray(window.ventasGlobal)) {
    const venta = window.ventasGlobal.find(v => v.id == asignacion.venta_id);
    if (venta && venta.folio) {
      console.log('SO encontrado para reporte', reporte.id, ':', venta.folio);
      return venta.folio;
    }
  }
  return '-';
}

// Carga ventas globalmente para acceso rápido en la tabla
onMounted(async () => {
  window.ventasGlobal = await getVentas();
  await cargarReportes();
});
</script>

<style scoped>
.consultar-reportes-container {
  margin: 2rem auto;
  text-align: center;
  background: #23272f;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  color: #e4c8c8;
  padding: 2rem 1.5rem;
}
.consultar-reportes-title {
  margin-bottom: 2rem;
  color: #e4c8c8;
}
.historico-dialog :deep(.p-dialog-content) {
  background: var(--color-card, #23272f);
  padding: 1.5rem 1rem;
  border-radius: 12px;
}
.historico-dialog :deep(.p-dialog-header) {
  background: var(--color-bg, #23272f);
  color: var(--color-title, #ff4081);
  border-bottom: 1px solid #e0e0e0;
  border-radius: 12px 12px 0 0;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 1rem 1.5rem;
}
.mt-3 {
  margin-top: 1.5rem;
}
.form-group {
  margin-bottom: 1rem;
  text-align: left;
}
.w-full {
  width: 100%;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>