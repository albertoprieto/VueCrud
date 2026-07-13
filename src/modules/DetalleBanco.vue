<template>
  <div class="detalle-banco-container">
    <Button icon="pi pi-arrow-left" label="Volver a Bancos" class="p-button-text mb-3" @click="router.push('/bancos')" />

    <div class="dev-banner">
      <i class="pi pi-wrench" />
      <span>Sección en desarrollo — datos y funciones aún en pruebas, pueden cambiar.</span>
    </div>

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <div class="saldo-card">
        <span class="saldo-banco">{{ nombre }}</span>
        <span class="saldo-valor">{{ formatTotal(saldo) }}</span>
        <span v-if="retiroPendienteTotal" class="saldo-pendiente">
          En revisión: -{{ formatTotal(retiroPendienteTotal) }} ({{ retirosPendientes.length }} comprobante{{ retirosPendientes.length === 1 ? '' : 's' }} por aprobar)
        </span>
        <Button
          label="Registrar retiro"
          icon="pi pi-upload"
          class="p-button-danger mt-3"
          @click="abrirRetiroDialog"
        />
      </div>

      <!-- Gráfica ingresos vs retiros por mes -->
      <div class="chart-card">
        <h3>Últimos 6 meses</h3>
        <div class="chart-wrap">
          <svg :viewBox="`0 0 ${chartWidth} ${chartHeight}`" class="chart-svg" preserveAspectRatio="xMidYMid meet">
            <line
              v-for="i in 4" :key="'grid'+i"
              :x1="padLeft" :x2="chartWidth - padRight"
              :y1="padTop + (i-1) * (plotHeight / 3)" :y2="padTop + (i-1) * (plotHeight / 3)"
              class="chart-grid"
            />
            <g v-for="(m, idx) in meses" :key="m.key">
              <rect
                :x="barX(idx) - barW - 2" :y="barY(m.ingreso)"
                :width="barW" :height="plotHeight - (barY(m.ingreso) - padTop)"
                class="bar-ingreso"
              />
              <rect
                :x="barX(idx) + 2" :y="barY(m.retiro)"
                :width="barW" :height="plotHeight - (barY(m.retiro) - padTop)"
                class="bar-retiro"
              />
              <text :x="barX(idx)" :y="chartHeight - 8" text-anchor="middle" class="chart-label">{{ m.label }}</text>
            </g>
          </svg>
        </div>
        <div class="chart-legend">
          <span class="legend-item"><span class="legend-swatch swatch-ingreso"></span>Ingresos</span>
          <span class="legend-item"><span class="legend-swatch swatch-retiro"></span>Retiros</span>
        </div>
      </div>

      <!-- Movimientos -->
      <div class="movimientos-card">
        <h3>Movimientos</h3>
        <DataTable :value="movimientos" responsiveLayout="scroll" :paginator="movimientos.length > 15" :rows="15">
          <Column field="fecha" header="Fecha">
            <template #body="{ data }">{{ formatFecha(data.fecha) }}</template>
          </Column>
          <Column field="tipo" header="Tipo" />
          <Column header="Descripción">
            <template #body="{ data }">{{ data.descripcion }}</template>
          </Column>
          <Column header="Monto">
            <template #body="{ data }">
              <span :class="data.monto >= 0 ? 'monto-positivo' : 'monto-negativo'">
                {{ data.monto >= 0 ? '+' : '' }}{{ formatTotal(data.monto) }}
              </span>
            </template>
          </Column>
          <Column header="Estatus">
            <template #body="{ data }">
              <span v-if="data.estatus" :class="'badge badge-' + badgeClass(data.estatus)">{{ data.estatus }}</span>
              <span v-else style="color:var(--color-border);">—</span>
            </template>
          </Column>
          <Column header="Comprobante">
            <template #body="{ data }">
              <a v-if="data.comprobante_url" :href="data.comprobante_url" target="_blank" rel="noopener noreferrer" class="link-comprobante">
                <i class="pi pi-file" /> Ver
              </a>
            </template>
          </Column>
          <Column v-if="esAdmin" header="Acciones" style="width:220px">
            <template #body="{ data }">
              <div v-if="data.tipo === 'Retiro' && data.estatus === 'pendiente'" style="display:flex;gap:0.5rem;">
                <Button icon="pi pi-check" label="Aprobar" class="p-button-sm p-button-success"
                  :loading="procesandoId === data.id" @click="aprobar(data.id)" />
                <Button icon="pi pi-times" label="Rechazar" class="p-button-sm p-button-danger p-button-outlined"
                  :loading="procesandoId === data.id" @click="rechazar(data.id)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>
    </template>

    <!-- Dialog: registrar retiro -->
    <Dialog v-model:visible="retiroDialogVisible" header="Registrar retiro" :modal="true" :style="{ width: '450px', maxWidth: '95vw' }" :draggable="false">
      <div class="retiro-form">
        <div class="retiro-field">
          <label>Monto a retirar</label>
          <InputNumber v-model="retiroForm.monto" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
        </div>
        <div class="retiro-field">
          <label>Motivo (opcional)</label>
          <InputText v-model="retiroForm.motivo" placeholder="Ej: Pago a proveedor" class="w-full" />
        </div>
        <div class="retiro-field">
          <label>Comprobante</label>
          <input type="file" accept="application/pdf,image/*" @change="onFileChange" />
        </div>
      </div>
      <div style="display:flex;justify-content:flex-end;gap:0.75rem;margin-top:1.25rem;">
        <Button label="Cancelar" class="p-button-text" @click="retiroDialogVisible = false" />
        <Button
          label="Registrar"
          icon="pi pi-upload"
          class="p-button-danger"
          :disabled="!retiroForm.monto || !retiroArchivo"
          :loading="guardandoRetiro"
          @click="confirmarRetiro"
        />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import { getNotas, getFacturas } from '@/services/pagosService';
