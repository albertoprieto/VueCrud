<template>
  <div class="asignaciones-lista">
    <h2>Asignaciones a Técnicos</h2>
    <div class="filtros">
      <Dropdown
        v-model="tecnicoFiltro"
        :options="tecnicos"
        optionLabel="tecnico"
        optionValue="tecnico"
        placeholder="Filtrar por técnico"
        class="mr-2"
        showClear
      />
      <Dropdown
        v-model="clienteFiltro"
        :options="clientes"
        optionLabel="cliente"
        optionValue="cliente"
        placeholder="Filtrar por cliente"
        class="mr-2"
        showClear
      />
      <InputText
        v-model="busqueda"
        placeholder="Buscar..."
        class="mr-2"
      />
    </div>
    <DataTable :value="asignacionesFiltradas" :loading="loading" responsiveLayout="scroll">
      <Column field="fecha_servicio" header="Fecha de Servicio" sortable />
      <Column field="tecnico" header="Técnico" sortable />
      <Column field="venta_id" header="Nota de Venta" sortable />
      <Column field="cliente" header="Cliente" sortable />
      <Column header="Acciones">
        <template #body="slotProps">
          <Button label="Ver Detalle" icon="pi pi-search" class="mr-2" @click="verDetalle(slotProps.data)" />
          <Button
            label="Agregar Reporte"
            icon="pi pi-plus"
            class="p-button-success"
            @click="irReporteServicio(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
    <Dialog v-model:visible="showDialog" header="Resumen de Asignación" :modal="true">
      <div v-if="asignacionSeleccionada">
        <p><b>Técnico:</b> {{ asignacionSeleccionada.tecnico }}</p>
        <p><b>Fecha de servicio:</b> {{ asignacionSeleccionada.fecha_servicio }}</p>
        <p><b>Nota de venta:</b> {{ asignacionSeleccionada.venta_id }}</p>
        <p v-if="asignacionSeleccionada.cliente"><b>Cliente:</b> {{ asignacionSeleccionada.cliente }}</p>
      </div>
      <template #footer>
        <Button label="Ver Detalle" icon="pi pi-search" @click="irDetalle" />
        <Button label="Cerrar" icon="pi pi-times" class="p-button-secondary" @click="showDialog = false" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { getClientes } from '@/services/clientesService';

const asignaciones = ref([]);
const loading = ref(false);
const showDialog = ref(false);
const asignacionSeleccionada = ref(null);
const tecnicoFiltro = ref(null);
const clienteFiltro = ref(null);
const busqueda = ref('');
const router = useRouter();

const tecnicos = ref([]);
const clientes = ref([]);
const clientesMap = ref({});

onMounted(async () => {
  loading.value = true;
  const [asignacionesRaw, clientesRaw] = await Promise.all([
    getAsignacionesTecnicos(),
    getClientes()
  ]);
  // Mapea id -> nombre para clientes
  clientesMap.value = Object.fromEntries(clientesRaw.map(c => [c.id, c.nombre]));
  asignaciones.value = asignacionesRaw.map(a => ({
    ...a,
    cliente: clientesMap.value[a.cliente_id] || a.cliente_nombre || a.cliente_id || '',
    tecnico: a.tecnico || a.tecnico_nombre || ''
  }));
  tecnicos.value = [...new Set(asignaciones.value.map(a => a.tecnico).filter(Boolean))].map(t => ({ tecnico: t }));
  clientes.value = [...new Set(asignaciones.value.map(a => a.cliente).filter(Boolean))].map(c => ({ cliente: c }));
  loading.value = false;
});

const asignacionesFiltradas = computed(() => {
  let lista = [...asignaciones.value];
  if (tecnicoFiltro.value) {
    lista = lista.filter(a => a.tecnico === tecnicoFiltro.value);
  }
  if (clienteFiltro.value) {
    lista = lista.filter(a => a.cliente === clienteFiltro.value);
  }
  if (busqueda.value) {
    const b = busqueda.value.toLowerCase();
    lista = lista.filter(a =>
      (a.tecnico && a.tecnico.toLowerCase().includes(b)) ||
      (a.cliente && a.cliente.toLowerCase().includes(b)) ||
      (a.venta_id && String(a.venta_id).includes(b)) ||
      (a.fecha_servicio && a.fecha_servicio.includes(b))
    );
  }
  return lista.sort((a, b) => new Date(a.fecha_servicio) - new Date(b.fecha_servicio));
});

function verDetalle(asignacion) {
  asignacionSeleccionada.value = asignacion;
  showDialog.value = true;
}
function irDetalle() {
  showDialog.value = false;
  router.push(`/asignacion/${asignacionSeleccionada.value.id}`);
}
function irReporteServicio(asignacion) {
  router.push(`/reporte-servicio/${asignacion.id}`);
}
</script>

<style scoped>
.asignaciones-lista {
  max-width: 1000px;
  margin: 2rem auto;
  background: var(--color-bg, #23272f);
  color: var(--color-text, #e4c8c8);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.filtros {
  display: flex;
  align-items: center;
  margin-bottom: 1.5rem;
  flex-wrap: wrap;
}
.mr-2 {
  margin-right: 1rem;
}
</style>