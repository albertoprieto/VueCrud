<template>
  <div class="bancos-container">
    <h2 class="bancos-title">Bancos</h2>

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <div class="bancos-total-card">
        <span class="bancos-total-label">Saldo total (todos los bancos)</span>
        <span class="bancos-total-valor">{{ formatTotal(saldoGlobal) }}</span>
        <Button label="Agregar ingreso" icon="pi pi-file-import" class="p-button-sm p-button-success" style="margin-top:0.75rem;" @click="abrirNuevoIngreso" />
      </div>

      <div class="bancos-grid">
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
        <label>Fecha de la transacción*</label>
        <Calendar v-model="ingresoFechaDate" dateFormat="dd/mm/yy" showIcon iconDisplay="input" class="w-full" />
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
import { LUGARES_VALIDOS, fetchBancosRaw, buildFilas, calcularSaldoBanco } from '@/composables/useBancosData';
import { crearIngresoBanco } from '@/services/ingresosBancoService';

const toast = useToast();

const loading = ref(true);
const filas = ref([]);
const saldosIncialesPorBanco = ref({});

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2,
});
function formatTotal(value) { return formatoMoneda.format(Number(value) || 0); }
function formatFecha(f) {
  if (!f) return '';
  const [y, m, d] = String(f).slice(0, 10).split('-');
  return `${d}/${m}/${y}`;
}

const tarjetas = computed(() => LUGARES_VALIDOS.map(nombre => ({
  nombre,
  ...calcularSaldoBanco(filas.value, nombre, saldosIncialesPorBanco.value),
})));

const saldoGlobal = computed(() => tarjetas.value.reduce((acc, b) => acc + b.saldo, 0));

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
const ingresoArchivo = ref(null);
const guardandoIngreso = ref(false);

function abrirNuevoIngreso() {
  ingresoForm.value = { banco: '', monto: null, imeis: '', usuario: '', cuenta_origen: '', referencia_comprobante: '', clave_rastreo: '' };
  ingresoFechaDate.value = new Date();
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
      fecha_transaccion: fechaISO(ingresoFechaDate.value), usuario: f.usuario,
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
  color: var(--color-success);
}
.banco-card-saldo.negativo {
  color: var(--color-error);
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
