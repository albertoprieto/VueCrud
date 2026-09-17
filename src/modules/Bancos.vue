<template>
  <div class="bancos-container">
    <h2 class="bancos-title page-title">Bancos</h2>

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <div class="bancos-total-card">
        <span class="bancos-total-label">Saldo total (todos los bancos)</span>
        <span class="bancos-total-valor">{{ formatTotal(saldoGlobal) }}</span>
        <Dropdown v-model="filtroMes" :options="opcionesFiltroMes" optionLabel="label" optionValue="value" placeholder="Mes" style="margin-top:0.75rem;min-width:180px;" />
        <Button label="Agregar ingreso" icon="pi pi-file-import" class="p-button-sm p-button-success" style="margin-top:0.75rem;" @click="abrirNuevoIngreso" />
      </div>

      <div class="buscador-global">
        <i class="pi pi-search" />
        <InputText v-model="busquedaGlobal" placeholder="Buscar por IMEI o usuario en todos los bancos..." class="buscador-global-input" />
      </div>

      <div v-if="busquedaActiva" class="busqueda-banner">
        <span><i class="pi pi-filter" /> Resultados para "{{ busquedaGlobal.trim() }}" — {{ resultadosBusqueda.length }} encontrado{{ resultadosBusqueda.length === 1 ? '' : 's' }}</span>
        <Button label="Quitar búsqueda" icon="pi pi-times" class="p-button-sm p-button-outlined" @click="busquedaGlobal = ''" />
      </div>

      <div v-if="busquedaActiva" class="resultados-card">
        <DataTable :value="resultadosBusqueda" responsiveLayout="scroll" :paginator="resultadosBusqueda.length > 30" :rows="30" dataKey="key">
          <template #empty>Sin resultados para esta búsqueda.</template>
          <Column field="banco" header="Banco" />
          <Column field="tipo" header="Tipo" />
          <Column header="Fecha"><template #body="{ data }">{{ formatFecha(data.fecha) }}</template></Column>
          <Column field="nombre" header="Nombre" />
          <Column field="usuario" header="Usuario" />
          <Column field="imeis" header="IMEIs" />
          <Column header="Monto">
            <template #body="{ data }">
              <span :class="data.monto < 0 ? 'monto-negativo' : 'monto-positivo'">{{ data.monto >= 0 ? '+' : '' }}{{ formatTotal(data.monto) }}</span>
            </template>
          </Column>
          <Column header="Estatus">
            <template #body="{ data }">{{ data.estatus || data.estatusValidacion }}</template>
          </Column>
          <Column header="" style="width:60px">
            <template #body="{ data }">
              <router-link :to="{ name: 'detalle-banco', params: { nombre: data.banco } }" class="p-button p-button-sm p-button-text" title="Ver en su banco">
                <i class="pi pi-arrow-right" />
              </router-link>
            </template>
          </Column>
        </DataTable>
      </div>

      <div v-if="!busquedaActiva" class="bancos-grid">
        <router-link
          v-for="banco in tarjetas"
          :key="banco.nombre"
          :to="{ name: 'detalle-banco', params: { nombre: banco.nombre } }"
          class="banco-card"
        >
          <div class="banco-card-header">
            <i class="pi pi-wallet" />
            <span class="banco-card-nombre">{{ banco.nombre }}</span>
          </div>
          <span class="banco-card-saldo" :class="{ negativo: banco.saldo < 0 }">{{ formatTotal(banco.saldo) }}</span>
          <span class="banco-card-desglose">
            Inicial {{ formatTotal(banco.saldoInicial) }} · Neto {{ formatConSigno(banco.entradasNetas - banco.egresos - banco.retiros) }}
          </span>
          <span v-if="banco.comision" class="banco-card-desglose">Comisión 1%: -{{ formatTotal(banco.comision) }}</span>
          <span v-if="banco.sinValidarCount" class="banco-card-pendiente">
            {{ banco.sinValidarCount }} sin validar ({{ formatTotal(banco.sinValidar) }}) — no suman
          </span>
          <span v-if="banco.pendientesCount" class="banco-card-pendiente">
            {{ banco.pendientesCount }} retiro{{ banco.pendientesCount === 1 ? '' : 's' }} por aprobar (-{{ formatTotal(banco.pendiente) }})
          </span>
          <span class="banco-card-footer">
            {{ banco.totalMovimientos }} movimiento{{ banco.totalMovimientos === 1 ? '' : 's' }}
            <template v-if="banco.ultimaFecha"> · último {{ formatFecha(banco.ultimaFecha) }}</template>
          </span>
        </router-link>
      </div>
    </template>

    <!-- Dialog: agregar ingreso bancario (comprobante primero) — se elige el
         banco aquí, un paso antes de entrar al detalle de un banco en
         particular, porque el operador normalmente no sabe a qué banco cayó
         el pago hasta que ve el comprobante. Se liga a una o varias notas
         después, desde el detalle de la nota (ver DetallePago.vue). -->
    <Dialog v-model:visible="ingresoDialogVisible" header="Agregar ingreso" :modal="true" :style="{ width: '460px', maxWidth: '95vw' }" :draggable="false">
      <div class="form-group">
        <label>Banco*</label>
        <Dropdown v-model="ingresoForm.banco" :options="LUGARES_VALIDOS" placeholder="Selecciona banco" class="w-full" />
      </div>
      <div class="form-group">
        <label>Monto*</label>
        <InputNumber v-model="ingresoForm.monto" mode="currency" currency="MXN" locale="es-MX" class="w-full" />
      </div>
      <div class="form-group">
        <label>IMEI(s)* — separados por coma</label>
        <InputText v-model="ingresoForm.imeis" class="w-full" placeholder="Ej: 359123456789012, 359123456789013" />
      </div>
      <div class="form-group">
        <label>Fecha de whatsapp*</label>
        <Calendar v-model="ingresoFechaDate" dateFormat="dd/mm/yy" showIcon iconDisplay="input" class="w-full" />
      </div>
      <div class="form-group">
        <label>Fecha de la transacción (opcional)</label>
        <Calendar v-model="ingresoFechaRealDate" dateFormat="dd/mm/yy" showIcon iconDisplay="input" showButtonBar class="w-full" />
      </div>
      <div class="form-group">
        <label>Usuario (opcional)</label>
        <InputText v-model="ingresoForm.usuario" class="w-full" />
      </div>
      <p style="margin:0.25rem 0 0.5rem;font-size:0.8rem;opacity:0.75;">Al menos uno de estos tres es obligatorio:</p>
      <div class="form-group">
        <label>Cuenta origen (últimos dígitos)</label>
        <InputText v-model="ingresoForm.cuenta_origen" class="w-full" />
      </div>
      <div class="form-group">
        <label>Referencia de comprobante</label>
        <InputText v-model="ingresoForm.referencia_comprobante" class="w-full" />
      </div>
      <div class="form-group">
        <label>Clave de rastreo (últimos dígitos)</label>
        <InputText v-model="ingresoForm.clave_rastreo" class="w-full" />
      </div>
      <div class="form-group">
        <label>Comprobante (imagen o PDF)*</label>
        <input type="file" accept="application/pdf,image/*" @change="onIngresoFileChange" />
      </div>
      <div class="modal-actions">
        <Button label="Registrar" icon="pi pi-check" :loading="guardandoIngreso" @click="confirmarIngreso" />
        <Button label="Cancelar" class="p-button-secondary" @click="ingresoDialogVisible = false" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import InputNumber from 'primevue/inputnumber';
