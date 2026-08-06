<template>
  <div class="bancos-container">
    <h2 class="bancos-title">Comprobantes</h2>

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <div class="bancos-total-card">
        <span class="bancos-total-label">Saldo total en bancos</span>
        <span class="bancos-total-valor">{{ formatTotal(saldoTotal) }}</span>
      </div>

      <div class="comprobantes-toolbar">
        <InputText v-model="busqueda" placeholder="Buscar por nombre, usuario o IMEI..." class="comprobantes-buscador" />
        <Dropdown v-model="filtroBanco" :options="opcionesFiltroBanco" optionLabel="label" optionValue="value" placeholder="Banco" class="comprobantes-filtro" />
        <Dropdown v-model="filtroTipo" :options="opcionesFiltroTipo" optionLabel="label" optionValue="value" placeholder="Tipo" class="comprobantes-filtro" />
        <div class="comprobantes-toolbar-acciones">
          <Button label="Nuevo movimiento" icon="pi pi-plus" class="p-button-sm" @click="abrirNuevoMovimiento" />
          <Button label="Nuevo retiro" icon="pi pi-upload" class="p-button-sm p-button-danger" @click="abrirNuevoRetiro" />
        </div>
      </div>

      <DataTable
        :value="filasFiltradas"
        responsiveLayout="scroll"
        :loading="loading"
        :paginator="filasFiltradas.length > 50"
        :rows="50"
        dataKey="key"
        sortMode="single"
      >
        <template #loading><DataTableLoader text="Cargando comprobantes..." /></template>

        <Column field="tipo" header="Tipo" sortable style="width:100px">
          <template #body="{ data }"><span :class="'badge badge-' + badgeClaseTipo(data.tipo)">{{ data.tipo }}</span></template>
        </Column>
        <Column field="fecha" header="Fecha" sortable>
          <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
        </Column>
        <Column field="banco" header="Banco" sortable>
          <template #body="{ data }">
            <Dropdown v-if="editando === data.key" v-model="edicion.banco" :options="lugaresValidos" showClear placeholder="Sin banco" class="edit-input" />
            <span v-else-if="data.banco" class="badge badge-info">{{ data.banco }}</span>
            <span v-else class="badge badge-warning">Sin banco</span>
          </template>
        </Column>
        <Column field="nombre" header="Nombre" sortable>
          <template #body="{ data }">
            <InputText v-if="editando === data.key" v-model="edicion.nombre" class="edit-input" />
            <span v-else>{{ data.nombre || '—' }}</span>
          </template>
        </Column>
        <Column field="usuario" header="Usuario" sortable>
          <template #body="{ data }">{{ data.usuario || '—' }}</template>
        </Column>
        <Column field="imeis" header="IMEIs">
          <template #body="{ data }">{{ data.imeis || '—' }}</template>
        </Column>
        <Column field="monto" header="Monto" sortable>
          <template #body="{ data }">
            <InputNumber v-if="editando === data.key" v-model="edicion.monto" mode="currency" currency="MXN" locale="es-MX" class="edit-input" />
            <span v-else :class="data.monto < 0 ? 'monto-negativo' : 'monto-positivo'">{{ formatTotal(data.monto) }}</span>
          </template>
        </Column>
        <Column header="Reportes">
          <template #body="{ data }">
            <span v-if="data.conReporte === null" class="celda-vacia">—</span>
            <span v-else :class="'badge badge-' + (data.conReporte ? 'success' : 'danger')">{{ data.conReporte ? 'Con reporte' : 'Sin reporte' }}</span>
          </template>
        </Column>
        <Column header="Comprobante">
          <template #body="{ data }">
            <span v-if="data.conComprobante === null" class="celda-vacia">—</span>
            <span v-else :class="'badge badge-' + (data.conComprobante ? 'success' : 'danger')">{{ data.conComprobante ? 'Con comprobante' : 'Sin comprobante' }}</span>
          </template>
        </Column>
        <Column header="Estatus">
          <template #body="{ data }">
            <span v-if="data.estatus" :class="'badge badge-' + badgeClaseEstatus(data.estatus)">{{ data.estatus }}</span>
            <span v-else class="celda-vacia">—</span>
          </template>
        </Column>
        <Column header="Acciones" style="width:230px">
          <template #body="{ data }">
            <div style="display:flex;gap:0.4rem;flex-wrap:wrap;align-items:center;">
              <template v-if="editando === data.key">
                <Button icon="pi pi-check" class="p-button-sm p-button-success" :loading="guardando" @click="guardarEdicion(data)" />
                <Button icon="pi pi-times" class="p-button-sm p-button-secondary" @click="cancelarEdicion" />
              </template>
              <template v-else>
                <Button v-if="esEditable(data)" icon="pi pi-pencil" class="p-button-sm p-button-text" @click="iniciarEdicion(data)" />
                <Button
                  v-if="data.tipo === 'Retiro' && data.estatus === 'pendiente' && esAdmin"
                  icon="pi pi-check" label="Aprobar" class="p-button-sm p-button-success"
                  @click="aprobar(data)"
                />
                <Button
                  v-if="data.tipo === 'Retiro' && data.estatus === 'pendiente' && esAdmin"
                  icon="pi pi-times" label="Rechazar" class="p-button-sm p-button-danger p-button-outlined"
                  @click="rechazar(data)"
                />
                <router-link v-if="data.tipo === 'Nota'" :to="{ name: 'detalle-pago', params: { tipo: 'nota', id: data.id } }" class="p-button p-button-sm p-button-text p-button-icon-only"><i class="pi pi-eye" /></router-link>
                <router-link v-else-if="data.tipo === 'Factura'" :to="{ name: 'detalle-factura', params: { id: data.id } }" class="p-button p-button-sm p-button-text p-button-icon-only"><i class="pi pi-eye" /></router-link>
              </template>
            </div>
          </template>
        </Column>
      </DataTable>
    </template>

    <Dialog v-model:visible="showMovimientoDialog" header="Nuevo movimiento" :modal="true" :style="{ width: '420px', maxWidth: '95vw' }">
      <div class="form-group">
        <label>Tipo</label>
        <Dropdown v-model="nuevoMovimiento.tipo" :options="['Ingreso', 'Egreso']" class="w-full" />
      </div>
      <div class="form-group">
        <label>Banco</label>
        <Dropdown v-model="nuevoMovimiento.banco" :options="lugaresValidos" showClear placeholder="Sin banco" class="w-full" />
      </div>
      <div class="form-group">
        <label>Concepto</label>
        <InputText v-model="nuevoMovimiento.concepto" class="w-full" placeholder="Ej: Pago a proveedor" />
      </div>
      <div class="form-group">
        <label>Monto</label>
        <InputNumber v-model="nuevoMovimiento.monto" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
      </div>
      <div class="form-group">
        <label>Referencia (opcional)</label>
        <InputText v-model="nuevoMovimiento.referencia" class="w-full" />
      </div>
      <div class="modal-actions">
        <Button label="Registrar" icon="pi pi-check" :loading="guardandoMovimiento" @click="confirmarNuevoMovimiento" />
        <Button label="Cancelar" class="p-button-secondary" @click="showMovimientoDialog = false" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showRetiroDialog" header="Registrar retiro" :modal="true" :style="{ width: '420px', maxWidth: '95vw' }">
      <div class="form-group">
        <label>Banco</label>
        <Dropdown v-model="nuevoRetiro.banco" :options="lugaresValidos" placeholder="Selecciona un banco" class="w-full" />
      </div>
      <div class="form-group">
        <label>Monto a retirar</label>
        <InputNumber v-model="nuevoRetiro.monto" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
      </div>
      <div class="form-group">
        <label>Motivo (opcional)</label>
        <InputText v-model="nuevoRetiro.motivo" placeholder="Ej: Pago a proveedor" class="w-full" />
      </div>
      <div class="form-group">
        <label>Comprobante</label>
        <input type="file" accept="application/pdf,image/*" @change="onArchivoRetiroChange" />
      </div>
      <div class="modal-actions">
        <Button
          label="Registrar" icon="pi pi-upload" class="p-button-danger"
          :disabled="!nuevoRetiro.banco || !nuevoRetiro.monto || !archivoRetiro"
          :loading="guardandoRetiro" @click="confirmarNuevoRetiro"
        />
        <Button label="Cancelar" class="p-button-secondary" @click="showRetiroDialog = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Dropdown from 'primevue/dropdown';
