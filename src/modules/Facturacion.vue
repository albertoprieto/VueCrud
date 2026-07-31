<template>
  <div class="fact-container">
    <h2 class="fact-title"><i class="pi pi-receipt" /> Facturación</h2>

    <div class="fact-nueva-bar">
      <Button label="Nueva Factura" icon="pi pi-plus" class="p-button-sm" @click="abrirNuevaFactura" />
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

    <div class="fact-table-card">
      <DataTable
        v-if="!isMobile"
        :value="facturasFiltradas"
        responsiveLayout="scroll"
        :loading="loading"
        :paginator="facturasFiltradas.length > 15"
        :rows="15"
      >
        <template #loading><DataTableLoader text="Cargando facturas..." /></template>
        <Column field="id" header="ID" style="width:60px" />
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
        <Column header="Estatus">
          <template #body="{ data }">
            <span :class="'badge badge-' + badgeClass(data.status)">{{ data.status }}</span>
          </template>
        </Column>
        <Column header="Pago">
          <template #body="{ data }">
            <span :class="'badge badge-' + (data.pagado ? 'success' : 'warning')">{{ data.pagado ? 'Pagada' : 'Pendiente pago' }}</span>
          </template>
        </Column>
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
        <Column header="Acciones" style="width:220px">
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

    <Dialog v-model:visible="showConfirmDelete" header="Eliminar prefactura" :modal="true" :closable="false">
      <div style="padding:1rem;text-align:center;">
        <span>¿Eliminar esta prefactura? Los reportes de servicio quedarán libres para agregarse a otra.</span>
      </div>
      <div style="display:flex;gap:1rem;justify-content:center;padding-bottom:1rem;">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" :loading="eliminando" @click="ejecutarEliminar" />
        <Button label="Cancelar" class="p-button-secondary" @click="showConfirmDelete = false" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showNuevaDialog" header="Nueva factura" :modal="true" :closable="false" style="width: 920px; max-width: 96vw;">
      <div class="nueva-fact-form">
        <div class="form-group">
          <label>Cliente</label>
          <InputText v-model="nuevaCliente" class="w-full" placeholder="Nombre del cliente (existente o nuevo)" />
          <small style="color:var(--color-text);opacity:0.7;">
            Al ligar un reporte de servicio se autocompleta con su cliente (editable). Si el cliente no existe aún, se dará de alta con sus datos fiscales al momento de timbrar.
          </small>
        </div>

        <div class="form-group">
          <label>Órdenes / reportes de servicio (opcional)</label>
          <InputText v-model="busquedaReporte" class="w-full" placeholder="Buscar por orden o cliente..." />
          <div class="reportes-pick-list">
            <div v-if="cargandoReportes" style="padding:0.75rem;text-align:center;"><i class="pi pi-spin pi-spinner" /></div>
            <div v-else-if="!reportesFiltradosDisponibles.length" class="reportes-pick-empty">Sin reportes disponibles.</div>
            <label v-for="r in reportesFiltradosDisponibles" :key="r.id" class="reportes-pick-item">
              <input type="checkbox" :checked="reporteEstaSeleccionado(r)" @change="toggleReporteSeleccionado(r, $event.target.checked)" />
              <span>{{ r.folio || r.id }} — {{ r.nombre_cliente || 'Sin cliente' }} — {{ formatTotal(r.total) }}</span>
            </label>
          </div>
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
          <label>Productos / conceptos manuales (requerido si no hay reportes ni artículos ligados)</label>
          <div v-for="(prod, idx) in productosManuales" :key="idx" class="producto-manual-row">
            <InputText v-model="prod.Descripcion" placeholder="Descripción" class="producto-desc" />
            <InputNumber v-model="prod.ValorUnitario" placeholder="Precio unitario" mode="currency" currency="MXN" locale="es-MX" class="producto-precio" />
            <InputNumber v-model="prod.Cantidad" placeholder="Cant." :min="1" class="producto-cant" />
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
      <div class="modal-actions" style="display:flex;gap:1rem;justify-content:flex-end;padding-top:0.5rem;">
        <Button label="Crear factura" icon="pi pi-check" :loading="creandoFactura" @click="confirmarNuevaFactura" />
        <Button label="Cancelar" class="p-button-secondary" @click="showNuevaDialog = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import DataTableLoader from '@/components/DataTableLoader.vue';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import { getFacturas, eliminarFactura, crearFactura, getNotas } from '@/services/pagosService';
import { getTodosReportes } from '@/services/reportesServicio';
import { getTodosArticulos, sincronizarStockArticulos } from '@/services/articulosService';
import { updateIMEI } from '@/services/imeiService';
import { getUbicaciones, getImeisPorUbicacion } from '@/services/ubicacionesService';

const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

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
  { value: 'todos', label: 'Cualquier pago' },
  { value: 'pagadas', label: 'Pagadas' },
  { value: 'pendientes', label: 'Pendiente pago' },
];

