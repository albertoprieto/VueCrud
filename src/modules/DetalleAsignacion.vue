<template>
  <div class="detalle-asignacion">
    <h2>Detalle de Asignación</h2>
    <div v-if="asignacion">
      <div class="asignacion-info">
        <div>
          <span class="asignacion-label">Técnico:</span>
          <span class="asignacion-value">{{ asignacion.tecnico }}</span>
        </div>
        <div>
          <span class="asignacion-label">Fecha de servicio:</span>
          <span class="asignacion-value">{{ asignacion.fecha_servicio }}</span>
        </div>
        <div>
          <span class="asignacion-label">Nota de venta:</span>
          <span class="asignacion-value">{{ asignacion.venta_id }}</span>
        </div>
        <div>
          <span class="asignacion-label">Cliente:</span>
          <span class="asignacion-value">{{ clienteNombre || asignacion.cliente_id }}</span>
        </div>
      </div>
      <div v-if="ventaDetalle" class="venta-detalle-card">
        <h3>Detalle de la Nota de Venta</h3>
        <div class="venta-detalle-info">
          <div>
            <span class="venta-label">Fecha:</span>
            <span class="venta-value">{{ ventaDetalle.fecha?.split('T')[0] || ventaDetalle.fecha }}</span>
          </div>
          <div>
            <span class="venta-label">Observaciones:</span>
            <span class="venta-value">{{ ventaDetalle.observaciones || 'Sin observaciones' }}</span>
          </div>
          <div>
            <span class="venta-label">Total:</span>
            <span class="venta-value">${{ ventaDetalle.total?.toFixed(2) }}</span>
          </div>
        </div>
        <table class="detalle-table">
          <thead>
            <tr>
              <th>Artículo</th>
              <th>Cantidad</th>
              <th>Precio Unitario</th>
              <th>Subtotal</th>
              <th v-if="detalleVenta && detalleVenta.some(i => i.imei)">IMEI</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="item in detalleVenta" :key="item.id">
              <td>{{ item.articulo_nombre }}</td>
              <td>{{ item.cantidad }}</td>
              <td>${{ Number(item.precio_unitario).toFixed(2) }}</td>
              <td>${{ (item.cantidad * item.precio_unitario).toFixed(2) }}</td>
              <td v-if="item.imei">{{ item.imei }}</td>
            </tr>
          </tbody>
        </table>
      </div>
      <Button
        v-if="puedeReportar"
        label="Generar Reporte de Servicio"
        icon="pi pi-file-edit"
        class="p-button-success"
        @click="irAReporte"
      />
      <ReporteServicio
        v-if="showReporteDialog"
        :asignacionId="asignacion.id"
        :visible="showReporteDialog"
        @update:visible="showReporteDialog = $event"
        @close="showReporteDialog = false"
        @saved="onReporteGuardado"
      />
      <div v-if="reporteServicio">
        <h3>Reporte de Servicio</h3>
        <p><b>Descripción:</b> {{ reporteServicio.descripcion }}</p>
        <p><b>Observaciones:</b> {{ reporteServicio.observaciones }}</p>
        <p><b>Fecha de reporte:</b> {{ reporteServicio.fecha }}</p>
      </div>
    </div>
    <Button label="Regresar" icon="pi pi-arrow-left" @click="$router.back()" class="btn-regresar" />
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { getDetalleVenta, getVentas } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import Button from 'primevue/button';
import ReporteServicio from './ReporteServicio.vue';
import { getReportePorAsignacion } from '@/services/reportesServicio';

const route = useRoute();
const router = useRouter();
const asignacion = ref(null);
const ventaDetalle = ref(null);
const detalleVenta = ref([]);
const clienteNombre = ref('');
const reporteServicio = ref(null);
const showReporteDialog = ref(false);

const puedeReportar = computed(() => {
  return (
    asignacion.value &&
    // asignacion.value.tecnico_id === userId &&   <--- solo el tecnico
    new Date(asignacion.value.fecha_servicio) <= new Date() &&
    !reporteServicio.value
  );
});

async function onReporteGuardado() {
  reporteServicio.value = await getReportePorAsignacion(asignacion.value.id);
}

function irAReporte() {
  showReporteDialog.value = true;
}

onMounted(async () => {
  const asignaciones = await getAsignacionesTecnicos();
  asignacion.value = asignaciones.find(a => a.id == route.params.id);

  if (asignacion.value?.venta_id) {
    // Obtener info general de la venta
    const ventas = await getVentas();
    ventaDetalle.value = ventas.find(v => v.id == asignacion.value.venta_id) || {};
    // Obtener detalle de artículos
    detalleVenta.value = await getDetalleVenta(asignacion.value.venta_id);
  }
  // Obtener nombre del cliente
  if (asignacion.value?.cliente_id) {
    const clientes = await getClientes();
    const cliente = clientes.find(c => c.id == asignacion.value.cliente_id);
    clienteNombre.value = cliente ? cliente.nombre : '';
  }
  reporteServicio.value = await getReportePorAsignacion(asignacion.value.id);
});
</script>

<style scoped>
.detalle-asignacion {
  max-width: 700px;
  margin: 2rem auto;
  background: var(--color-bg, #23272f);
  color: var(--color-text, #fff);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 2.5rem 2rem;
}
h2 {
  color: var(--color-title, #ff4081);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2.1rem;
  font-weight: bold;
  letter-spacing: 1px;
}
.asignacion-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem 2.5rem;
  margin-bottom: 2.2rem;
  font-size: 1.1em;
}
.asignacion-label {
  font-weight: 600;
  color: var(--color-title, #ff4081);
  margin-right: 0.4em;
}
.asignacion-value {
  font-weight: 400;
  color: var(--color-text, #fff);
}
.venta-detalle-card {
  background: var(--color-card, #292d36);
  border-radius: 12px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
  padding: 1.5rem 1rem 2rem 1rem;
  margin-bottom: 2rem;
}
.venta-detalle-info {
  display: flex;
  flex-wrap: wrap;
  gap: 1.2rem 2.5rem;
  margin-bottom: 1.5rem;
  font-size: 1.05em;
}
.venta-label {
  font-weight: 600;
  color: var(--color-title, #ff4081);
  margin-right: 0.4em;
}
.venta-value {
  font-weight: 400;
  color: var(--color-text, #fff);
}
.detalle-table {
  width: 100%;
  border-collapse: collapse;
  margin-top: 1rem;
  background: var(--color-card, #292d36);
  border-radius: 8px;
  overflow: hidden;
  box-shadow: 0 2px 8px rgba(0,0,0,0.05);
  color: var(--color-text, #fff);
}
.detalle-table th, .detalle-table td {
  padding: 0.7em 1em;
  text-align: left;
  border-bottom: 1px solid var(--color-border, #444);
}
.detalle-table th {
  background: var(--color-bg, #23272f);
  color: var(--color-title, #ff4081);
  font-weight: 600;
  font-size: 1.05em;
}
.detalle-table tr:last-child td {
  border-bottom: none;
}
.btn-regresar {
  margin-top: 2rem;
  display: block;
  margin-left: auto;
  margin-right: auto;
  min-width: 180px;
}
</style>