import Dialog from 'primevue/dialog';
import DataTableLoader from '@/components/DataTableLoader.vue';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import {
  getNotas, getFacturas,
  actualizarLugarPagoNota, actualizarCamposNota,
  actualizarLugarPagoFactura, actualizarCamposFactura,
} from '@/services/pagosService';
import { getRetiros, crearRetiro, aprobarRetiro, rechazarRetiro } from '@/services/bancosService';
import { getMovimientosDinero, registrarAbonoDinero, actualizarMovimientoDinero } from '@/services/dineroService';

const toast = useToast();
const loginStore = useLoginStore();
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

const lugaresValidos = ['ASP Vianey', 'ASP Renovaciones', 'Comercializadora', 'BBVA PAU', 'Tecnico', 'Oficina', 'Mercadopago', 'MercadoPago Eliseo'];

const loading = ref(true);
const notas = ref([]);
const facturas = ref([]);
const movimientos = ref([]);
const retiros = ref([]);

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2,
});
function formatTotal(value) { return formatoMoneda.format(Number(value) || 0); }
function formatFecha(f) {
  if (!f) return '—';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}

function parseComprobantes(raw) {
  if (Array.isArray(raw)) return raw;
  if (typeof raw === 'string') {
    try { return JSON.parse(raw) || []; } catch { return []; }
  }
  return [];
}