import Calendar from 'primevue/calendar';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { LUGARES_VALIDOS, fetchBancosRaw, buildFilas, calcularSaldoBanco, mesKey } from '@/composables/useBancosData';
import { crearIngresoBanco } from '@/services/ingresosBancoService';

const toast = useToast();

const loading = ref(true);
const filas = ref([]);
const saldosIncialesPorBanco = ref({});

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2,
});
function formatTotal(value) { return formatoMoneda.format(Number(value) || 0); }
function formatConSigno(value) {
  const n = Number(value) || 0;
  return (n >= 0 ? '+' : '') + formatoMoneda.format(n);
}
function formatFecha(f) {
  if (!f) return '';
  const [y, m, d] = String(f).slice(0, 10).split('-');
  return `${d}/${m}/${y}`;
}

const nombresMes = ['Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio', 'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre'];
const filtroMes = ref(mesKey(new Date()));
const opcionesFiltroMes = computed(() => {
  const keys = [...new Set([mesKey(new Date()), ...filas.value.map(f => mesKey(f.fecha))].filter(Boolean))].sort().reverse();
  return [
    { label: 'Todos los meses', value: 'todos' },
    ...keys.map(k => {
      const [y, m] = k.split('-');
      return { label: `${nombresMes[Number(m) - 1]} ${y}`, value: k };
    }),
  ];
});

