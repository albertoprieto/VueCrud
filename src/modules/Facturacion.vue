<template>
  <div class="fact-container">
    <h2 class="fact-title"><i class="pi pi-receipt" /> Facturación</h2>

    <div class="fact-nueva-bar">
      <Button label="Sincronizar comprobantes" icon="pi pi-sync" class="p-button-sm p-button-outlined" :loading="sincronizandoTodas" @click="sincronizarTodasComprobantes" />
      <Button label="Exportar Excel" icon="pi pi-file-excel" class="p-button-sm p-button-outlined p-button-success" :disabled="!facturasFiltradas.length" @click="exportarExcel" />
      <Button label="Nueva Prefactura" icon="pi pi-plus" class="p-button-sm" @click="abrirNuevaFactura" />
    </div>

    <div class="fact-toolbar">
      <div class="fact-search">
        <i class="pi pi-search" />
        <InputText v-model="filtroCliente" placeholder="Buscar por cliente..." />
      </div>
      <div class="fact-search">
        <i class="pi pi-hashtag" />
        <InputText v-model="filtroOrden" placeholder="Buscar por orden..." />
      </div>
      <div class="fact-search">
        <i class="pi pi-mobile" />
        <InputText v-model="filtroImei" placeholder="Buscar por IMEI..." />
      </div>
      <div class="fact-search">
        <i class="pi pi-wrench" />
        <InputText v-model="filtroInstalador" placeholder="Buscar por instalador..." />
      </div>
      <div class="fact-search">
        <i class="pi pi-user" />
        <InputText v-model="filtroVendedor" placeholder="Buscar por vendedor..." />
      </div>
      <Dropdown
        v-model="filtroLugarPago"
        :options="lugaresPago"
        placeholder="Pagado en"
        showClear
        class="fact-dropdown"
      />
      <Calendar
        v-model="mesFiltro"
        view="month"
        dateFormat="mm/yy"
        placeholder="Todos los meses"
        showIcon
        iconDisplay="input"
        showButtonBar
        class="fact-dropdown"
      />
      <div class="filtro-estado">
        <button
          v-for="op in opcionesEstado"
          :key="op.value"
          type="button"
          class="estado-chip"
          :class="{ activo: filtroEstado === op.value }"
          @click="filtroEstado = op.value"
        >
          {{ op.label }}
          <span class="estado-chip-count">{{ contarPorEstado(op.value) }}</span>
        </button>
      </div>
      <div class="filtro-estado">
        <button
          v-for="op in opcionesPago"
          :key="op.value"
          type="button"
          class="estado-chip"
          :class="{ activo: filtroPago === op.value }"
          @click="filtroPago = op.value"
        >
          {{ op.label }}
          <span class="estado-chip-count">{{ contarPorPago(op.value) }}</span>
        </button>
      </div>
    </div>
    <p class="fact-mes-aviso">
      <i class="pi pi-info-circle" /> El filtro de mes solo aplica a facturas ya timbradas/canceladas — las prefacturas pendientes de timbrar siempre se muestran, sin importar su fecha.
    </p>

    <div class="fact-table-card">
      <DataTable
        v-if="!isMobile"
        :value="facturasFiltradas"
        responsiveLayout="scroll"
        :loading="loading"
        :paginator="facturasFiltradas.length > 100"
        :rows="100"
        size="small"
      >
        <template #loading><DataTableLoader text="Cargando facturas..." /></template>
        <Column header="Fecha">
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column header="Antigüedad">
          <template #body="{ data }">
            <span v-if="data.status === 'Pendiente timbre'" class="antiguedad-pill" :class="claseAntiguedad(data.fecha)">
              {{ diasPendiente(data.fecha) }} día{{ diasPendiente(data.fecha) === 1 ? '' : 's' }}
            </span>
            <span v-else class="celda-vacia">—</span>
          </template>
        </Column>
        <Column field="cliente" header="Cliente" />
        <Column header="Órdenes">
          <template #body="{ data }">{{ (data.ordenes || []).join(', ') || '—' }}</template>
        </Column>
        <Column header="IMEIs">
          <template #body="{ data }">{{ getImeisUnicos(data).join(', ') || '—' }}</template>
        </Column>
        <Column header="Total">
          <template #body="{ data }"><span class="celda-total">{{ formatTotal(data.total) }}</span></template>
        </Column>
        <Column header="Timbre" style="text-align:center;">
          <template #body="{ data }">
            <span v-if="data.status === 'Cancelado'" class="texto-cancelada">🟠 Cancelada</span>
            <span v-else-if="data.status === 'Timbrado'" class="emoji-check" title="Timbrada">✅</span>
            <span v-else class="emoji-cross" title="Pendiente de timbrar">❌</span>
          </template>
        </Column>
        <Column header="Pago" style="text-align:center;">
          <template #body="{ data }">
            <span v-if="data.pagado" class="emoji-check" title="Pagada">✅</span>
            <span v-else class="emoji-cross" title="Pendiente de pago">❌</span>
          </template>
        </Column>
        <Column header="Comprobante" style="text-align:center;">
          <template #body="{ data }">
            <div v-if="data.comprobantes && data.comprobantes.length" style="display:flex;justify-content:center;gap:0.4rem;">
              <a
                v-for="(comp, idx) in data.comprobantes" :key="idx"
                href="#" @click.prevent="abrirArchivoCfdi(comp)"
                :title="nombreArchivoComprobante(comp)"
              ><i class="pi pi-image comprobante-icono"></i></a>
            </div>
            <span v-else class="celda-vacia">—</span>
          </template>
        </Column>
        <Column header="Acciones" style="width:280px">
          <template #body="{ data }">
            <div style="display:flex;gap:0.5rem;flex-wrap:wrap;">
              <Button
                v-if="data.status === 'Pendiente timbre'"
                icon="pi pi-verified" label="Timbrar"
                class="p-button-sm p-button-success"
                @click="irDetalle(data.id)"
              />
              <Button v-else icon="pi pi-eye" label="Detalle" class="p-button-sm p-button-info" @click="irDetalle(data.id)" />
              <Button
                v-if="data.status === 'Timbrado' && data.cfdi_pdf_path"
                icon="pi pi-file-pdf" label="PDF"
                class="p-button-sm p-button-outlined"
                @click="abrirArchivoCfdi(data.cfdi_pdf_path)"
              />
              <Button
                v-if="data.status === 'Timbrado' && data.cfdi_xml_path"
                icon="pi pi-file" label="XML"
                class="p-button-sm p-button-outlined"
                @click="abrirArchivoCfdi(data.cfdi_xml_path)"
              />
              <Button
                v-if="data.status === 'Pendiente timbre'"
                icon="pi pi-file-pdf" label="Prefactura"
                class="p-button-sm p-button-outlined p-button-warning"
                :loading="generandoPrefacturaId === data.id"
                @click="abrirPrefactura(data)"
              />
              <Button
                icon="pi pi-trash" class="p-button-sm p-button-danger p-button-outlined"
                v-if="data.status === 'Pendiente timbre'"
                @click="confirmarEliminar(data)"
              />
            </div>
          </template>
        </Column>
      </DataTable>

      <div v-else class="mobile-list-wrap">
        <div v-if="loading" class="mobile-loader-wrap"><DataTableLoader text="Cargando facturas..." /></div>
        <div v-else-if="!facturasFiltradas.length" class="mobile-empty">No hay facturas para mostrar.</div>
        <div v-else class="mobile-cards">
          <article v-for="item in facturasFiltradas" :key="item.id" class="mobile-card" @click="irDetalle(item.id)">
            <header class="mobile-card-header">
              <div>
                <p class="mobile-card-id">Factura #{{ item.id }}</p>
                <p class="mobile-card-cliente">{{ item.cliente || 'Sin cliente' }}</p>
              </div>
              <div style="display:flex;flex-direction:column;gap:0.3rem;align-items:flex-end;">
                <span :class="'badge badge-' + badgeClass(item.status)">{{ item.status }}</span>
                <span :class="'badge badge-' + (item.pagado ? 'success' : 'warning')">{{ item.pagado ? 'Pagada' : 'Pendiente pago' }}</span>
              </div>
            </header>
            <div class="mobile-card-grid">
              <div class="mobile-field"><span class="mobile-label">Total</span><span class="mobile-value">{{ formatTotal(item.total) }}</span></div>
              <div class="mobile-field"><span class="mobile-label">Fecha</span><span class="mobile-value">{{ formatFecha(item.fecha) }}</span></div>
              <div class="mobile-field mobile-field-full"><span class="mobile-label">IMEIs</span><span class="mobile-value">{{ getImeisUnicos(item).join(', ') || '—' }}</span></div>
              <div v-if="item.status === 'Pendiente timbre'" class="mobile-field">
                <span class="mobile-label">Antigüedad</span>
                <span class="antiguedad-pill" :class="claseAntiguedad(item.fecha)">{{ diasPendiente(item.fecha) }} día{{ diasPendiente(item.fecha) === 1 ? '' : 's' }}</span>
              </div>
            </div>
          </article>
        </div>
      </div>
    </div>

    <Dialog v-model:visible="prefacturaPdfVisible" header="Prefactura (borrador sin timbrar)" :modal="true" :style="{ width: '85vw' }" :draggable="false">
      <iframe v-if="prefacturaPdfUrl" :src="prefacturaPdfUrl" style="width:100%;height:80vh;border:none;" />
    </Dialog>

    <Dialog v-model:visible="showConfirmDelete" header="Eliminar prefactura" :modal="true" :closable="false">
      <div style="padding:1rem;text-align:center;">
        <span>¿Eliminar esta prefactura? Los reportes de servicio quedarán libres para agregarse a otra.</span>
      </div>
      <div style="display:flex;gap:1rem;justify-content:center;padding-bottom:1rem;">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" :loading="eliminando" @click="ejecutarEliminar" />
        <Button label="Cancelar" class="p-button-secondary" @click="showConfirmDelete = false" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showNuevaDialog" header="Nueva prefactura" :modal="true" :closable="false" class="nueva-fact-dialog" style="width: 760px; max-width: 96vw;">
      <div class="nueva-fact-form">
        <div class="form-group">
          <label>Cliente</label>
          <InputText v-model="nuevaCliente" class="w-full" placeholder="Nombre del cliente (existente o nuevo)" />
          <small style="color:var(--color-text);opacity:0.7;">
            Si el cliente no existe aún, se dará de alta con sus datos fiscales al momento de timbrar. Los reportes de servicio se ligan después, desde el detalle de la prefactura.
          </small>
        </div>

        <div class="form-group">
          <label>Artículos en existencia (opcional) — descuenta stock y marca el IMEI como vendido</label>
          <div class="articulo-pick-row">
            <Dropdown
              v-model="ubicacionSeleccionada"
              :options="ubicaciones"
              optionLabel="nombre"
              filter
              placeholder="Selecciona una bodega/ubicación..."
              class="w-full"
              @change="onUbicacionSeleccionada"
            />
          </div>
          <InputText
            v-if="ubicacionSeleccionada"
            v-model="busquedaArticuloImei"
            class="w-full"
            style="margin-top:0.5rem;"
            placeholder="Buscar por artículo, SKU o IMEI..."
          />
          <div v-if="ubicacionSeleccionada" class="reportes-pick-list">
            <div v-if="cargandoImeisUbicacion" style="padding:0.75rem;text-align:center;"><i class="pi pi-spin pi-spinner" /></div>
            <div v-else-if="!imeisDisponiblesFiltrados.length" class="reportes-pick-empty">Sin IMEIs disponibles en esta ubicación.</div>
            <label v-for="im in imeisDisponiblesFiltrados" :key="im.imei" class="reportes-pick-item">
              <input type="checkbox" :checked="false" @change="agregarArticuloVendido(im, $event.target.checked)" />
              <span>{{ im.articulo_nombre || im.sku || 'Artículo' }} — IMEI {{ im.imei }} — {{ formatTotal(precioDeArticulo(im.articulo_nombre)) }}</span>
            </label>
          </div>
          <div v-if="articulosVendidos.length" class="articulos-vendidos-lista">
            <div v-for="(a, idx) in articulosVendidos" :key="a.imei" class="articulo-vendido-item">
              <span>{{ a.articulo_nombre }} — IMEI {{ a.imei }} — {{ formatTotal(a.precioVenta) }}</span>
              <Button icon="pi pi-times" class="p-button-sm p-button-danger p-button-text" @click="quitarArticuloVendido(idx)" />
            </div>
          </div>
        </div>

        <div class="form-group">
          <label>Productos / conceptos manuales (requerido si no hay artículos ligados)</label>
          <div v-for="(prod, idx) in productosManuales" :key="idx" class="producto-manual-row">
            <InputText v-model="prod.Descripcion" placeholder="Descripción" class="producto-desc" />
            <InputNumber v-model="prod.ValorUnitario" placeholder="Precio unitario" mode="currency" currency="MXN" locale="es-MX" class="producto-precio" />
            <InputNumber v-model="prod.Cantidad" placeholder="Cant." :min="1" class="producto-cant" />
            <InputText v-model="prod.ClaveProdServ" placeholder="Clave SAT (ej. 81112501)" class="producto-clave" />
            <Button icon="pi pi-trash" class="p-button-sm p-button-danger p-button-text" @click="quitarProductoManual(idx)" v-if="productosManuales.length > 1" />
          </div>
          <Button icon="pi pi-plus" label="Agregar concepto" class="p-button-sm p-button-text" @click="agregarProductoManual" />
        </div>

        <div class="form-group">
          <label>Total</label>
          <InputNumber v-model="nuevaTotal" class="w-full" mode="currency" currency="MXN" locale="es-MX" />
        </div>

        <div class="form-group">
          <label class="pago-toggle-label">
            <input type="checkbox" v-model="nuevaPagada" />
            Ya está pagada
          </label>
          <small style="color:var(--color-text);opacity:0.7;">
            Si no la marcas, la factura queda como "Pendiente pago" (independiente de si ya está timbrada o no).
          </small>
        </div>
      </div>
      <template #footer>
        <div class="modal-actions">
          <Button label="Cancelar" class="p-button-secondary" @click="showNuevaDialog = false" />
          <Button label="Generar prefactura" icon="pi pi-check" :loading="creandoFactura" @click="confirmarNuevaFactura" />
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import * as XLSX from 'xlsx';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import DataTableLoader from '@/components/DataTableLoader.vue';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import { getFacturas, eliminarFactura, crearFactura, generarPrefacturaFactura, getPrefacturaPdfUrl, sincronizarComprobantesTodas } from '@/services/pagosService';
import { getTodosArticulos, sincronizarStockArticulos } from '@/services/articulosService';
import { updateIMEI } from '@/services/imeiService';
import { getUbicaciones, getImeisPorUbicacion } from '@/services/ubicacionesService';
import { getClientes } from '@/services/clientesService';