// ── Unificación: cada comprobante/movimiento de dinero, sin importar su origen, es una fila ──
const filas = computed(() => {
  const out = [];
  for (const n of notas.value) {
    out.push({
      key: `nota-${n.id}`, id: n.id, tipo: 'Nota',
      fecha: n.fecha, banco: n.lugar_pago || null,
      nombre: n.cliente || '', usuario: n.usuario || '',
      imeis: (n.imeis || []).join(', '),
      monto: Number(n.total) || 0,
      conReporte: (n.reporte_ids || []).length > 0,
      conComprobante: parseComprobantes(n.comprobantes).length > 0,
      estatus: n.status,
      raw: n,
    });
  }
  for (const f of facturas.value) {
    out.push({
      key: `factura-${f.id}`, id: f.id, tipo: 'Factura',
      fecha: f.fecha, banco: f.lugar_pago || null,
      nombre: f.cliente || '', usuario: f.usuario || '',
      imeis: (f.imeis || []).join(', '),
      monto: Number(f.total) || 0,
      conReporte: (f.reporte_ids || []).length > 0,
      conComprobante: parseComprobantes(f.comprobantes).length > 0 || !!f.cfdi_pdf_path,
      estatus: f.status,
      raw: f,
    });
  }
  for (const m of movimientos.value) {
    out.push({
      key: `mov-${m.id}`, id: m.id, tipo: m.tipo === 'Egreso' ? 'Egreso' : 'Ingreso',
      fecha: m.fecha, banco: m.banco || null,
      nombre: m.concepto || '', usuario: '',
      imeis: '',
      monto: Number(m.monto) || 0,
      conReporte: null, conComprobante: null,
      estatus: '',
      raw: m,
    });
  }
  for (const r of retiros.value) {
    out.push({
      key: `retiro-${r.id}`, id: r.id, tipo: 'Retiro',
      fecha: r.creado_fecha, banco: r.banco || null,
      nombre: r.motivo || 'Retiro de banco', usuario: '',
      imeis: '',
      monto: -(Number(r.monto) || 0),
      conReporte: null, conComprobante: !!r.comprobante_path,
      estatus: r.estatus,
      raw: r,
    });
  }
  return out;
});

const saldoTotal = computed(() => {
  let total = 0;
  for (const f of filas.value) {
    if (f.tipo === 'Nota' && f.raw.status === 'cancelado') continue;
    if (f.tipo === 'Factura' && f.raw.status === 'Cancelado') continue;
    if (f.tipo === 'Retiro' && f.raw.estatus !== 'aprobado') continue;
    total += f.monto;
  }
  return total;
});

const busqueda = ref('');
const filtroBanco = ref('todos');
const filtroTipo = ref('todos');
const opcionesFiltroBanco = [
  { label: 'Todos los bancos', value: 'todos' },
  { label: 'Sin banco', value: 'sin_banco' },
  ...lugaresValidos.map(l => ({ label: l, value: l })),
];
const opcionesFiltroTipo = [
  { label: 'Todos', value: 'todos' },
  { label: 'Nota', value: 'Nota' },
  { label: 'Factura', value: 'Factura' },
  { label: 'Ingreso', value: 'Ingreso' },
  { label: 'Egreso', value: 'Egreso' },
  { label: 'Retiro', value: 'Retiro' },
];