const tarjetas = computed(() => {
  const mes = filtroMes.value === 'todos' ? null : filtroMes.value;
  return LUGARES_VALIDOS.map(nombre => ({
    nombre,
    ...calcularSaldoBanco(filas.value, nombre, saldosIncialesPorBanco.value, mes),
  }));
});

const saldoGlobal = computed(() => tarjetas.value.reduce((acc, b) => acc + b.saldo, 0));

const busquedaGlobal = ref('');
const busquedaActiva = computed(() => !!busquedaGlobal.value.trim());
const resultadosBusqueda = computed(() => {
  const q = busquedaGlobal.value.trim().toLowerCase();
  if (!q) return [];
  return filas.value.filter(f =>
    (f.imeis || '').toLowerCase().includes(q) || (f.usuario || '').toLowerCase().includes(q) || (f.nombre || '').toLowerCase().includes(q)
  );
});

async function cargar() {
  loading.value = true;
  try {
    const raw = await fetchBancosRaw();
    filas.value = buildFilas(raw);
    saldosIncialesPorBanco.value = raw.saldosIncialesPorBanco;
  } catch {
    filas.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los bancos.', life: 4000 });
  }
  loading.value = false;
}

onMounted(cargar);

// ── Agregar ingreso bancario (comprobante primero) ── el banco se elige
// aquí porque este es el punto de entrada natural: el operador sube el
// comprobante antes de decidir a qué nota corresponde, y a veces ni siquiera
// sabe de antemano en qué banco cayó hasta que lo ve — no tiene sentido
// pedirle que entre primero al detalle de un banco específico.
const ingresoDialogVisible = ref(false);
const ingresoForm = ref({ banco: '', monto: null, imeis: '', usuario: '', cuenta_origen: '', referencia_comprobante: '', clave_rastreo: '' });
const ingresoFechaDate = ref(new Date());
const ingresoFechaRealDate = ref(null);
const ingresoArchivo = ref(null);
const guardandoIngreso = ref(false);

