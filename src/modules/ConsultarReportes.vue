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
      <InputText v-model="filtroSimSerie" placeholder="Filtrar por SIM Serie" class="filtro-input" clearable />
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
    <DataTable 
      :value="reportesFiltrados" 
      responsiveLayout="scroll" 
      :loading="loading"
      :paginator="true"
      :rows="10"
      :rowsPerPageOptions="[5, 10, 20, 50]"
      paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink RowsPerPageDropdown"
      currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords} reportes"
    >
      <template #loading>
        <DataTableLoader text="Cargando reportes..." />
      </template>
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
import DataTableLoader from '@/components/DataTableLoader.vue';
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


const empresa = {
  nombre: 'COMERCIALIZADORA TECNOLOGICA DEL RIO',
  direccion: 'Fresno 1441 44910 Guadalajara, Jalisco, México',
  rfc: 'CTR1905206K5',
  regimen: '626 - Régimen Simplificado de Confianza',
  telefono: '3325373183',
  correo: 'gpsvector@gmail.com',
  web: 'gpsubicacion.com',
  logoBase64: 'data:image/svg+xml;base64,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' // Puedes agregar un logo en base64 si lo deseas
};
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

// Cachear datos para evitar peticiones duplicadas
let asignaciones = [];
let ventasCache = [];
let clientesCache = [];

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
const filtroSimSerie = ref('');
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
      const simSerieOk = !filtroSimSerie.value || (r.sim_serie && String(r.sim_serie).toLowerCase().includes(filtroSimSerie.value.toLowerCase()));
      const pagadoOk = filtroPagado.value === '' || r.pagado === filtroPagado.value;
      return clienteOk && soOk && vendedorOk && fechaOk && tecnicoOk && imeiOk && simSerieOk && pagadoOk;
    });
});

// Función para mapear reportes con datos de ventas, clientes y asignaciones
function mapearReportes(reportesData, ventasData, clientesData, asignacionesData) {
  return reportesData.map(r => {
    const asignacion = asignacionesData.find(a => a.id == r.asignacion_id);
    let folio = r.folio;
    let vendedor = r.vendedor;
    let nombre_cliente = r.nombre_cliente;
    let nombre_instalador = r.nombre_instalador;
    let monto_tecnico = r.monto_tecnico;
    let viaticos = r.viaticos;
    let total = r.total;
    let venta = null;
    if (asignacion && asignacion.venta_id && Array.isArray(ventasData)) {
      venta = ventasData.find(v => v.id == asignacion.venta_id);
      if (venta) {
        folio = venta.folio || (venta.id ? `SO-${String(venta.id).padStart(5, '0')}` : folio);
        vendedor = venta.vendedor || vendedor;
        const cliente = clientesData.find(c => c.id === venta.cliente_id);
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
}

async function cargarReportes(forceReload = false) {
  loading.value = true;
  try {
    // Cargar reportes
    const res = await axios.get(`${API_URL}-todos`);
    
    // Solo recargar datos auxiliares si es necesario o si forceReload
    if (forceReload || asignaciones.length === 0) {
      asignaciones = await getAsignacionesTecnicos();
    }
    if (forceReload || ventasCache.length === 0) {
      ventasCache = await getVentas();
      window.ventasGlobal = ventasCache;
    }
    if (forceReload || clientesCache.length === 0) {
      clientesCache = await getClientes();
    }
    
    // Mapear reportes con datos cacheados
    reportes.value = mapearReportes(res.data, ventasCache, clientesCache, asignaciones);
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
  // Usar datos cacheados
  const venta = ventasCache.find(v => v.id == asignacion.venta_id);
  if (!venta) {
    loading.value = false;
    toast.add({ severity: 'warn', summary: 'No encontrada', detail: 'No se encontró la nota de venta.', life: 4000 });
    messageDialogText.value = 'No se encontró la nota de venta.';
    showMessageDialog.value = true;
    return;
  }
  ventaSeleccionada.value = venta;
  clienteSeleccionado.value = clientesCache.find(c => c.id === venta.cliente_id) || {};
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
    // Usar datos cacheados
    const venta = ventasCache.find(v => v.id == asignacion.venta_id);
    if (!venta) {
      loading.value = false;
      toast.add({ severity: 'warn', summary: 'No encontrada', detail: 'No se encontró la nota de venta.', life: 4000 });
      messageDialogText.value = 'No se encontró la nota de venta.';
      showMessageDialog.value = true;
      return;
    }
    const cliente = clientesCache.find(c => c.id === venta.cliente_id) || {};
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

async function descargarReporteServicio(reporte, empresa) {
  loading.value = true;
  try {
    // Usar el PDF profesional del archivo de servicios
    let detalleReporte = null;
    let venta = null;
    let cliente = null;
    try {
      const resp = await axios.get(`${API_URL}/${reporte.id}`);
      detalleReporte = resp.data || null;
    } catch (_) {
      detalleReporte = null;
    }
    // Buscar venta y cliente si hay asignación - usar datos cacheados
    const asignacion = asignaciones.find(a => a.id == reporte.asignacion_id);
    if (asignacion && asignacion.venta_id) {
      venta = ventasCache.find(v => v.id == asignacion.venta_id);
      cliente = venta ? (clientesCache.find(c => c.id === venta.cliente_id) || {}) : {};
    }
    // Unir campos relevantes
    const reporteCampos = {
      ...reporte,
      ...detalleReporte
    };
    // Importar la función profesional
    const { generarReporteServicioPDF } = await import('@/components/GeneraReporteServicioPDF.js');
    generarReporteServicioPDF({ reporte: reporteCampos, empresa });
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

// Carga inicial de datos - todo en una sola función para evitar duplicaciones
onMounted(async () => {
  await cargarReportes(true); // forceReload=true para cargar todo la primera vez
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
      // Usar datos cacheados en lugar de hacer nuevas peticiones
      venta = ventasCache.find(v => v.id == asignacion.venta_id);
      cliente = venta ? (clientesCache.find(c => c.id === venta.cliente_id) || {}) : {};
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