const filasFiltradas = computed(() => {
  const q = busqueda.value.trim().toLowerCase();
  return filas.value.filter(f => {
    if (q && !(
      String(f.nombre || '').toLowerCase().includes(q) ||
      String(f.usuario || '').toLowerCase().includes(q) ||
      String(f.imeis || '').toLowerCase().includes(q)
    )) return false;
    if (filtroBanco.value === 'sin_banco' && f.banco) return false;
    if (filtroBanco.value !== 'todos' && filtroBanco.value !== 'sin_banco' && f.banco !== filtroBanco.value) return false;
    if (filtroTipo.value !== 'todos' && f.tipo !== filtroTipo.value) return false;
    return true;
  });
});

function badgeClaseTipo(tipo) {
  if (tipo === 'Nota' || tipo === 'Factura' || tipo === 'Ingreso') return 'success';
  if (tipo === 'Egreso' || tipo === 'Retiro') return 'danger';
  return 'info';
}
function badgeClaseEstatus(estatus) {
  const e = String(estatus).toLowerCase();
  if (e === 'pagado' || e === 'timbrado' || e === 'aprobado') return 'success';
  if (e === 'cancelado' || e === 'rechazado') return 'danger';
  return 'warning';
}

// ── Edición inline (banco, nombre, monto) ──
const editando = ref(null);
const edicion = ref({ banco: null, nombre: '', monto: 0 });
const guardando = ref(false);

function esEditable(fila) {
  return fila.tipo === 'Nota' || fila.tipo === 'Factura' || fila.tipo === 'Ingreso' || fila.tipo === 'Egreso';
}
function iniciarEdicion(fila) {
  editando.value = fila.key;
  edicion.value = { banco: fila.banco, nombre: fila.nombre, monto: fila.monto };
}
function cancelarEdicion() {
  editando.value = null;
}

async function guardarEdicion(fila) {
  guardando.value = true;
  try {
    if (fila.tipo === 'Nota') {
      if (edicion.value.banco !== fila.banco) await actualizarLugarPagoNota(fila.id, edicion.value.banco || '');
      if (edicion.value.nombre !== fila.nombre || Number(edicion.value.monto) !== fila.monto) {
        await actualizarCamposNota(fila.id, { cliente: edicion.value.nombre, total: edicion.value.monto });
      }
    } else if (fila.tipo === 'Factura') {
      if (edicion.value.banco !== fila.banco) await actualizarLugarPagoFactura(fila.id, edicion.value.banco || '');
      if (edicion.value.nombre !== fila.nombre || Number(edicion.value.monto) !== fila.monto) {
        await actualizarCamposFactura(fila.id, { cliente: edicion.value.nombre, total: edicion.value.monto });
      }
    } else if (fila.tipo === 'Ingreso' || fila.tipo === 'Egreso') {
      await actualizarMovimientoDinero(fila.id, { banco: edicion.value.banco || null, concepto: edicion.value.nombre, monto: Number(edicion.value.monto) || 0 });
    }
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Cambios guardados.', life: 2500 });
    editando.value = null;
    await cargar();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar.', life: 4000 });
  }
  guardando.value = false;
}

// ── Nuevo movimiento manual (Ingreso/Egreso) ──
const showMovimientoDialog = ref(false);
const nuevoMovimiento = ref({ tipo: 'Ingreso', banco: null, concepto: '', monto: 0, referencia: '' });
const guardandoMovimiento = ref(false);

function abrirNuevoMovimiento() {
  nuevoMovimiento.value = { tipo: 'Ingreso', banco: null, concepto: '', monto: 0, referencia: '' };
  showMovimientoDialog.value = true;
}
async function confirmarNuevoMovimiento() {
  if (!nuevoMovimiento.value.concepto || !nuevoMovimiento.value.monto) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'Concepto y monto son obligatorios.', life: 3000 });
    return;
  }
  guardandoMovimiento.value = true;
  try {
    await registrarAbonoDinero({
      fecha: new Date().toISOString().slice(0, 10),
      tipo: nuevoMovimiento.value.tipo,
      concepto: nuevoMovimiento.value.concepto,
      monto: Number(nuevoMovimiento.value.monto),
      referencia: nuevoMovimiento.value.referencia,
      banco: nuevoMovimiento.value.banco,
    });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Movimiento registrado.', life: 2500 });
    showMovimientoDialog.value = false;
    await cargar();
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo registrar el movimiento.', life: 4000 });
  }
  guardandoMovimiento.value = false;
}

