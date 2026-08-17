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
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useToast } from 'primevue/usetoast';
import { LUGARES_VALIDOS, fetchBancosRaw, buildFilas, calcularSaldoBanco } from '@/composables/useBancosData';

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
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()}`;
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
</style>
