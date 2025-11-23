<template>
  <div class="consultar-reportes-container">
    <!-- Botón global para agregar reporte de servicio -->
    <div style="display: flex; justify-content: flex-end; margin-bottom: 1.5rem;">
      <Button
        label="Agregar Reporte"
        icon="pi pi-plus"
        class="p-button-success"
        @click="irReporteServicioGlobal"
      />
    </div>
    <div v-if="showNuevoReporteDialog">
      <NuevoReporteDeServicio @close="showNuevoReporteDialog = false" />
    </div>
    <h2 class="consultar-reportes-title">Reportes de Servicio</h2>
    <div class="filtros" style="display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
      <InputText v-model="filtroCliente" placeholder="Filtrar por cliente" class="filtro-input" clearable />
      <InputText v-model="filtroSO" placeholder="Filtrar por Orden de servicio" class="filtro-input" clearable />
      <InputText v-model="filtroVendedor" placeholder="Filtrar por vendedor" class="filtro-input" clearable />
      <InputText v-model="filtroFecha" placeholder="Filtrar por fecha (YYYY-MM-DD)" class="filtro-input" clearable />
      <InputText v-model="filtroTecnico" placeholder="Filtrar por técnico" class="filtro-input" clearable />
      <InputText v-model="filtroIMEI" placeholder="Filtrar por IMEI" class="filtro-input" clearable />
      <Dropdown
        v-model="filtroPagado"
        :options="[
          { label: 'Todos', value: '' },
          { label: 'Sí', value: true },
          { label: 'No', value: false }
        ]"
        optionLabel="label"
        optionValue="value"
        placeholder="¿Pagado?"
        class="filtro-input"
        showClear
      />
    </div>
    <DataTable :value="reportesFiltrados" responsiveLayout="scroll" :loading="loading">
      <Column field="tipo_servicio" header="Tipo" />
      <Column field="nombre_cliente" header="Cliente" />
      <Column header="Orden">
        <template #body="slotProps">
          <span>
            {{ slotProps.data.folio  }}
          </span>
        </template>
      </Column>
      <Column header="Vendedor">
        <template #body="slotProps">
          <span>
            {{ slotProps.data.vendedor || '-' }}
          </span>
        </template>
      </Column>
      <Column field="fecha" header="Fecha">
        <template #body="slotProps">
          {{ formatearFecha(slotProps.data.fecha) }}
        </template>
      </Column>
      <Column field="nombre_instalador" header="Técnico" />
      <Column field="monto_tecnico" header="Monto Técnico">
        <template #body="slotProps">
          {{ slotProps.data.monto_tecnico ? '$' + Number(slotProps.data.monto_tecnico).toFixed(2) : '-' }}
        </template>
      </Column>
      <Column field="viaticos" header="Viáticos">
        <template #body="slotProps">
          {{ slotProps.data.viaticos ? '$' + Number(slotProps.data.viaticos).toFixed(2) : '-' }}
        </template>
      </Column>
      <Column field="total" header="Total Cobrado">
        <template #body="slotProps">
          {{ slotProps.data.total ? '$' + Number(slotProps.data.total).toFixed(2) : '-' }}
        </template>
      </Column>
      <Column field="pagado" header="¿Pagado?">
        <template #body="slotProps">
          <span :style="{ color: slotProps.data.pagado ? '#28a745' : (slotProps.data.comprobante_estado==='pendiente' ? '#f0ad4e' : '#d32f2f'), fontWeight: 'bold' }">
            {{ slotProps.data.pagado ? 'Sí' : (slotProps.data.comprobante_estado==='pendiente' ? 'En revisión' : 'No') }}
          </span>
        </template>
      </Column>
      <Column header="Acciones">
          <template #body="slotProps">
            <div style="display: flex; flex-wrap: wrap; gap: 0.5rem; justify-content: flex-start; align-items: center; min-width: 320px;">
              <Button
                v-if="!slotProps.data.pagado"  
                icon="pi pi-pencil"
                class="p-button-sm p-button-info"
                label="Editar"
                @click="abrirEditar(slotProps.data)"
              />
              <Button
                v-if="!slotProps.data.pagado"
                icon="pi pi-trash"
                class="p-button-sm p-button-danger"
                label="Eliminar"
                @click="confirmarEliminarReporte(slotProps.data)"
              />
              <Button
                icon="pi pi-file-pdf"
                class="p-button-sm p-button-warning"
                label="Reporte de servicio"
                @click="descargarReporteServicio(slotProps.data)"
              />
              <!-- Ver comprobante cuando existe -->
              <a v-if="slotProps.data.comprobante_path" :href="urlComprobante(slotProps.data)" target="_blank" rel="noopener noreferrer" style="display: contents;">
                <Button
                  icon="pi pi-download"
                  class="p-button-sm p-button-secondary"
                  label="Ver comprobante"
                />
              </a>
              <Button
                v-if="!slotProps.data.pagado && !slotProps.data.comprobante_path"
                icon="pi pi-upload"
                class="p-button-sm p-button-success"
                label="Marcar como pagado"
                @click="marcarComoPagado(slotProps.data)"
              />
              <Button
                v-if="user && user.perfil==='Admin' && slotProps.data.comprobante_estado==='pendiente' && !slotProps.data.pagado"
                icon="pi pi-check-circle"
                class="p-button-sm p-button-success"
                label="Aprobar comprobante"
                @click="aprobarComprobante(slotProps.data)"
              />
              <Button
                v-if="user && user.perfil==='Admin' && slotProps.data.comprobante_estado==='pendiente' && !slotProps.data.pagado"
                icon="pi pi-times-circle"
                class="p-button-sm p-button-danger"
                label="Rechazar comprobante"
                @click="rechazarComprobante(slotProps.data)"
              />
            </div>
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
            <InputText v-model="reporteEditando.tipo_servicio" class="w-full" />
          </div>
          <div class="form-group">
            <label>Lugar / Centro de instalación</label>
            <InputText v-model="reporteEditando.lugar_instalacion" class="w-full" />
          </div>
          <h4 class="section-title">Datos del vehículo</h4>
          <div class="form-group">
            <InputText v-model="reporteEditando.marca" placeholder="Marca" class="w-full mb-2" />
            <InputText v-model="reporteEditando.submarca" placeholder="Submarca" class="w-full mb-2" />
            <InputText v-model="reporteEditando.modelo" placeholder="Modelo" class="w-full mb-2" />
            <InputText v-model="reporteEditando.placas" placeholder="Placa" class="w-full mb-2" />
            <InputText v-model="reporteEditando.color" placeholder="Color" class="w-full mb-2" />
            <InputText v-model="reporteEditando.numero_economico" placeholder="Número económico" class="w-full mb-2" />
          </div>
          <h4 class="section-title">Datos del dispositivo</h4>
          <div class="form-group">
            <InputText v-model="reporteEditando.modelo_gps" placeholder="Modelo GPS" class="w-full mb-2" />
            <InputText v-model="reporteEditando.imei" placeholder="IMEI" class="w-full mb-2" />
            <InputText v-model="reporteEditando.sim_serie" placeholder="SIM" class="w-full mb-2" />
            <InputText v-model="reporteEditando.accesorios" placeholder="Accesorios adicionales" class="w-full mb-2" />
            <InputText v-model="reporteEditando.ubicacion_gps" placeholder="Ubicación del GPS" class="w-full mb-2" />
            <InputText v-model="reporteEditando.ubicacion_bloqueo" placeholder="Ubicación del Bloqueo" class="w-full mb-2" />
          </div>
          <div class="form-group">
            <label>Observaciones</label>
            <InputText v-model="reporteEditando.observaciones" class="w-full" />
          </div>
          <h4 class="section-title">Datos del cobro</h4>
          <div class="form-group">
            <label>Subtotal (orden de servicio)</label>
            <InputText v-model="reporteEditando.subtotal" class="w-full mb-2" disabled />
          </div>
          <div class="form-group">
            <label>Total a cobrar</label>
            <InputText v-model="reporteEditando.total" class="w-full mb-2" />
          </div>
          <div class="form-group">
            <label>Método de pago</label>
            <InputText v-model="reporteEditando.forma_pago" class="w-full mb-2" disabled />
          </div>
          <div class="form-group">
            <label>Monto cobrado por el técnico</label>
            <InputText v-model="reporteEditando.monto_tecnico" type="number" class="w-full mb-2" />
          </div>
          <div class="form-group">
            <label>Viáticos</label>
            <InputText v-model="reporteEditando.viaticos" type="number" class="w-full mb-2" />
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
        <span v-if="!messageDialogText">Factura generada correctamente.</span>
        <span v-else>{{ messageDialogText }}</span>
        <div v-if="xmlGenerado || pdfGenerado" style="margin-top:2rem; display: flex; gap: 1rem; justify-content: center;">
          <Button v-if="xmlGenerado" label="Descargar XML" icon="pi pi-download" @click="descargarXML" class="p-button-success" />
          <Button v-if="pdfGenerado" label="Descargar PDF" icon="pi pi-file-pdf" @click="descargarPDF" class="p-button-warning" />
        </div>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="showMessageDialog = false" class="mt-3" />
    </Dialog>

    <!-- Dialogo Factura (PrimeVue, datos prellenados) -->
    <Dialog v-model:visible="showFacturaDialog" header="Datos de Facturación" :modal="true" :closable="false">
      <form @submit.prevent="enviarFactura">
        <div class="form-group">
          <label>Nombre del cliente</label>
          <InputText v-model="facturaData.nombre_cliente" class="w-full" required />
        </div>
        <div class="form-group">
          <label>RFC del cliente</label>
          <InputText v-model="facturaData.rfc_cliente" class="w-full" required />
        </div>
        <div class="form-group">
          <label>Uso CFDI</label>
          <InputText v-model="facturaData.uso_cfdi" class="w-full" required />
        </div>
        <div class="form-group">
          <label>Método de pago</label>
          <InputText v-model="facturaData.metodo_pago" class="w-full" required />
        </div>
        <div class="form-group">
          <label>Forma de pago</label>
          <InputText v-model="facturaData.forma_pago" class="w-full" required />
        </div>
        <div class="form-group">
          <label>Total</label>
          <InputNumber v-model="facturaData.total" class="w-full" required />
        </div>
        <div class="form-group">
          <label>Productos</label>
          <div v-for="(prod, idx) in facturaData.productos" :key="idx" style="margin-bottom:1rem; border-bottom:1px solid #eee;">
            <InputText v-model="prod.ClaveProdServ" placeholder="ClaveProdServ" class="w-full" required />
            <InputText v-model="prod.ClaveUnidad" placeholder="ClaveUnidad" class="w-full" required />
            <InputText v-model="prod.Unidad" placeholder="Unidad" class="w-full" required />
            <InputText v-model="prod.Descripcion" placeholder="Descripción" class="w-full" required />
            <InputNumber v-model="prod.ValorUnitario" placeholder="ValorUnitario" class="w-full" required />
            <InputNumber v-model="prod.Importe" placeholder="Importe" class="w-full" required />
            <InputNumber v-model="prod.Cantidad" placeholder="Cantidad" class="w-full" required />
          </div>
        </div>
        <div class="modal-actions">
          <Button label="Facturar" icon="pi pi-check" type="submit" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showFacturaDialog = false" type="button" />
        </div>
      </form>
    </Dialog>

    <!-- Dialogo Comprobante (obligatorio para marcar como pagado) -->
    <Dialog v-model:visible="showComprobanteDialog" header="Cargar comprobante" :modal="true" :closable="false">
      <form @submit.prevent="confirmarPagadoConComprobante">
        <div class="form-group">
          <label for="comprobante">Selecciona un archivo de comprobante (obligatorio)</label>
          <input id="comprobante" type="file" @change="onComprobanteChange" accept="application/pdf,image/*" class="w-full" />
          <small v-if="!archivoComprobante" style="color:#d32f2f;display:block;margin-top:0.5rem;">Debes cargar un comprobante para continuar.</small>
          <small v-else style="color:#28a745;display:block;margin-top:0.5rem;">{{ archivoComprobante?.name }}</small>
        </div>
        <div class="modal-actions">
          <Button label="Subir y enviar a revisión" icon="pi pi-check" type="submit" :disabled="!archivoComprobante" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" type="button" @click="cancelarComprobante" />
        </div>
      </form>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import NotaVentaPDF from '@/components/NotaVentaPDF.vue';
