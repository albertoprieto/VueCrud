<template>
  <div class="bancos-container">
    <h2 class="bancos-title">Bancos — Estado de Cuenta</h2>

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <div class="bancos-total-card">
        <span class="bancos-total-label">Saldo total en bancos</span>
        <span class="bancos-total-valor">{{ formatTotal(totalGeneral) }}</span>
      </div>

      <div class="bancos-grid">
        <button
          v-for="banco in bancos"
          :key="banco.nombre"
          type="button"
          class="banco-card"
          @click="router.push({ name: 'detalle-banco', params: { nombre: banco.nombre } })"
        >
          <span class="banco-nombre">{{ banco.nombre }}</span>
          <span class="banco-saldo">{{ formatTotal(banco.saldo) }}</span>
          <span class="banco-sub">{{ banco.movimientos }} movimiento{{ banco.movimientos === 1 ? '' : 's' }}</span>
          <span v-if="banco.pendiente" class="banco-pendiente">En revisión: -{{ formatTotal(banco.pendiente) }}</span>
        </button>
      </div>
    </template>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import { getNotas, getFacturas } from '@/services/pagosService';
import { getRetiros } from '@/services/bancosService';

const router = useRouter();

const lugaresPago = ['ASP Vianey', 'ASP Renovaciones', 'Comercializadora', 'BBVA PAU', 'Tecnico', 'Oficina', 'Mercadopago'];

const loading = ref(true);
const notas = ref([]);
const facturas = ref([]);
const retiros = ref([]);

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency',
  currency: 'MXN',
  minimumFractionDigits: 2,
  maximumFractionDigits: 2,
});

function formatTotal(value) {
  return formatoMoneda.format(Number(value) || 0);
}

const bancos = computed(() => {
  return lugaresPago.map(nombre => {
    const ingresos = [
      ...notas.value.filter(n => n.lugar_pago === nombre && n.status !== 'cancelado'),
      ...facturas.value.filter(f => f.lugar_pago === nombre && f.status !== 'Cancelado'),
    ];
    const ingresoTotal = ingresos.reduce((acc, r) => acc + (Number(r.total) || 0), 0);

    const retirosBanco = retiros.value.filter(r => r.banco === nombre);
    const aprobados = retirosBanco.filter(r => r.estatus === 'aprobado');
    const pendientes = retirosBanco.filter(r => r.estatus === 'pendiente');
    const retiroAprobadoTotal = aprobados.reduce((acc, r) => acc + (Number(r.monto) || 0), 0);
    const retiroPendienteTotal = pendientes.reduce((acc, r) => acc + (Number(r.monto) || 0), 0);

    return {
      nombre,
      saldo: ingresoTotal - retiroAprobadoTotal,
      movimientos: ingresos.length + retirosBanco.length,
      pendiente: retiroPendienteTotal,
    };
  });
});

const totalGeneral = computed(() => bancos.value.reduce((acc, b) => acc + b.saldo, 0));

async function cargar() {
  loading.value = true;
  try {
    [notas.value, facturas.value, retiros.value] = await Promise.all([
      getNotas(),
      getFacturas(),
      getRetiros(),
    ]);
  } catch {
    notas.value = [];
    facturas.value = [];
    retiros.value = [];
  }
  loading.value = false;
}

onMounted(cargar);
</script>

<style scoped>
.bancos-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  max-width: 1100px;
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
  margin-bottom: 2rem;
  border-radius: 14px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
}
.bancos-total-label {
  font-size: 0.9rem;
  color: var(--color-text);
}
.bancos-total-valor {
  font-size: 2.2rem;
  font-weight: 800;
  color: var(--color-primary);
}
.bancos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(220px, 1fr));
  gap: 1rem;
}
.banco-card {
  display: flex;
  flex-direction: column;
  gap: 0.3rem;
  padding: 1.25rem;
  border-radius: 14px;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  cursor: pointer;
  text-align: left;
  transition: border-color 0.15s, box-shadow 0.15s, transform 0.15s;
}
.banco-card:hover {
  border-color: var(--color-primary);
  box-shadow: 0 4px 16px rgba(0, 0, 0, 0.08);
  transform: translateY(-3px);
}
.banco-nombre {
  font-weight: 700;
  font-size: 1rem;
  color: var(--color-title);
}
.banco-saldo {
  font-weight: 800;
  font-size: 1.5rem;
  color: var(--color-primary);
}
.banco-sub {
  font-size: 0.78rem;
  color: var(--color-text);
}
.banco-pendiente {
  font-size: 0.78rem;
  font-weight: 600;
  color: var(--color-warning);
}
</style>
