<template>
  <div class="movimientos-inventario">
    <h2>Movimientos de Inventario</h2>
    <div class="table-actions">
      <InputText v-model="filtroUsuario" placeholder="Filtrar por usuario..." class="p-inputtext-sm" style="max-width:180px;" />
      <InputText v-model="filtroImei" placeholder="Filtrar por IMEI..." class="p-inputtext-sm" style="max-width:180px; margin-left:8px;" />
      <Dropdown
        v-model="filtroEvento"
        :options="eventosDisponibles"
        optionLabel="label"
        optionValue="value"
        placeholder="Filtrar por evento"
        class="p-inputtext-sm"
        style="max-width:180px; margin-left:8px;"
        showClear
      />
      <Button
        icon="pi pi-file-excel"
        class="p-button-success p-button-sm"
        label="Exportar Excel"
        style="margin-left: 1rem"
        @click="exportarMovimientos"
      />
    </div>
    <div class="movimientos-card">
      <DataTable
        :value="movimientosFiltrados"
        :sortField="sortField"
        :sortOrder="sortOrder"
        responsiveLayout="scroll"
        @sort="onSort"
        :loading="loadingMovimientos"
      >
        <Column field="fecha" header="Fecha/Hora" sortable>
          <template #body="slotProps">
            {{ formatearFecha(slotProps.data.fecha) }}
          </template>
        </Column>
        <Column field="usuario" header="Usuario" sortable />
        <Column field="evento" header="Evento" sortable />
        <Column field="articulo_nombre" header="Artículo" sortable />
        <Column field="imei" header="IMEI" sortable />
        <Column field="ubicacion_origen" header="Origen" sortable />
        <Column field="ubicacion_destino" header="Destino" sortable />
        <Column field="motivo" header="Motivo" />
      </DataTable>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getMovimientosInventario } from '@/services/inventarioService';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';

const movimientos = ref([]);
const loadingMovimientos = ref(true);
const filtroUsuario = ref('');
const filtroImei = ref('');
const filtroEvento = ref(null);
const sortField = ref('fecha');
const sortOrder = ref(-1);

const eventosDisponibles = [
  { label: 'Alta', value: 'alta' },
  { label: 'Transferencia', value: 'transferencia' },
  { label: 'Devolución', value: 'devolucion' },
  { label: 'Baja', value: 'baja' },
  // Agrega más eventos según tu sistema
];

const formatearFecha = (fecha) => {
  if (!fecha) return '';
  const d = new Date(fecha);
  return d.toLocaleString('es-MX');
};

const movimientosFiltrados = computed(() => {
  return movimientos.value.filter(m =>
    (!filtroUsuario.value || (m.usuario && m.usuario.toLowerCase().includes(filtroUsuario.value.toLowerCase()))) &&
    (!filtroImei.value || (m.imei && m.imei.toLowerCase().includes(filtroImei.value.toLowerCase()))) &&
    (!filtroEvento.value || m.evento === filtroEvento.value)
  );
});

const onSort = (event) => {
  sortField.value = event.sortField;
  sortOrder.value = event.sortOrder;
};

const exportarMovimientos = () => {
  const data = movimientosFiltrados.value.map(m => ({
    'Fecha/Hora': formatearFecha(m.fecha),
    'Usuario': m.usuario,
    'Evento': m.evento,
    'Artículo': m.articulo_nombre,
    'IMEI': m.imei,
    'Origen': m.ubicacion_origen,
    'Destino': m.ubicacion_destino,
    'Motivo': m.motivo,
  }));
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Movimientos');
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  saveAs(new Blob([excelBuffer], { type: 'application/octet-stream' }), 'movimientos_inventario.xlsx');
};

const loadMovimientos = async () => {
  loadingMovimientos.value = true;
  try {
    movimientos.value = await getMovimientosInventario();
  } finally {
    loadingMovimientos.value = false;
  }
};

onMounted(loadMovimientos);
</script>

<style scoped>
.movimientos-inventario {
  margin: 2rem auto;
  text-align: center;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
  max-width: 1200px;
}
h2 {
  margin-bottom: 2rem;
  color: var(--color-title);
}
.table-actions {
  margin-bottom: 1rem;
  display: flex;
  flex-wrap: wrap;
  justify-content: flex-end;
  gap: 0.5rem;
}
.movimientos-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
:root {
  --color-title: #e91e63;
  --color-card: #fff;
  --color-bg: #f7f7fa;
  --color-text: #222;
}
body.dark,
html.dark {
  --color-title: #ff80ab;
  --color-card: #23232b;
  --color-bg: #181820;
  --color-text: #eee;
}
@media (max-width: 700px) {
  .movimientos-inventario {
    padding: 1rem 0.2rem;
  }
  .movimientos-card {
    padding: 0.5rem;
  }
}
</style>