const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');
const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');
function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  const encoded = p.split('/').map(seg => encodeURIComponent(seg)).join('/');
  return `${API_URL}${encoded}`;
}
function abrirArchivoCfdi(path) { if (path) window.open(urlComprobante(path), '_blank', 'noopener'); }
function nombreArchivoComprobante(path) { return path ? decodeURIComponent(path.split('/').pop()) : 'comprobante'; }

const facturas = ref([]);
const loading = ref(true);
const isMobile = ref(false);
const filtroCliente = ref('');
const filtroOrden = ref('');
const filtroImei = ref('');
const filtroInstalador = ref('');
const filtroVendedor = ref('');
const filtroLugarPago = ref('');
const filtroEstado = ref('todos');
const filtroPago = ref('todos');
const mesFiltro = ref(null);

const lugaresPago = [
  'ASP Renovaciones',
  'Comercializadora',
  'BBVA PAU',
  'Tecnico',
  'Oficina',
  'Mercadopago'
];

const opcionesEstado = [
  { value: 'todos', label: 'Todas' },
  { value: 'Pendiente timbre', label: 'Pendientes' },
  { value: 'Timbrado', label: 'Timbradas' },
  { value: 'Cancelado', label: 'Canceladas' },
];

const opcionesPago = [
  { value: 'con_comprobante', label: 'Con comprobante' },
  { value: 'pagadas', label: 'Pagadas' },
  { value: 'pendientes', label: 'Pendiente pago' },
];

