<template>
  <div class="dinero-container">
    <h2>Resumen de Dinero</h2>
    <div class="dinero-dashboard">
      <div class="dinero-card ingreso">
        <h3>Ingresos</h3>
        <p class="dinero-monto">{{ formatoMoneda(totalIngresos) }}</p>
      </div>
      <div class="dinero-card egreso">
        <h3>Egresos</h3>
        <p class="dinero-monto">{{ formatoMoneda(totalEgresos) }}</p>
      </div>
      <div class="dinero-card saldo">
        <h3>Saldo</h3>
        <p class="dinero-monto">{{ formatoMoneda(saldo) }}</p>
      </div>
    </div>
    <h3>Movimientos</h3>
    <DataTable :value="movimientos" :paginator="true" :rows="10" class="dinero-table" :loading="cargando">
      <Column field="fecha" header="Fecha" sortable />
      <Column field="tipo" header="Tipo" sortable />
      <Column field="concepto" header="Concepto" sortable />
      <Column field="monto" header="Monto" :body="formatoMoneda" sortable />
      <Column field="referencia" header="Referencia" />
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import axios from 'axios';

const movimientos = ref([]);
const cargando = ref(false);

const cargarMovimientos = async () => {
  cargando.value = true;
  try {
    // Simulación: reemplaza por tu endpoint real
    const res = await axios.get('https://api.gpsubicacionapi.com/movimientos-dinero');
    movimientos.value = res.data;
  } catch (e) {
    // Datos simulados si el endpoint falla
    movimientos.value = [
      { fecha: '2025-07-01', tipo: 'Ingreso', concepto: 'Venta 001', monto: 5000, referencia: 'Venta #001' },
      { fecha: '2025-07-02', tipo: 'Egreso', concepto: 'Compra insumos', monto: 1200, referencia: 'Factura #A123' },
      { fecha: '2025-07-03', tipo: 'Ingreso', concepto: 'Venta 002', monto: 3500, referencia: 'Venta #002' },
      { fecha: '2025-07-04', tipo: 'Egreso', concepto: 'Pago renta', monto: 2000, referencia: 'Renta Julio' },
      { fecha: '2025-07-05', tipo: 'Ingreso', concepto: 'Abono cliente', monto: 1500, referencia: 'Abono #C456' },
    ];
  }
  cargando.value = false;
};

onMounted(cargarMovimientos);

const totalIngresos = computed(() => movimientos.value.filter(m => m.tipo === 'Ingreso').reduce((acc, m) => acc + Number(m.monto), 0));
const totalEgresos = computed(() => movimientos.value.filter(m => m.tipo === 'Egreso').reduce((acc, m) => acc + Number(m.monto), 0));
const saldo = computed(() => totalIngresos.value - totalEgresos.value);

const formatoMoneda = (valor) => {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(Number(valor) || 0);
};
</script>

<style scoped>
.dinero-container {
  max-width: 900px;
  margin: 2rem auto;
  background: var(--color-bg, #23272f);
  color: var(--color-text, #fff);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.dinero-dashboard {
  display: flex;
  gap: 2rem;
  margin-bottom: 2rem;
}
.dinero-card {
  flex: 1;
  background: #23232b;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  text-align: center;
}
.dinero-card.ingreso { border-left: 6px solid #43a047; }
.dinero-card.egreso { border-left: 6px solid #e53935; }
.dinero-card.saldo { border-left: 6px solid #ffb300; }
.dinero-monto {
  font-size: 2rem;
  font-weight: bold;
  margin: 0.5rem 0 0 0;
}
.dinero-table {
  margin-top: 1rem;
}
</style>