// ── Nuevo retiro ──
const showRetiroDialog = ref(false);
const nuevoRetiro = ref({ banco: null, monto: null, motivo: '' });
const archivoRetiro = ref(null);
const guardandoRetiro = ref(false);

function abrirNuevoRetiro() {
  nuevoRetiro.value = { banco: null, monto: null, motivo: '' };
  archivoRetiro.value = null;
  showRetiroDialog.value = true;
}
function onArchivoRetiroChange(e) {
  const files = e?.target?.files;
  archivoRetiro.value = files && files.length ? files[0] : null;
}
async function confirmarNuevoRetiro() {
  if (!nuevoRetiro.value.banco || !nuevoRetiro.value.monto || !archivoRetiro.value) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'Banco, monto y comprobante son obligatorios.', life: 3000 });
    return;
  }
  guardandoRetiro.value = true;
  try {
    await crearRetiro({ banco: nuevoRetiro.value.banco, monto: nuevoRetiro.value.monto, motivo: nuevoRetiro.value.motivo, archivo: archivoRetiro.value });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Retiro registrado, pendiente de aprobación.', life: 3000 });
    showRetiroDialog.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo registrar el retiro.', life: 4000 });
  }
  guardandoRetiro.value = false;
}

async function aprobar(fila) {
  try {
    await aprobarRetiro(fila.id);
    toast.add({ severity: 'success', summary: 'Aprobado', detail: 'Retiro aprobado.', life: 2500 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo aprobar.', life: 4000 });
  }
}
async function rechazar(fila) {
  try {
    await rechazarRetiro(fila.id);
    toast.add({ severity: 'success', summary: 'Rechazado', detail: 'Retiro rechazado.', life: 2500 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo rechazar.', life: 4000 });
  }
}

async function cargar() {
  loading.value = true;
  try {
    [notas.value, facturas.value, movimientos.value, retiros.value] = await Promise.all([
      getNotas(), getFacturas(), getMovimientosDinero(), getRetiros(),
    ]);
  } catch {
    notas.value = []; facturas.value = []; movimientos.value = []; retiros.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los comprobantes.', life: 4000 });
  }
  loading.value = false;
}

onMounted(cargar);
</script>

<style scoped>
.bancos-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
}
.bancos-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-title);
}
.bancos-total-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.25rem;
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 14px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.05));
}
.bancos-total-label {
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text);
  opacity: 0.7;
}
.bancos-total-valor {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--color-title);
}

.comprobantes-toolbar {
  display: flex; flex-wrap: wrap; gap: 0.75rem; align-items: center;
  margin-bottom: 1.25rem; padding: 1rem 1.1rem; border-radius: 16px;
  background: var(--color-card); border: 1px solid var(--color-border);
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.04));
}
.comprobantes-buscador { flex: 1; min-width: 220px; }
.comprobantes-filtro { min-width: 180px; }
.comprobantes-toolbar-acciones { display: flex; gap: 0.5rem; margin-left: auto; flex-wrap: wrap; }

.edit-input { width: 100%; min-width: 130px; }
.form-group { margin-bottom: 1rem; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.4rem; font-size: 0.85rem; }
.w-full { width: 100%; }
.modal-actions { display: flex; gap: 1rem; justify-content: flex-end; padding-top: 0.5rem; }

.celda-vacia { color: var(--color-border); }
.monto-positivo { color: var(--color-success); font-weight: 700; }
.monto-negativo { color: var(--color-error); font-weight: 700; }

.badge {
  display: inline-flex; align-items: center; padding: 0.25rem 0.75rem;
  border-radius: 1rem; font-size: 0.78rem; font-weight: 700;
}
.badge-success { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-danger { background: color-mix(in srgb, var(--color-error) 20%, transparent); color: var(--color-error); }
.badge-info { background: color-mix(in srgb, var(--color-primary) 18%, transparent); color: var(--color-primary); }

@media (max-width: 768px) {
  .bancos-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }
  .bancos-total-card {
    padding: 1.1rem;
  }
  .comprobantes-toolbar-acciones { margin-left: 0; width: 100%; }
}
</style>