function contarPorEstado(valor) {
  if (valor === 'todos') return facturas.value.length;
  return facturas.value.filter(f => f.status === valor).length;
}

function contarPorPago(valor) {
  if (valor === 'con_comprobante') return facturas.value.filter(f => f.comprobantes && f.comprobantes.length).length;
  if (valor === 'pagadas') return facturas.value.filter(f => f.pagado).length;
  return facturas.value.filter(f => !f.pagado).length;
}

function getImeisUnicos(row) {
  const arr = (Array.isArray(row?.imeis) ? row.imeis : []).map(v => String(v).trim()).filter(Boolean);
  return Array.from(new Set(arr));
}

const facturasFiltradas = computed(() => {
  const cl = filtroCliente.value.trim().toLowerCase();
  const ord = filtroOrden.value.trim().toLowerCase();
  const imei = filtroImei.value.trim();
  const inst = filtroInstalador.value.trim().toLowerCase();
  const vend = filtroVendedor.value.trim().toLowerCase();
  return facturas.value.filter(f => {
    if (filtroEstado.value !== 'todos' && f.status !== filtroEstado.value) return false;
    if (cl && !(f.cliente || '').toLowerCase().includes(cl)) return false;
    if (ord && !(f.ordenes || []).some(o => String(o).toLowerCase().includes(ord))) return false;
    if (imei && !getImeisUnicos(f).some(im => im.includes(imei))) return false;
    if (inst && !(f.instalador || '').toLowerCase().includes(inst)) return false;
    if (vend && !(f.vendedor || '').toLowerCase().includes(vend)) return false;
    if (filtroLugarPago.value && (f.lugar_pago || '') !== filtroLugarPago.value) return false;
    if (filtroPago.value === 'con_comprobante' && !(f.comprobantes && f.comprobantes.length)) return false;
    if (filtroPago.value === 'pagadas' && !f.pagado) return false;
    if (filtroPago.value === 'pendientes' && f.pagado) return false;
    // El mes solo filtra facturas ya resueltas (Timbrado/Cancelado) — las
    // prefacturas pendientes de timbrar siempre se muestran, sin importar
    // qué tan viejas sean, para no perderlas de vista por accidente.
    if (mesFiltro.value && f.status !== 'Pendiente timbre') {
      const fecha = f.fecha ? new Date(f.fecha) : null;
      const mismoMes = fecha
        && fecha.getMonth() === mesFiltro.value.getMonth()
        && fecha.getFullYear() === mesFiltro.value.getFullYear();
      if (!mismoMes) return false;
    }
    return true;
  });
});