import axios from 'axios';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';
import { getVentas, getDetalleVenta } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { useToast } from 'primevue/usetoast';
import { generarReporteServicioPDF } from '@/services/reporteServicioPdfService.js';
import { useLoginStore } from '@/stores/loginStore';
import { registrarAbonoDinero, getMovimientosDineroPorReferencia } from '@/services/dineroService.js';
import { useRouter } from 'vue-router';
import NuevoReporteDeServicio from './NuevoReporteDeServicio.vue';

const API_URL = `${import.meta.env.VITE_API_URL}/reportes-servicio`;

const toast = useToast();
const loginStore = useLoginStore();
const router = useRouter();
const user = computed(() => loginStore.user || {});

const reportes = ref([]);
const loading = ref(false);

const showDialog = ref(false);
const showEditDialog = ref(false);
const reporteEditando = ref(null);

const showConfirmDeleteDialog = ref(false);
const reporteSeleccionado = ref(null);
const reporteAEliminar = ref(null);
const showComprobanteDialog = ref(false);
const archivoComprobante = ref(null);
const showNuevoReporteDialog = ref(false);

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
const xmlGenerado = ref('');
const pdfGenerado = ref('');

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
  firma_instalador: { label: 'Firma del instalador' },
  requiere_factura: { label: '¿Requiere factura?', type: 'select' }
};