function abrirNuevoIngreso() {
  ingresoForm.value = { banco: '', monto: null, imeis: '', usuario: '', cuenta_origen: '', referencia_comprobante: '', clave_rastreo: '' };
  ingresoFechaDate.value = new Date();
  ingresoFechaRealDate.value = null;
  ingresoArchivo.value = null;
  ingresoDialogVisible.value = true;
}
function onIngresoFileChange(event) {
  const files = event?.target?.files;
  ingresoArchivo.value = files && files.length ? files[0] : null;
}
function fechaISO(d) {
  const dt = d instanceof Date ? d : new Date(d);
  return `${dt.getFullYear()}-${String(dt.getMonth() + 1).padStart(2, '0')}-${String(dt.getDate()).padStart(2, '0')}`;
}
async function confirmarIngreso() {
  const f = ingresoForm.value;
  if (!f.banco || !f.monto || !f.imeis.trim()) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'Banco, monto e IMEI(s) son obligatorios.', life: 3000 });
    return;
  }
  if (!(f.cuenta_origen.trim() || f.referencia_comprobante.trim() || f.clave_rastreo.trim())) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'Captura al menos: cuenta origen, referencia o clave de rastreo.', life: 3500 });
    return;
  }
  if (!ingresoArchivo.value) {
    toast.add({ severity: 'warn', summary: 'Faltan datos', detail: 'El comprobante (imagen o PDF) es obligatorio.', life: 3000 });
    return;
  }
  guardandoIngreso.value = true;
  try {
    await crearIngresoBanco({
      banco: f.banco, monto: Number(f.monto), imeis: f.imeis,
      fecha_transaccion: fechaISO(ingresoFechaDate.value),
      fecha_transaccion_real: ingresoFechaRealDate.value ? fechaISO(ingresoFechaRealDate.value) : '',
      usuario: f.usuario,
      cuenta_origen: f.cuenta_origen, referencia_comprobante: f.referencia_comprobante,
      clave_rastreo: f.clave_rastreo, comprobante: ingresoArchivo.value,
    });
    toast.add({ severity: 'success', summary: 'Registrado', detail: 'Ingreso registrado.', life: 2500 });
    ingresoDialogVisible.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo registrar el ingreso.', life: 4000 });
  }
  guardandoIngreso.value = false;
}
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

.buscador-global {
  position: relative;
  display: flex;
  align-items: center;
  max-width: 480px;
  margin: 0 auto 1rem;
}
.buscador-global .pi-search {
  position: absolute;
  left: 0.9rem;
  opacity: 0.5;
  pointer-events: none;
}
.buscador-global-input {
  width: 100%;
  padding-left: 2.4rem;
  border-radius: 10px;
}
.busqueda-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 1rem;
  padding: 0.75rem 1.1rem;
  margin-bottom: 1rem;
  border-radius: 12px;
  background: color-mix(in srgb, var(--color-warning) 14%, transparent);
  border: 1px solid var(--color-warning);
  color: var(--color-warning);
  font-weight: 600;
  font-size: 0.9rem;
}
.resultados-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 16px;
  overflow: hidden;
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.05));
}
.monto-negativo { color: var(--color-error); font-weight: 700; }
.monto-positivo { color: var(--color-success); font-weight: 700; }

.bancos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1.25rem;
}
.banco-card {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  padding: 1.5rem;
  border-radius: 16px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.05));
  text-decoration: none;
  color: inherit;
  transition: transform 0.15s ease, box-shadow 0.15s ease, border-color 0.15s ease;
}
.banco-card:hover {
  transform: translateY(-2px);
  border-color: var(--color-primary);
  box-shadow: 0 6px 18px rgba(0, 0, 0, 0.08);
}
.banco-card-header {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  color: var(--color-primary);
}
.banco-card-nombre {
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-title);
}
.banco-card-saldo {
  font-size: 1.9rem;
  font-weight: 800;
  color: var(--color-title);
}
.banco-card-saldo.negativo {
  color: var(--color-error);
}
.banco-card-desglose {
  font-size: 0.76rem;
  color: var(--color-text);
  opacity: 0.7;
}
.banco-card-pendiente {
  font-size: 0.8rem;
  font-weight: 600;
  color: var(--color-warning);
}
.banco-card-footer {
  font-size: 0.78rem;
  color: var(--color-text);
  opacity: 0.65;
  margin-top: auto;
}

@media (max-width: 768px) {
  .bancos-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }
  .bancos-total-card {
    padding: 1.1rem;
  }
}
.form-group { margin-bottom: 1rem; text-align: left; }
.form-group label { display: block; font-weight: 600; margin-bottom: 0.4rem; font-size: 0.85rem; }
.modal-actions { display: flex; gap: 1rem; justify-content: flex-end; padding-top: 0.5rem; }
.w-full { width: 100%; }
</style>