const formatoMoneda = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2 });
function formatTotal(v) { return v != null ? formatoMoneda.format(Number(v)) : '-'; }
function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}
function badgeClass(status) {
  if (status === 'Timbrado') return 'success';
  if (status === 'Cancelado') return 'danger';
  return 'warning';
}

function irDetalle(id) {
  router.push({ name: 'detalle-factura', params: { id } });
}

function timbreTexto(status) {
  if (status === 'Timbrado') return 'Timbrada';
  if (status === 'Cancelado') return 'Cancelada';
  return 'Pendiente';
}

function stamp() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  return `${y}${m}${day}_${hh}${mm}`;
}

const sincronizandoTodas = ref(false);
async function sincronizarTodasComprobantes() {
  sincronizandoTodas.value = true;
  try {
    const res = await sincronizarComprobantesTodas();
    toast.add({
      severity: 'success', summary: 'Sincronización completada',
      detail: `${res.facturas_actualizadas} prefactura(s) actualizadas, ${res.comprobantes_agregados} comprobante(s) agregados.`,
      life: 5000
    });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo sincronizar.', life: 4000 });
  }
  sincronizandoTodas.value = false;
}

function exportarExcel() {
  if (!facturasFiltradas.value.length) return;

  const filas = facturasFiltradas.value.map(f => ({
    Fecha: formatFecha(f.fecha),
    Antigüedad: f.status === 'Pendiente timbre' ? `${diasPendiente(f.fecha)} día(s)` : '',
    Cliente: f.cliente || '',
    Órdenes: (f.ordenes || []).join(', '),
    IMEIs: getImeisUnicos(f).join(', '),
    Total: Number(f.total) || 0,
    Timbre: timbreTexto(f.status),
    Pago: f.pagado ? 'Pagada' : 'Pendiente de pago',
    'Lugar de pago': f.lugar_pago || '',
  }));

  const ws = XLSX.utils.json_to_sheet(filas);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'facturacion');
  XLSX.writeFile(wb, `facturacion_${stamp()}.xlsx`);
}

