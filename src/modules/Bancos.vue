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
          :style="{ '--serie-color': bancoColor(banco.nombre) }"
          @click="router.push({ name: 'detalle-banco', params: { nombre: banco.nombre } })"
        >
          <span class="banco-nombre"><span class="banco-dot"></span>{{ banco.nombre }}</span>
          <span class="banco-saldo">{{ formatTotal(banco.saldo) }}</span>
          <span class="banco-pct">{{ pctBanco(banco.saldo) }}</span>
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

const lugaresPago = ['ASP Renovaciones', 'Comercializadora', 'BBVA PAU', 'Mercadopago'];

// Paleta categórica (identidad fija por banco, no ciclada) — misma que Pagos.vue
const BANCO_COLORES = {
  'ASP Vianey': '#2a78d6',
  'ASP Renovaciones': '#1baf7a',
  'Comercializadora': '#eda100',
  'BBVA PAU': '#008300',
  'Tecnico': '#4a3aa7',
  'Oficina': '#e34948',
  'Mercadopago': '#e87ba4',
};

function bancoColor(nombre) {
  return BANCO_COLORES[nombre] || '#898781';
}

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

function pctBanco(saldo) {
  if (!totalGeneral.value) return '0%';
  return `${((Number(saldo) || 0) / totalGeneral.value * 100).toFixed(1)}%`;
}

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
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 1rem;
}
.banco-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.3rem;
  flex: 1 1 200px;
  max-width: 240px;
  padding: 1.25rem;
  border-radius: 12px;
  border: 1px solid var(--color-border);
  border-top: 3px solid color-mix(in srgb, var(--serie-color, var(--color-border)) 65%, transparent);
  background: var(--color-card);
  cursor: pointer;
  text-align: center;
  box-shadow: var(--shadow-1, 0 1px 3px rgba(0, 0, 0, 0.05));
  transition: transform 0.15s, box-shadow 0.15s, border-color 0.15s;
}
.banco-card:hover {
  border-top-color: var(--serie-color, var(--color-primary));
  box-shadow: var(--shadow-2, 0 8px 20px rgba(0, 0, 0, 0.09));
  transform: translateY(-3px);
}
.banco-nombre {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 700;
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--color-text);
  opacity: 0.75;
}
.banco-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--serie-color, var(--color-border));
  flex-shrink: 0;
}
.banco-saldo {
  font-weight: 800;
  font-size: 1.55rem;
  color: var(--color-title);
}
.banco-pct {
  font-size: 0.78rem;
  font-weight: 700;
  padding: 0.15rem 0.6rem;
  border-radius: 999px;
  background: color-mix(in srgb, var(--serie-color, var(--color-text)) 16%, transparent);
  color: var(--serie-color, var(--color-text));
}
.banco-sub {
  font-size: 0.74rem;
  color: var(--color-text);
  opacity: 0.6;
}
.banco-pendiente {
  font-size: 0.76rem;
  font-weight: 600;
  color: var(--color-warning);
}

@media (max-width: 768px) {
  .bancos-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }

  .bancos-total-card {
    padding: 1.1rem;
  }

  .bancos-grid {
    flex-wrap: nowrap;
    justify-content: flex-start;
    overflow-x: auto;
    scroll-snap-type: x mandatory;
    padding-bottom: 0.4rem;
    margin: 0 -0.25rem;
    padding-left: 0.25rem;
    padding-right: 0.25rem;
  }

  .banco-card {
    flex: 0 0 165px;
    max-width: none;
    scroll-snap-align: start;
  }
}
</style>