import { getRetiros, crearRetiro, aprobarRetiro, rechazarRetiro } from '@/services/bancosService';

const props = defineProps({ nombre: { type: String, required: true } });
const route = useRoute();
const router = useRouter();
const toast = useToast();
const loginStore = useLoginStore();

const nombre = computed(() => props.nombre || route.params.nombre);
const esAdmin = computed(() => (loginStore.user?.perfil || '').toLowerCase() === 'admin');

const loading = ref(true);
const notas = ref([]);
const facturas = ref([]);
const retiros = ref([]);
const procesandoId = ref(null);

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2,
});
function formatTotal(value) { return formatoMoneda.format(Number(value) || 0); }
function formatFecha(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
}
function badgeClass(estatus) {
  if (estatus === 'aprobado') return 'success';
  if (estatus === 'rechazado') return 'danger';
  return 'warning';
}

const ingresos = computed(() => {
  const ns = notas.value.filter(n => n.lugar_pago === nombre.value && n.status !== 'cancelado')
    .map(n => ({ id: `nota-${n.id}`, fecha: n.fecha, tipo: 'Ingreso', descripcion: `Nota #${n.id} — ${n.cliente || 'Sin cliente'}`, monto: Number(n.total) || 0 }));
  const fs = facturas.value.filter(f => f.lugar_pago === nombre.value && f.status !== 'Cancelado')
    .map(f => ({ id: `factura-${f.id}`, fecha: f.fecha, tipo: 'Ingreso', descripcion: `Factura #${f.id} — ${f.cliente || 'Sin cliente'}`, monto: Number(f.total) || 0 }));
  return [...ns, ...fs];
});

const retirosBanco = computed(() => retiros.value.filter(r => r.banco === nombre.value));
const retirosPendientes = computed(() => retirosBanco.value.filter(r => r.estatus === 'pendiente'));
const retiroPendienteTotal = computed(() => retirosPendientes.value.reduce((acc, r) => acc + (Number(r.monto) || 0), 0));
const retiroAprobadoTotal = computed(() => retirosBanco.value.filter(r => r.estatus === 'aprobado').reduce((acc, r) => acc + (Number(r.monto) || 0), 0));
const ingresoTotal = computed(() => ingresos.value.reduce((acc, r) => acc + r.monto, 0));
const saldo = computed(() => ingresoTotal.value - retiroAprobadoTotal.value);

const movimientos = computed(() => {
  const retirosMov = retirosBanco.value.map(r => ({
    id: r.id, fecha: r.creado_fecha, tipo: 'Retiro',
    descripcion: r.motivo || 'Retiro de banco',
    monto: -(Number(r.monto) || 0),
    estatus: r.estatus,
    comprobante_url: r.comprobante_url,
  }));
  return [...ingresos.value, ...retirosMov].sort((a, b) => new Date(b.fecha) - new Date(a.fecha));
});

// ── Gráfica: últimos 6 meses ──
const chartWidth = 640;
const chartHeight = 220;
const padLeft = 20, padRight = 20, padTop = 10, padBottom = 30;
const plotHeight = chartHeight - padTop - padBottom;

const meses = computed(() => {
  const hoy = new Date();
  const arr = [];
  for (let i = 5; i >= 0; i--) {
    const d = new Date(hoy.getFullYear(), hoy.getMonth() - i, 1);
    const key = `${d.getFullYear()}-${d.getMonth()}`;
    const label = d.toLocaleDateString('es-MX', { month: 'short' });
    const ingreso = ingresos.value
      .filter(r => { const rd = new Date(r.fecha); return rd.getFullYear() === d.getFullYear() && rd.getMonth() === d.getMonth(); })
      .reduce((acc, r) => acc + r.monto, 0);
    const retiro = retirosBanco.value
      .filter(r => r.estatus === 'aprobado')
      .filter(r => { const rd = new Date(r.creado_fecha); return rd.getFullYear() === d.getFullYear() && rd.getMonth() === d.getMonth(); })
      .reduce((acc, r) => acc + (Number(r.monto) || 0), 0);
    arr.push({ key, label, ingreso, retiro });
  }
  return arr;
});

const maxValor = computed(() => Math.max(1, ...meses.value.map(m => Math.max(m.ingreso, m.retiro))));
const barW = 22;
const groupGap = (chartWidth - padLeft - padRight) / 6;