const prefacturaPdfVisible = ref(false);
const prefacturaPdfUrl = ref('');
const generandoPrefacturaId = ref(null);

async function abrirPrefactura(row) {
  if (row.facturapi_draft_id) {
    prefacturaPdfUrl.value = await getPrefacturaPdfUrl(row.id);
    prefacturaPdfVisible.value = true;
    return;
  }

  generandoPrefacturaId.value = row.id;
  try {
    const clientes = await getClientes();
    const cliente = clientes.find(c => (c.nombre || '').trim().toLowerCase() === (row.cliente || '').trim().toLowerCase());
    if (!cliente?.rfc || !cliente?.codigo_postal || !cliente?.regimen_fiscal) {
      toast.add({
        severity: 'warn', summary: 'Faltan datos fiscales',
        detail: 'Completa el RFC / código postal / régimen fiscal del cliente desde el detalle de la factura antes de generar la prefactura.',
        life: 6000
      });
      irDetalle(row.id);
      return;
    }

    await generarPrefacturaFactura(row.id, {
      rfc_cliente: cliente.rfc,
      uso_cfdi: 'G03',
      forma_pago: '03',
      metodo_pago: 'PUE',
      domicilio_fiscal_receptor: cliente.codigo_postal,
      regimen_fiscal_receptor: cliente.regimen_fiscal,
    });
    await cargar();
    prefacturaPdfUrl.value = await getPrefacturaPdfUrl(row.id);
    prefacturaPdfVisible.value = true;
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo generar la prefactura.', life: 5000 });
  }
  generandoPrefacturaId.value = null;
}

const showConfirmDelete = ref(false);
const eliminarItem = ref(null);
const eliminando = ref(false);
function confirmarEliminar(item) {
  eliminarItem.value = item;
  showConfirmDelete.value = true;
}
async function ejecutarEliminar() {
  if (!eliminarItem.value) return;
  eliminando.value = true;
  try {
    await eliminarFactura(eliminarItem.value.id);
    toast.add({ severity: 'success', summary: 'Eliminada', detail: 'Prefactura eliminada.', life: 3000 });
    showConfirmDelete.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo eliminar.', life: 4000 });
  }
  eliminando.value = false;
}

async function cargar() {
  loading.value = true;
  try {
    facturas.value = await getFacturas();
  } catch {
    facturas.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar las facturas.', life: 4000 });
  }
  loading.value = false;
}

function setViewportMode() { isMobile.value = window.innerWidth <= 768; }

function diasPendiente(fecha) {
  if (!fecha) return 0;
  const dias = (Date.now() - new Date(fecha).getTime()) / 86400000;
  return Math.max(0, Math.floor(dias));
}
function claseAntiguedad(fecha) {
  const d = diasPendiente(fecha);
  if (d >= 15) return 'antiguedad-critica';
  if (d >= 7) return 'antiguedad-media';
  return '';
}

const showNuevaDialog = ref(false);
const nuevaCliente = ref('');
const nuevaTotal = ref(0);
const nuevaPagada = ref(false);
const productosManuales = ref([{ Descripcion: '', ValorUnitario: 0, Cantidad: 1, ClaveProdServ: '' }]);
const creandoFactura = ref(false);

