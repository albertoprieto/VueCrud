<template>
  <div class="consultar-reportes-container">
    <h2 class="consultar-reportes-title">Consultar Reportes de Servicio</h2>
    <DataTable :value="reportes" responsiveLayout="scroll" :loading="loading">
      <Column field="id" header="ID" />
      <Column field="asignacion_id" header="Asignación" />
      <Column field="tipo_servicio" header="Tipo de Servicio" />
      <Column field="marca" header="Marca" />
      <Column field="modelo" header="Modelo" />
      <Column field="placas" header="Placas" />
      <Column field="nombre_cliente" header="Cliente" />
      <Column field="fecha" header="Fecha" />
      <Column field="nombre_instalador" header="Instalador" />
      <Column field="observaciones" header="Observaciones" />
      <Column header="Nota de Venta">
        <template #body="slotProps">
          <Button
            icon="pi pi-file-pdf"
            label="Ver PDF"
            size="small"
            @click="mostrarNota(slotProps.data)"
            v-if="slotProps.data.asignacion_id"
          />
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
          <div class="form-group">
            <label>Tipo de Servicio</label>
            <input v-model="reporteEditando.tipo_servicio" class="w-full" />
          </div>
          <div class="form-group">
            <label>Marca</label>
            <input v-model="reporteEditando.marca" class="w-full" />
          </div>
          <div class="form-group">
            <label>Modelo</label>
            <input v-model="reporteEditando.modelo" class="w-full" />
          </div>
          <div class="form-group">
            <label>Placas</label>
            <input v-model="reporteEditando.placas" class="w-full" />
          </div>
          <div class="form-group">
            <label>Observaciones</label>
            <textarea v-model="reporteEditando.observaciones" class="w-full" />
          </div>
          <!-- Agrega más campos según tu modelo -->
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
import { getVentas, getDetalleVenta } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';

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

async function cargarReportes() {
  loading.value = true;
  try {
    const res = await axios.get('https://api.gpsubicacionapi.com/reportes-servicio-todos');
    reportes.value = res.data;
    asignaciones = await getAsignacionesTecnicos();
  } catch (e) {
    reportes.value = [];
    asignaciones = [];
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
    messageDialogText.value = 'No se encontró la nota de venta relacionada.';
    showMessageDialog.value = true;
    return;
  }
  const ventas = await getVentas();
  const venta = ventas.find(v => v.id == asignacion.venta_id);
  if (!venta) {
    loading.value = false;
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
    await axios.put(`https://api.gpsubicacionapi.com/reportes-servicio/${reporteEditando.value.id}`, reporteEditando.value);
    await cargarReportes();
    showEditDialog.value = false;
    messageDialogText.value = 'Reporte actualizado correctamente.';
    showMessageDialog.value = true;
  } catch (e) {
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
    await axios.delete(`https://api.gpsubicacionapi.com/reportes-servicio/${reporteAEliminar.value.id}`);
    await cargarReportes();
    messageDialogText.value = 'Reporte eliminado correctamente.';
    showMessageDialog.value = true;
  } catch (e) {
    messageDialogText.value = 'Error al eliminar el reporte.';
    showMessageDialog.value = true;
  }
  showConfirmDeleteDialog.value = false;
  loading.value = false;
}

onMounted(cargarReportes);
</script>

<style scoped>
.consultar-reportes-container {
  max-width: 800px;
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