const filtroCliente = ref('');
const filtroSO = ref('');
const filtroVendedor = ref('');
const filtroFecha = ref('');
const filtroTecnico = ref('');
const filtroIMEI = ref('');
const filtroPagado = ref('');

const reportesFiltrados = computed(() => {
  let lista = reportes.value;
  // Si es técnico y NO es admin, filtra solo sus reportes
  if (user.value && user.value.perfil === 'Tecnico') {
    lista = lista.filter(r => {
      return (
        (r.nombre_instalador && r.nombre_instalador.toLowerCase() === (user.value.username || '').toLowerCase())
      );
    });
  }
  // Admin ve todo, otros perfiles pueden tener lógica aquí si se requiere
  return lista.filter(r => {
      const clienteOk = !filtroCliente.value || (r.nombre_cliente && r.nombre_cliente.toLowerCase().includes(filtroCliente.value.toLowerCase()));
      const so = r.folio || obtenerSO(r);
      const soOk = !filtroSO.value || (so && so.toLowerCase().includes(filtroSO.value.toLowerCase()));
      const vendedorOk = !filtroVendedor.value || (r.vendedor && r.vendedor.toLowerCase().includes(filtroVendedor.value.toLowerCase()));
      const fechaOk = !filtroFecha.value || (r.fecha && r.fecha.includes(filtroFecha.value));
      const tecnicoOk = !filtroTecnico.value || (r.nombre_instalador && r.nombre_instalador.toLowerCase().includes(filtroTecnico.value.toLowerCase()));
      const imeiOk = !filtroIMEI.value || (r.imei && String(r.imei).toLowerCase().includes(filtroIMEI.value.toLowerCase()));
      const pagadoOk = filtroPagado.value === '' || r.pagado === filtroPagado.value;
      return clienteOk && soOk && vendedorOk && fechaOk && tecnicoOk && imeiOk && pagadoOk;
    });
});