const articulosTodos = ref([]);
const ubicaciones = ref([]);
const ubicacionSeleccionada = ref(null);
const imeisUbicacion = ref([]);
const cargandoImeisUbicacion = ref(false);
const busquedaArticuloImei = ref('');
const articulosVendidos = ref([]);

const articulosPorNombre = computed(() => {
  const map = {};
  for (const a of articulosTodos.value) {
    if (a?.nombre) map[a.nombre] = a;
  }
  return map;
});
function precioDeArticulo(nombre) {
  return articulosPorNombre.value[nombre]?.precioVenta ?? null;
}

const imeisDisponiblesUbicacion = computed(() => {
  const yaElegidos = new Set(articulosVendidos.value.map(a => a.imei));
  return imeisUbicacion.value.filter(im => im.status === 'Disponible' && !yaElegidos.has(im.imei));
});
const imeisDisponiblesFiltrados = computed(() => {
  const q = busquedaArticuloImei.value.trim().toLowerCase();
  if (!q) return imeisDisponiblesUbicacion.value;
  return imeisDisponiblesUbicacion.value.filter(im =>
    String(im.articulo_nombre || '').toLowerCase().includes(q) ||
    String(im.sku || '').toLowerCase().includes(q) ||
    String(im.imei || '').toLowerCase().includes(q)
  );
});

function recalcularTotal() {
  const totalArticulos = articulosVendidos.value.reduce((sum, a) => sum + (Number(a.precioVenta) || 0), 0);
  nuevaTotal.value = totalArticulos;
}

function agregarProductoManual() {
  productosManuales.value.push({ Descripcion: '', ValorUnitario: 0, Cantidad: 1, ClaveProdServ: '' });
}
function quitarProductoManual(idx) {
  productosManuales.value.splice(idx, 1);
}

async function onUbicacionSeleccionada() {
  imeisUbicacion.value = [];
  busquedaArticuloImei.value = '';
  if (!ubicacionSeleccionada.value) return;
  cargandoImeisUbicacion.value = true;
  try {
    imeisUbicacion.value = await getImeisPorUbicacion(ubicacionSeleccionada.value.id);
  } catch {
    imeisUbicacion.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los IMEIs de esta ubicación.', life: 4000 });
  }
  cargandoImeisUbicacion.value = false;
}

function agregarArticuloVendido(imeiObj, checked) {
  if (!checked) return;
  const articuloInfo = articulosPorNombre.value[imeiObj.articulo_nombre] || {};
  articulosVendidos.value = [...articulosVendidos.value, {
    imei: imeiObj.imei,
    imeiCompleto: imeiObj,
    articulo_id: articuloInfo.id || null,
    articulo_nombre: imeiObj.articulo_nombre || imeiObj.sku || 'Artículo',
    precioVenta: Number(articuloInfo.precioVenta) || 0,
    codigoSat: articuloInfo.codigoSat || null,
    unidadSat: articuloInfo.unidadSat || null,
    codigoUnidadSat: articuloInfo.codigoUnidadSat || null,
  }];
  recalcularTotal();
}
function quitarArticuloVendido(idx) {
  articulosVendidos.value.splice(idx, 1);
  recalcularTotal();
}

async function abrirNuevaFactura() {
  nuevaCliente.value = '';
  nuevaTotal.value = 0;
  nuevaPagada.value = false;
  productosManuales.value = [{ Descripcion: '', ValorUnitario: 0, Cantidad: 1, ClaveProdServ: '' }];
  ubicacionSeleccionada.value = null;
  imeisUbicacion.value = [];
  busquedaArticuloImei.value = '';
  articulosVendidos.value = [];
  showNuevaDialog.value = true;

  try {
    const [articulos, ubis] = await Promise.all([getTodosArticulos(), getUbicaciones()]);
    articulosTodos.value = articulos;
    ubicaciones.value = ubis;
  } catch {
    articulosTodos.value = [];
    ubicaciones.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los artículos/ubicaciones.', life: 4000 });
  }
}