function contarPorEstado(valor) {
  if (valor === 'todos') return facturas.value.length;
  return facturas.value.filter(f => f.status === valor).length;
}

function contarPorPago(valor) {
  if (valor === 'todos') return facturas.value.length;
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
    if (filtroPago.value === 'pagadas' && !f.pagado) return false;
    if (filtroPago.value === 'pendientes' && f.pagado) return false;
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
const busquedaReporte = ref('');
const cargandoReportes = ref(false);
const reportesTodos = ref([]);
const reportesSeleccionados = ref([]);
const reportesAsignadosIds = ref(new Set());
const productosManuales = ref([{ Descripcion: '', ValorUnitario: 0, Cantidad: 1 }]);
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

const reportesDisponibles = computed(() =>
  reportesTodos.value.filter(r => !reportesAsignadosIds.value.has(r.id))
);
const reportesFiltradosDisponibles = computed(() => {
  const q = busquedaReporte.value.trim().toLowerCase();
  if (!q) return reportesDisponibles.value;
  return reportesDisponibles.value.filter(r =>
    String(r.folio || '').toLowerCase().includes(q) ||
    String(r.nombre_cliente || '').toLowerCase().includes(q)
  );
});

function reporteEstaSeleccionado(r) {
  return reportesSeleccionados.value.some(s => s.id === r.id);
}
function recalcularTotal() {
  const totalReportes = reportesSeleccionados.value.reduce((sum, s) => sum + (Number(s.total) || 0), 0);
  const totalArticulos = articulosVendidos.value.reduce((sum, a) => sum + (Number(a.precioVenta) || 0), 0);
  nuevaTotal.value = totalReportes + totalArticulos;
}
function toggleReporteSeleccionado(r, checked) {
  if (checked) {
    reportesSeleccionados.value = [...reportesSeleccionados.value, r];
  } else {
    reportesSeleccionados.value = reportesSeleccionados.value.filter(s => s.id !== r.id);
  }
  recalcularTotal();
  if (reportesSeleccionados.value.length) {
    nuevaCliente.value = reportesSeleccionados.value[0]?.nombre_cliente || nuevaCliente.value;
  }
}

function agregarProductoManual() {
  productosManuales.value.push({ Descripcion: '', ValorUnitario: 0, Cantidad: 1 });
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
  busquedaReporte.value = '';
  reportesSeleccionados.value = [];
  productosManuales.value = [{ Descripcion: '', ValorUnitario: 0, Cantidad: 1 }];
  ubicacionSeleccionada.value = null;
  imeisUbicacion.value = [];
  busquedaArticuloImei.value = '';
  articulosVendidos.value = [];
  showNuevaDialog.value = true;

  cargandoReportes.value = true;
  try {
    const [reportes, notas, articulos, ubis] = await Promise.all([getTodosReportes(), getNotas(), getTodosArticulos(), getUbicaciones()]);
    reportesTodos.value = reportes;
    articulosTodos.value = articulos;
    ubicaciones.value = ubis;
    const asignados = new Set();
    for (const n of notas) for (const rid of (n.reporte_ids || [])) asignados.add(rid);
    for (const f of facturas.value) for (const rid of (f.reporte_ids || [])) asignados.add(rid);
    reportesAsignadosIds.value = asignados;
  } catch {
    reportesTodos.value = [];
    articulosTodos.value = [];
    ubicaciones.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los reportes/artículos/ubicaciones.', life: 4000 });
  }
  cargandoReportes.value = false;
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
    .map(p => ({ Descripcion: p.Descripcion.trim(), ValorUnitario: Number(p.ValorUnitario), Cantidad: Number(p.Cantidad) || 1 }));
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

  if (!reportesSeleccionados.value.length && !todosLosConceptos.length) {
    toast.add({ severity: 'warn', summary: 'Faltan conceptos', detail: 'Agrega al menos un concepto, artículo o liga un reporte de servicio.', life: 4500 });
    return;
  }

  creandoFactura.value = true;
  try {
    await crearFactura({
      ordenes: reportesSeleccionados.value.map(r => r.folio),
      cliente,
      total,
      status: 'Pendiente timbre',
      reporte_ids: reportesSeleccionados.value.map(r => r.id),
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
        toast.add({ severity: 'warn', summary: 'Factura creada, stock pendiente', detail: 'La factura se creó pero no se pudo actualizar el stock/IMEIs. Actualízalo manualmente.', life: 6000 });
      }
    }

    toast.add({ severity: 'success', summary: 'Factura creada', detail: 'La prefactura se creó correctamente.', life: 3000 });
    showNuevaDialog.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo crear la factura.', life: 4000 });
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

.fact-nueva-bar { display: flex; justify-content: flex-end; margin-bottom: 1rem; }

.nueva-fact-form .form-group { margin-bottom: 1.1rem; }
.nueva-fact-form label { display: block; font-weight: 600; margin-bottom: 0.4rem; font-size: 0.85rem; }
.pago-toggle-label { display: flex !important; align-items: center; gap: 0.5rem; cursor: pointer; }
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