async function cargarReportes() {
  loading.value = true;
  try {
    const res = await axios.get(`${API_URL}-todos`);
    reportes.value = res.data;
    asignaciones = await getAsignacionesTecnicos();
    const ventasGlobal = Array.isArray(window.ventasGlobal) ? window.ventasGlobal : await getVentas();
    const clientesGlobal = await getClientes();
    reportes.value = reportes.value.map(r => {
      const asignacion = asignaciones.find(a => a.id == r.asignacion_id);
      let folio = r.folio;
      let vendedor = r.vendedor;
      let nombre_cliente = r.nombre_cliente;
      let nombre_instalador = r.nombre_instalador;
      let monto_tecnico = r.monto_tecnico;
      let viaticos = r.viaticos;
      let total = r.total;
      let venta = null;
      if (asignacion && asignacion.venta_id && Array.isArray(ventasGlobal)) {
        venta = ventasGlobal.find(v => v.id == asignacion.venta_id);
        if (venta) {
          folio = venta.folio || (venta.id ? `SO-${String(venta.id).padStart(5, '0')}` : folio);
          vendedor = venta.vendedor || vendedor;
          const cliente = clientesGlobal.find(c => c.id === venta.cliente_id);
          if (cliente) {
            nombre_cliente = cliente.nombre;
          }
        }
        if (asignacion.tecnico) {
          nombre_instalador = asignacion.tecnico;
        }
      }
      return { ...r, folio, vendedor, nombre_cliente, nombre_instalador, monto_tecnico, viaticos, total };
    });
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

function confirmarEliminarReporte(reporte) {
  reporteAEliminar.value = reporte;
  showConfirmDeleteDialog.value = true;
}
async function eliminarReporteConfirmado() {
  if (!reporteAEliminar.value) return;
  loading.value = true;
  const reporteId = reporteAEliminar.value.id;
  let detalleReporte = null;
  // Obtener detalle antes de eliminar para saber qué IMEIs revertir
  try {
    const respDetalle = await axios.get(`${API_URL}/${reporteId}`);
    detalleReporte = respDetalle.data || null;
  } catch (e) {
    // Si falla, continuamos; intentaremos con los campos mínimos del listado
    detalleReporte = { imei: reporteAEliminar.value.imei, sim_serie: reporteAEliminar.value.sim_serie };
  }
  try {
    await axios.delete(`${API_URL}/${reporteId}`);
    // Eliminar movimiento de dinero relacionado (referencia por folio o id)
    try {
      const movimientos = await getMovimientosDineroPorReferencia(reporteAEliminar.value.folio || `ReporteServicio-${reporteId}`);
      if (Array.isArray(movimientos) && movimientos.length > 0) {
        for (const mov of movimientos) {
          await axios.delete(`${import.meta.env.VITE_API_URL}/movimientos-dinero/${mov.id}`);
        }
      }
    } catch (e) {
      console.error('Error eliminando movimientos dinero relacionados:', e);
    }
    // Revertir IMEIs a Disponible
    try {
      const imeisSet = new Set();
      if (detalleReporte?.imei) imeisSet.add(String(detalleReporte.imei).trim());
      if (detalleReporte?.sim_serie) imeisSet.add(String(detalleReporte.sim_serie).trim());
      if (Array.isArray(detalleReporte?.imeis_articulos)) {
        for (const li of detalleReporte.imeis_articulos) {
          if (Array.isArray(li.imeis)) {
            for (const im of li.imeis) if (im) imeisSet.add(String(im).trim());
          }
        }
      }
      // Evitar revertir strings vacíos o placeholders
      const imeisList = Array.from(imeisSet).filter(v => v && v !== '-' && v.toLowerCase() !== 'null');
      if (imeisList.length) {
        await Promise.all(imeisList.map(im => fetch(`${import.meta.env.VITE_API_URL}/imeis/${encodeURIComponent(im)}`, {
          method: 'PUT',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ status: 'Disponible' })
        }).catch(err => console.error('Error revertiendo IMEI', im, err))));
      }
    } catch (e) {
      console.error('Error revertiendo IMEIs a Disponible:', e);
    }
    await cargarReportes();
    toast.add({ severity: 'success', summary: 'Eliminado', detail: 'Reporte eliminado y IMEIs revertidos a Disponible.', life: 3000 });
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

    // Obtener detalle completo del reporte (para imeis_articulos, sim_series)
    let detalleReporte = null;
    try {
      const resp = await axios.get(`${API_URL}/${reporte.id}`);
      detalleReporte = resp.data || null;
    } catch (_) {
      detalleReporte = null;
    }

    const reporteCampos = {
      tipo_servicio: reporte.tipo_servicio,
      lugar_instalacion: reporte.lugar_instalacion,
      marca: reporte.marca,
      submarca: reporte.submarca,
      modelo: reporte.modelo,
      placas: reporte.placas,
      color: reporte.color,
      numero_economico: reporte.numero_economico,
      modelo_gps: reporte.modelo_gps,
      imei: reporte.imei,
      sim_serie: reporte.sim_serie,
      accesorios: reporte.accesorios,
      ubicacion_gps: reporte.ubicacion_gps,
      ubicacion_bloqueo: reporte.ubicacion_bloqueo,
      observaciones: reporte.observaciones,
      subtotal: reporte.subtotal,
      total: reporte.total,
      forma_pago: reporte.forma_pago,
      monto_tecnico: reporte.monto_tecnico,
      viaticos: reporte.viaticos,
      pagado: reporte.pagado,
      nombre_cliente: reporte.nombre_cliente,
      nombre_instalador: reporte.nombre_instalador,
      // NUEVO: estructuras N
      imeis_articulos: detalleReporte?.imeis_articulos || reporte.imeis_articulos || [],
      sim_series: detalleReporte?.sim_series || reporte.sim_series || []
    };
    await generarReporteServicioPDF({
      reporte: reporteCampos,
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
    if (venta) {
      return venta.folio || (venta.id ? `SO-${String(venta.id).padStart(5, '0')}` : '-');
    }
  }
  return '-';
}

// Carga ventas globalmente para acceso rápido en la tabla
onMounted(async () => {
  window.ventasGlobal = await getVentas();
  const clientesGlobal = await getClientes();
  asignaciones = await getAsignacionesTecnicos();
  await cargarReportes();
  // Mapea folio, vendedor, nombre_cliente y nombre_instalador a cada reporte
  reportes.value = reportes.value.map(r => {
    let folio = r.folio;
    let vendedor = r.vendedor;
    let nombre_cliente = r.nombre_cliente;
    let nombre_instalador = r.nombre_instalador;
    // Mantén los valores originales, no los fuerces a string
    let monto_tecnico = r.monto_tecnico;
    let viaticos = r.viaticos;
    let total = r.total;
    // Busca la asignación y la venta asociada
    const asignacion = asignaciones.find(a => a.id == r.asignacion_id);
    let venta = null;
    if (asignacion && asignacion.venta_id && Array.isArray(window.ventasGlobal)) {
      venta = window.ventasGlobal.find(v => v.id == asignacion.venta_id);
      if (venta) {
        folio = venta.folio || (venta.id ? `SO-${String(venta.id).padStart(5, '0')}` : folio);
        vendedor = venta.vendedor || vendedor;
        // Busca el cliente
        const cliente = clientesGlobal.find(c => c.id === venta.cliente_id);
        if (cliente) {
          nombre_cliente = cliente.nombre;
        }
      }
      // Busca el técnico
      if (asignacion.tecnico) {
        nombre_instalador = asignacion.tecnico;
      }
    }
    return { ...r, folio, vendedor, nombre_cliente, nombre_instalador, monto_tecnico, viaticos, total };
  });
});

function marcarComoPagado(reporte) {
  reporteSeleccionado.value = reporte;
  archivoComprobante.value = null;
  showComprobanteDialog.value = true;
}

function onComprobanteChange(event) {
  const files = event?.target?.files;
  archivoComprobante.value = files && files.length ? files[0] : null;
}

async function confirmarPagadoConComprobante() {
  if (!archivoComprobante.value || !reporteSeleccionado.value) {
    return toast.add({ severity: 'warn', summary: 'Falta comprobante', detail: 'Debes cargar un comprobante.', life: 3000 });
  }
  loading.value = true;
  try {
    // 1) Subir archivo a backend
    const fd = new FormData();
    fd.append('archivo', archivoComprobante.value);
    await axios.post(`${API_URL}/${reporteSeleccionado.value.id}/comprobante`, fd, {
      headers: { 'Content-Type': 'multipart/form-data' }
    });
    // 2) No marcamos pagado aún. Queda en revisión.
    await axios.put(`${API_URL}/${reporteSeleccionado.value.id}`, { comprobante_estado: 'pendiente' });
    await cargarReportes();
    toast.add({ severity: 'success', summary: 'En revisión', detail: 'Comprobante enviado. Pendiente de aprobación.', life: 3000 });
    showComprobanteDialog.value = false;
    archivoComprobante.value = null;
    reporteSeleccionado.value = null;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo subir el comprobante.', life: 4000 });
  }
  loading.value = false;
}

function cancelarComprobante() {
  showComprobanteDialog.value = false;
  archivoComprobante.value = null;
}

async function aprobarComprobante(reporte) {
  if (user.value?.perfil !== 'Admin') {
    return toast.add({ severity: 'warn', summary: 'Permiso', detail: 'Solo Admin puede aprobar.', life: 3000 });
  }
  loading.value = true;
  try {
    const token = localStorage.getItem('access_token') || '';
    await axios.put(`${API_URL}/${reporte.id}/aprobar-comprobante`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    // Registrar movimiento de dinero al aprobar
    await registrarAbonoDinero({
      fecha: new Date().toISOString().slice(0, 19).replace('T', ' '),
      tipo: 'Ingreso',
      concepto: `Servicio: ${reporte.tipo_servicio || ''}`,
      monto: Number(reporte.total) || 0,
      referencia: reporte.folio || `ReporteServicio-${reporte.id}`
    });
    await cargarReportes();
    toast.add({ severity: 'success', summary: 'Aprobado', detail: 'Comprobante aprobado. Reporte pagado.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo aprobar el comprobante.', life: 4000 });
  }
  loading.value = false;
}

// Nueva función para facturar
async function facturarReporte(reporte) {
  loading.value = true;
  try {
    // Construir el objeto factura usando datos del reporte y sugerencias si faltan
    const factura = {
      nombre_cliente: reporte.nombre_cliente || 'Público en General',
      rfc_cliente: reporte.rfc_cliente || 'XAXX010101000',
      uso_cfdi: reporte.uso_cfdi || 'G03',
      productos: Array.isArray(reporte.productos) && reporte.productos.length > 0
        ? reporte.productos.map(p => ({
            ClaveProdServ: p.ClaveProdServ || '81112100',
            ClaveUnidad: p.ClaveUnidad || 'E48',
            Unidad: p.Unidad || 'Servicio',
            Descripcion: p.Descripcion || 'Servicio de reinstalación GPS',
            ValorUnitario: Number(p.ValorUnitario) || Number(reporte.total) || 100.0,
            Importe: Number(p.Importe) || Number(reporte.total) || 100.0,
            Cantidad: Number(p.Cantidad) || 1
          }))
        : [{
            ClaveProdServ: '81112100',
            ClaveUnidad: 'E48',
            Unidad: 'Servicio',
            Descripcion: reporte.tipo_servicio || 'Servicio de reinstalación GPS',
            ValorUnitario: Number(reporte.total) || 100.0,
            Importe: Number(reporte.total) || 100.0,
            Cantidad: 1
          }],
      metodo_pago: reporte.metodo_pago || 'PUE',
      forma_pago: reporte.forma_pago || '01',
      total: Number(reporte.total) || 100.0
    };
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/facturar`, factura);
    toast.add({ severity: 'success', summary: 'XML/PDF generado', detail: 'Factura generada correctamente.', life: 3000 });
    xmlGenerado.value = response.data.cfdi_xml;
    pdfGenerado.value = response.data.cfdi_pdf || '';
    messageDialogText.value = '';
    showMessageDialog.value = true;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al facturar.', life: 4000 });
    messageDialogText.value = 'Error al facturar.';
    showMessageDialog.value = true;
  }
  loading.value = false;
}

function descargarXML() {
  const blob = new Blob([xmlGenerado.value], { type: 'application/xml' });
  const link = document.createElement('a');
  link.href = URL.createObjectURL(blob);
  let filename = 'factura';
  if (reporteSeleccionado.value) {
    const folio = obtenerSO(reporteSeleccionado.value);
    if (folio && folio !== '-') filename = folio.replace(/\s/g, '');
  }
  link.download = `${filename}.xml`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

function descargarPDF() {
  if (!pdfGenerado.value) return;
  let byteCharacters = atob(pdfGenerado.value);
  let byteNumbers = new Array(byteCharacters.length);
  for (let i = 0; i < byteCharacters.length; i++) {
    byteNumbers[i] = byteCharacters.charCodeAt(i);
  }
  let byteArray = new Uint8Array(byteNumbers);
  const blob = new Blob([byteArray], { type: 'application/pdf' });
  const link = document.createElement('a');
  let filename = 'factura';
  if (reporteSeleccionado.value) {
    const folio = obtenerSO(reporteSeleccionado.value);
    if (folio && folio !== '-') filename = folio.replace(/\s/g, '');
  }
  link.href = URL.createObjectURL(blob);
  link.download = `${filename}.pdf`;
  document.body.appendChild(link);
  link.click();
  document.body.removeChild(link);
}

// Factura - Nueva lógica
const showFacturaDialog = ref(false);
const facturaData = ref({
  nombre_cliente: '',
  rfc_cliente: '',
  uso_cfdi: '',
  metodo_pago: '',
  forma_pago: '',
  total: '',
  productos: [{
    ClaveProdServ: '',
    ClaveUnidad: '',
    Unidad: '',
    Descripcion: '',
    ValorUnitario: '',
    Importe: '',
    Cantidad: 1
  }]
});

async function abrirFacturaDialog(reporte) {
  reporteSeleccionado.value = reporte;
  let venta = null;
  let cliente = null;
  if (reporte.asignacion_id) {
    const asignacion = asignaciones.find(a => a.id == reporte.asignacion_id);
    if (asignacion && asignacion.venta_id) {
      const ventas = await getVentas();
      venta = ventas.find(v => v.id == asignacion.venta_id);
      const clientes = await getClientes();
      cliente = venta ? (clientes.find(c => c.id === venta.cliente_id) || {}) : {};
    }
  }
  facturaData.value = {
    nombre_cliente: reporte.nombre_cliente || cliente?.nombre || 'Público en General',
    rfc_cliente: reporte.rfc_cliente || cliente?.rfc || 'XAXX010101000',
    uso_cfdi: reporte.uso_cfdi || cliente?.uso_cfdi || 'G03',
    metodo_pago: reporte.metodo_pago || venta?.metodo_pago || 'PUE',
    forma_pago: reporte.forma_pago || venta?.forma_pago || '01',
    total: reporte.total || venta?.total || 100.0,
    nombre_factura: reporte.tipo_servicio || 'Servicio',
    productos: Array.isArray(reporte.productos) && reporte.productos.length > 0
      ? reporte.productos.map(p => ({
          ClaveProdServ: p.ClaveProdServ || '81112100',
          ClaveUnidad: p.ClaveUnidad || 'E48',
          Unidad: p.Unidad || 'Servicio',
          Descripcion: p.Descripcion || reporte.tipo_servicio || 'Servicio de reinstalación GPS',
          ValorUnitario: p.ValorUnitario || reporte.total || venta?.total || 100.0,
          Importe: p.Importe || reporte.total || venta?.total || 100.0,
          Cantidad: p.Cantidad || 1
        }))
      : [{
          ClaveProdServ: '81112100',
          ClaveUnidad: 'E48',
          Unidad: 'Servicio',
          Descripcion: reporte.tipo_servicio || 'Servicio de reinstalación GPS',
          ValorUnitario: reporte.total || venta?.total || 100.0,
          Importe: reporte.total || venta?.total || 100.0,
          Cantidad: 1
        }]
  };
  showFacturaDialog.value = true;
}

async function enviarFactura() {
  loading.value = true;
  try {
    const response = await axios.post(`${import.meta.env.VITE_API_URL}/api/facturar`, {
      ...facturaData.value,
      total: Number(facturaData.value.total)
    });
    toast.add({ severity: 'success', summary: 'XML/PDF generado', detail: 'Factura generada correctamente.', life: 3000 });
    xmlGenerado.value = response.data.cfdi_xml;
    pdfGenerado.value = response.data.cfdi_pdf || '';
    messageDialogText.value = '';
    showMessageDialog.value = true;
    showFacturaDialog.value = false;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al facturar.', life: 4000 });
    messageDialogText.value = 'Error al facturar.';
    showMessageDialog.value = true;
  }
  loading.value = false;
}

function urlComprobante(reporte) {
  if (!reporte?.comprobante_path) return '#';
  const base = import.meta.env.VITE_API_URL?.replace(/\/$/, '') || '';
  const path = reporte.comprobante_path.startsWith('/') ? reporte.comprobante_path : `/${reporte.comprobante_path}`;
  return `${base}${path}`;
}

async function rechazarComprobante(reporte) {
  if (!(user.value && user.value.perfil === 'Admin')) {
    return toast.add({ severity: 'warn', summary: 'Permiso', detail: 'Solo Admin puede rechazar.', life: 3000 });
  }
  loading.value = true;
  try {
    const token = localStorage.getItem('access_token') || '';
    await axios.put(`${API_URL}/${reporte.id}/rechazar-comprobante`, {}, {
      headers: { Authorization: `Bearer ${token}` }
    });
    await cargarReportes();
    toast.add({ severity: 'success', summary: 'Rechazado', detail: 'Comprobante rechazado.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo rechazar el comprobante.', life: 4000 });
  }
  loading.value = false;
}

// Función para agregar reporte de servicio global (sin datos previos)
function irReporteServicioGlobal() {
  router.push({ path: '/nuevo-reporte-servicio' });
}
</script>

<style scoped>
.consultar-reportes-container {
  margin: 2rem auto;
  text-align: center;
  /* background: #23272f; */
  border-radius: 12px;
  /* box-shadow: 0 4px 24px rgba(0,0,0,0.10); */
  /* color: #e4c8c8; */
  padding: 2rem 1.5rem;
}
.consultar-reportes-title {
  margin-bottom: 2rem;
  /* color: #e4c8c8; */
}
.historico-dialog :deep(.p-dialog-content) {
  /* background: var(--color-card, #23272f); */
  padding: 1.5rem 1rem;
  border-radius: 12px;
}
.historico-dialog :deep(.p-dialog-header) {
  /* background: var(--color-bg, #23272f); */
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
.filtro-input {
  flex: 1;
  min-width: 150px;
  /* background: #2c2f3e; */
  color: #e4c8c8;
  /* border: 1px solid #444851; */
  border-radius: 8px;
  padding: 0.5rem 1rem;
}
</style>