async function confirmarNuevaFactura() {
  const cliente = nuevaCliente.value.trim();
  const total = Number(nuevaTotal.value) || 0;
  if (!cliente) {
    toast.add({ severity: 'warn', summary: 'Falta cliente', detail: 'Escribe el nombre del cliente.', life: 3500 });
    return;
  }
  if (total <= 0) {
    toast.add({ severity: 'warn', summary: 'Total inválido', detail: 'El total debe ser mayor a cero.', life: 3500 });
    return;
  }
  const conceptosManuales = productosManuales.value
    .filter(p => p.Descripcion?.trim() && Number(p.ValorUnitario) > 0)
    .map(p => ({
      Descripcion: p.Descripcion.trim(),
      ValorUnitario: Number(p.ValorUnitario),
      Cantidad: Number(p.Cantidad) || 1,
      ClaveProdServ: p.ClaveProdServ?.trim() || undefined
    }));
  const conceptosArticulos = articulosVendidos.value.map(a => ({
    Descripcion: `${a.articulo_nombre} (IMEI ${a.imei})`,
    ValorUnitario: Number(a.precioVenta) || 0,
    Cantidad: 1,
    ClaveProdServ: a.codigoSat || undefined,
    ClaveUnidad: a.codigoUnidadSat || undefined,
    Unidad: a.unidadSat || undefined,
    imei: a.imei
  }));
  const todosLosConceptos = [...conceptosManuales, ...conceptosArticulos];

  if (!todosLosConceptos.length) {
    toast.add({ severity: 'warn', summary: 'Faltan conceptos', detail: 'Agrega al menos un concepto o artículo.', life: 4500 });
    return;
  }

  creandoFactura.value = true;
  try {
    await crearFactura({
      ordenes: [],
      cliente,
      total,
      status: 'Pendiente timbre',
      reporte_ids: [],
      productos_manual: todosLosConceptos.length ? todosLosConceptos : null,
      pagado: nuevaPagada.value
    });

    if (articulosVendidos.value.length) {
      try {
        await Promise.all(articulosVendidos.value.map(a =>
          updateIMEI(a.imei, { ...a.imeiCompleto, status: 'Vendido' })
        ));
        await sincronizarStockArticulos();
      } catch {
        toast.add({ severity: 'warn', summary: 'Prefactura creada, stock pendiente', detail: 'La prefactura se creó pero no se pudo actualizar el stock/IMEIs. Actualízalo manualmente.', life: 6000 });
      }
    }

    toast.add({ severity: 'success', summary: 'Prefactura creada', detail: 'Ya puedes generarla en el PAC y previsualizar el PDF antes de timbrar.', life: 3500 });
    showNuevaDialog.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo crear la prefactura.', life: 4000 });
  }
  creandoFactura.value = false;
}

onMounted(() => {
  if (!esAdmin.value) {
    router.replace('/');
    return;
  }
  setViewportMode();
  window.addEventListener('resize', setViewportMode);
  cargar();
});
onBeforeUnmount(() => window.removeEventListener('resize', setViewportMode));
</script>

<style scoped>
.fact-container { margin: 2rem auto; padding: 2rem 1.5rem; }
.fact-title {
  display: flex; align-items: center; justify-content: center; gap: 0.6rem;
  color: var(--color-title); margin-bottom: 1.75rem;
  font-size: 1.6rem; font-weight: 800; letter-spacing: -0.02em;
}
.fact-title .pi { color: var(--color-primary); }

.fact-nueva-bar { display: flex; justify-content: flex-end; gap: 0.6rem; margin-bottom: 1rem; }

.nueva-fact-dialog :deep(.p-dialog-content) { padding-bottom: 0; }
.nueva-fact-form {
  max-height: 65vh; overflow-y: auto; overflow-x: hidden;
  padding-right: 0.5rem; margin-right: -0.5rem;
}
.nueva-fact-form .form-group { margin-bottom: 1.1rem; }
.nueva-fact-form label { display: block; font-weight: 600; margin-bottom: 0.4rem; font-size: 0.85rem; }
.pago-toggle-label { display: flex !important; align-items: center; gap: 0.5rem; cursor: pointer; }
.modal-actions { display: flex; gap: 1rem; justify-content: flex-end; }
.reportes-pick-list {
  margin-top: 0.5rem; max-height: 200px; overflow-y: auto;
  border: 1px solid var(--color-border); border-radius: 10px; padding: 0.4rem 0.6rem;
}
.reportes-pick-empty { padding: 0.5rem; color: var(--color-border); text-align: center; }
.reportes-pick-item {
  display: flex; align-items: center; gap: 0.5rem;
  padding: 0.35rem 0.2rem; font-size: 0.88rem; cursor: pointer;
}
.producto-manual-row {
  display: flex; gap: 0.5rem; align-items: center; margin-bottom: 0.5rem; flex-wrap: wrap;
}
.producto-desc { flex: 2; min-width: 160px; }
.producto-precio { flex: 1; min-width: 120px; }
.producto-cant { width: 90px; }
.producto-clave { width: 150px; }
.articulo-pick-row { margin-top: 0.5rem; }
.articulos-vendidos-lista { margin-top: 0.6rem; display: flex; flex-direction: column; gap: 0.4rem; }
.articulo-vendido-item {
  display: flex; align-items: center; justify-content: space-between; gap: 0.5rem;
  padding: 0.4rem 0.6rem; border-radius: 8px; font-size: 0.85rem;
  background: color-mix(in srgb, var(--color-success) 10%, transparent);
}