function barX(idx) { return padLeft + groupGap * idx + groupGap / 2; }
function barY(valor) { return padTop + plotHeight - (valor / maxValor.value) * plotHeight; }

// ── Registrar retiro ──
const retiroDialogVisible = ref(false);
const retiroForm = ref({ monto: null, motivo: '' });
const retiroArchivo = ref(null);
const guardandoRetiro = ref(false);

function abrirRetiroDialog() {
  retiroForm.value = { monto: null, motivo: '' };
  retiroArchivo.value = null;
  retiroDialogVisible.value = true;
}

function onFileChange(event) {
  const files = event?.target?.files;
  retiroArchivo.value = files && files.length ? files[0] : null;
}

async function confirmarRetiro() {
  if (!retiroForm.value.monto || !retiroArchivo.value) return;
  guardandoRetiro.value = true;
  try {
    await crearRetiro({
      banco: nombre.value,
      monto: retiroForm.value.monto,
      motivo: retiroForm.value.motivo,
      archivo: retiroArchivo.value,
    });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Retiro registrado, pendiente de aprobación.', life: 3000 });
    retiroDialogVisible.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo registrar el retiro.', life: 4000 });
  }
  guardandoRetiro.value = false;
}

async function aprobar(id) {
  procesandoId.value = id;
  try {
    await aprobarRetiro(id);
    toast.add({ severity: 'success', summary: 'Aprobado', detail: 'Retiro aprobado correctamente.', life: 3000 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo aprobar el retiro.', life: 4000 });
  }
  procesandoId.value = null;
}

async function rechazar(id) {
  procesandoId.value = id;
  try {
    await rechazarRetiro(id);
    toast.add({ severity: 'success', summary: 'Rechazado', detail: 'Retiro rechazado.', life: 3000 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo rechazar el retiro.', life: 4000 });
  }
  procesandoId.value = null;
}

async function cargar() {
  loading.value = true;
  try {
    [notas.value, facturas.value, retiros.value] = await Promise.all([
      getNotas(),
      getFacturas(),
      getRetiros(nombre.value),
    ]);
  } catch {
    notas.value = [];
    facturas.value = [];
    retiros.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el estado de cuenta.', life: 4000 });
  }
  loading.value = false;
}

onMounted(cargar);
</script>

<style scoped>
.detalle-banco-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  max-width: 1100px;
}
.mb-3 { margin-bottom: 1rem; }
.mt-3 { margin-top: 1rem; }
.dev-banner {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  padding: 0.75rem 1rem;
  margin-bottom: 1.25rem;
  border-radius: 10px;
  background: color-mix(in srgb, var(--color-warning) 18%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-warning) 45%, transparent);
  color: var(--color-warning);
  font-weight: 600;
  font-size: 0.9rem;
}
.dev-banner i {
  font-size: 1.1rem;
}
.saldo-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.35rem;
  padding: 2rem;
  margin-bottom: 1.5rem;
  border-radius: 16px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
}
.saldo-banco {
  font-size: 1.1rem;
  font-weight: 700;
  color: var(--color-title);
}
.saldo-valor {
  font-size: 2.6rem;
  font-weight: 800;
  color: var(--color-primary);
}
.saldo-pendiente {
  font-size: 0.85rem;
  font-weight: 600;
  color: var(--color-warning);
}
.chart-card, .movimientos-card {
  padding: 1.5rem;
  margin-bottom: 1.5rem;
  border-radius: 14px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
}
.chart-card h3, .movimientos-card h3 {
  margin: 0 0 1rem;
  color: var(--color-title);
  font-size: 1rem;
}
.chart-wrap { width: 100%; }
.chart-svg { width: 100%; height: 220px; }
.chart-grid { stroke: var(--color-border); stroke-width: 1; }
.bar-ingreso { fill: var(--color-success); }
.bar-retiro { fill: var(--color-error); }
.chart-label { font-size: 11px; fill: var(--color-text); }
.chart-legend {
  display: flex;
  gap: 1.25rem;
  justify-content: center;
  margin-top: 0.5rem;
}
.legend-item {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.82rem;
  color: var(--color-text);
}
.legend-swatch {
  width: 12px; height: 12px; border-radius: 3px; display: inline-block;
}
.swatch-ingreso { background: var(--color-success); }
.swatch-retiro { background: var(--color-error); }
.monto-positivo { color: var(--color-success); font-weight: 700; }
.monto-negativo { color: var(--color-error); font-weight: 700; }
.link-comprobante { color: var(--color-primary); font-weight: 600; text-decoration: none; }
.badge {
  padding: 0.25rem 0.75rem;
  border-radius: 1rem;
  font-size: 0.85rem;
  font-weight: bold;
}
.badge-success { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-warning { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-danger  { background: color-mix(in srgb, var(--color-error) 20%, transparent); color: var(--color-error); }
.retiro-form {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.retiro-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.35rem;
  font-size: 0.85rem;
}
.w-full { width: 100%; }
</style>