.fact-toolbar {
  display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
  margin-bottom: 1.5rem; padding: 1rem 1.1rem; border-radius: 16px;
  background: var(--color-card); border: 1px solid var(--color-border);
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.04));
}
.fact-search {
  position: relative; flex: 1; min-width: 220px; display: flex; align-items: center;
}
.fact-search .pi {
  position: absolute; left: 0.9rem; color: var(--color-text); opacity: 0.5; font-size: 0.9rem; pointer-events: none;
}
.fact-search :deep(input) {
  width: 100%; padding-left: 2.4rem; border-radius: 10px;
  background: var(--color-bg-light, transparent);
}
.fact-dropdown { min-width: 180px; }
.filtro-estado { display: flex; gap: 0.4rem; flex-wrap: wrap; }
.estado-chip {
  display: flex; align-items: center; gap: 0.4rem;
  padding: 0.45rem 1rem; border-radius: 999px;
  border: 1px solid var(--color-border); background: transparent; color: var(--color-text);
  cursor: pointer; font-size: 0.83rem; font-weight: 600;
  transition: background 0.15s, border-color 0.15s, color 0.15s;
}
.estado-chip:hover { border-color: var(--color-primary); }
.estado-chip.activo { background: var(--color-primary); border-color: var(--color-primary); color: var(--color-on-primary, #b63434); }
.estado-chip-count {
  opacity: 0.85; font-weight: 700; font-size: 0.72rem;
  background: color-mix(in srgb, currentColor 16%, transparent);
  padding: 0.05rem 0.45rem; border-radius: 999px;
}

.fact-mes-aviso {
  display: flex; align-items: center; gap: 0.5rem;
  font-size: 0.85rem; color: var(--color-text); opacity: 0.75;
  margin: -0.75rem 0 1rem;
}

.emoji-check, .emoji-cross { font-size: 1.1rem; line-height: 1; }
.comprobante-icono { font-size: 1.15rem; color: var(--color-primary); }
.texto-cancelada { color: var(--color-warning) !important; font-weight: 700; font-size: 0.82rem; }

.fact-table-card {
  background: var(--color-card); border: 1px solid var(--color-border);
  border-radius: 16px; overflow: hidden;
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.04));
}
.fact-table-card :deep(.p-datatable-header),
.fact-table-card :deep(th) {
  background: var(--color-bg-light, transparent);
  font-size: 0.78rem; text-transform: uppercase; letter-spacing: 0.03em;
}
.fact-table-card :deep(tr:hover td) {
  background: color-mix(in srgb, var(--color-primary) 5%, transparent);
}
.celda-total { font-weight: 700; color: var(--color-title); }
.celda-vacia { color: var(--color-border); }

.badge {
  display: inline-flex; align-items: center; gap: 0.4rem;
  padding: 0.3rem 0.8rem; border-radius: 999px; font-size: 0.78rem; font-weight: 700;
}
.badge::before { content: ''; width: 6px; height: 6px; border-radius: 50%; background: currentColor; }
.badge-success { background: color-mix(in srgb, var(--color-success) 18%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 20%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 16%, transparent); color: var(--color-error); }

.antiguedad-pill {
  display: inline-block; padding: 0.2rem 0.6rem; border-radius: 999px;
  font-size: 0.78rem; font-weight: 700;
  background: color-mix(in srgb, var(--color-success) 14%, transparent); color: var(--color-success);
}
.antiguedad-pill.antiguedad-media { background: color-mix(in srgb, var(--color-warning) 18%, transparent); color: var(--color-warning); }
.antiguedad-pill.antiguedad-critica { background: color-mix(in srgb, var(--color-error) 18%, transparent); color: var(--color-error); }

.mobile-list-wrap { padding: 0.75rem; }
.mobile-loader-wrap, .mobile-empty { padding: 1rem; text-align: center; }
.mobile-cards { display: flex; flex-direction: column; gap: 0.75rem; }
.mobile-card {
  border: 1px solid var(--color-border); background: var(--color-bg-light, transparent);
  border-radius: 14px; padding: 1rem; cursor: pointer; transition: border-color 0.15s;
}
.mobile-card:hover { border-color: var(--color-primary); }
.mobile-card-header { display: flex; justify-content: space-between; gap: 0.8rem; align-items: flex-start; margin-bottom: 0.75rem; }
.mobile-card-id { margin: 0; font-size: 0.78rem; color: var(--color-text); font-weight: 600; }
.mobile-card-cliente { margin: 0.2rem 0 0; font-weight: 700; color: var(--color-title); }
.mobile-card-grid { display: grid; grid-template-columns: repeat(2, minmax(0, 1fr)); gap: 0.6rem; }
.mobile-field-full { grid-column: 1 / -1; }
.mobile-label { display: block; font-size: 0.72rem; color: var(--color-text); margin-bottom: 0.15rem; text-transform: uppercase; }
.mobile-value { display: block; font-size: 0.88rem; color: var(--color-text); }

@media (max-width: 768px) {
  .fact-container { margin: 1rem auto; padding: 1rem 0.75rem; }
  .fact-toolbar { border-radius: 12px; }
}
</style>
