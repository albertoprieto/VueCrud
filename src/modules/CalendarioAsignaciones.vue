<template>
  <div class="asignaciones-lista">
    <h2>Asignaciones a Técnicos</h2>
    <div class="filtros">
      <AutoComplete
        v-model="tecnicoFiltro"
        :suggestions="tecnicosFiltrados"
        @complete="buscarTecnico"
        optionLabel="tecnico"
        placeholder="Filtrar por técnico"
        class="mr-2"
        :dropdown="true"
        forceSelection
        showClear
      />
      <AutoComplete
        v-model="clienteFiltro"
        :suggestions="clientesFiltrados"
        @complete="buscarCliente"
        optionLabel="cliente"
        placeholder="Filtrar por cliente"
        class="mr-2"
        :dropdown="true"
        forceSelection
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
      <Column field="venta_id" header="Nota de Venta" sortable>
        <template #body="slotProps">
          <span v-if="slotProps.data.venta_folio">
            {{ slotProps.data.venta_folio }}
          </span>
          <span v-else>
            {{ slotProps.data.venta_id }}
          </span>
        </template>
      </Column>
      <Column field="cliente" header="Cliente" sortable />
      <Column header="Acciones">
        <template #body="slotProps">
          <!-- <Button
            label="Ver Detalle"
            icon="pi pi-search"
            class="mr-2"
            @click="irDetalleDirecto(slotProps.data)"
          /> -->
          <Button
            label="Agregar Reporte"
            icon="pi pi-plus"
            class="p-button-success mr-2"
            @click="irReporteServicio(slotProps.data)"
          />
          <Button
            label="Descargar Orden"
            icon="pi pi-file-pdf"
            class="p-button-secondary"
            @click="descargarNota(slotProps.data)"
            v-if="slotProps.data.venta_id"
          />
          <!-- <Button
            label="Modificar Orden"
            icon="pi pi-pencil"
            class="p-button-warning ml-2"
            @click="modificarOrden(slotProps.data)"
          /> -->
        </template>
      </Column>
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import AutoComplete from 'primevue/autocomplete';
import InputText from 'primevue/inputtext';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { getClientes } from '@/services/clientesService';
import { getVentas, getDetalleVenta } from '@/services/ventasService';
import { getTodosArticulos } from '@/services/articulosService';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';

const asignaciones = ref([]);
const loading = ref(false);
const tecnicoFiltro = ref(null);
const clienteFiltro = ref(null);
const busqueda = ref('');
const router = useRouter();

const tecnicos = ref([]);
const clientes = ref([]);
const clientesMap = ref({});
const ventasMap = ref({});

const tecnicosFiltrados = ref([]);
const clientesFiltrados = ref([]);

onMounted(async () => {
  loading.value = true;
  const [asignacionesRaw, clientesRaw, ventasRaw] = await Promise.all([
    getAsignacionesTecnicos(),
    getClientes(),
    getVentas()
  ]);
  // Mapea id -> nombre para clientes
  clientesMap.value = Object.fromEntries(clientesRaw.map(c => [c.id, c.nombre]));
  // Mapea id -> folio para ventas
  ventasMap.value = Object.fromEntries(ventasRaw.map(v => [v.id, v.folio]));
  asignaciones.value = asignacionesRaw.map(a => ({
    ...a,
    cliente: clientesMap.value[a.cliente_id] || a.cliente_nombre || a.cliente_id || '',
    tecnico: a.tecnico || a.tecnico_nombre || '',
    venta_folio: ventasMap.value[a.venta_id] || ''
  }));
  tecnicos.value = [...new Set(asignaciones.value.map(a => a.tecnico).filter(Boolean))].map(t => ({ tecnico: t }));
  clientes.value = [...new Set(asignaciones.value.map(a => a.cliente).filter(Boolean))].map(c => ({ cliente: c }));
  loading.value = false;
});

function buscarTecnico(event) {
  const query = event.query?.toLowerCase() || '';
  tecnicosFiltrados.value = tecnicos.value.filter(t =>
    t.tecnico.toLowerCase().includes(query)
  );
}
function buscarCliente(event) {
  const query = event.query?.toLowerCase() || '';
  clientesFiltrados.value = clientes.value.filter(c =>
    c.cliente.toLowerCase().includes(query)
  );
}

const asignacionesFiltradas = computed(() => {
  let lista = [...asignaciones.value];
  if (tecnicoFiltro.value) {
    lista = lista.filter(a => a.tecnico === (tecnicoFiltro.value.tecnico || tecnicoFiltro.value));
  }
  if (clienteFiltro.value) {
    lista = lista.filter(a => a.cliente === (clienteFiltro.value.cliente || clienteFiltro.value));
  }
  if (busqueda.value) {
    const b = busqueda.value.toLowerCase();
    lista = lista.filter(a =>
      (a.tecnico && a.tecnico.toLowerCase().includes(b)) ||
      (a.cliente && a.cliente.toLowerCase().includes(b)) ||
      (a.venta_folio && a.venta_folio.toLowerCase().includes(b)) ||
      (a.venta_id && String(a.venta_id).includes(b)) ||
      (a.fecha_servicio && a.fecha_servicio.includes(b))
    );
  }
  return lista.sort((a, b) => new Date(a.fecha_servicio) - new Date(b.fecha_servicio));
});

function irDetalleDirecto(asignacion) {
  router.push(`/asignacion/${asignacion.id}`);
}
function irReporteServicio(asignacion) {
  router.push(`/reporte-servicio/${asignacion.id}`);
}

async function descargarNota(asignacion) {
  if (!asignacion.venta_id) return;
  loading.value = true;
  const [ventas, clientes, articulos, detalle] = await Promise.all([
    getVentas(),
    getClientes(),
    getTodosArticulos(),
    getDetalleVenta(asignacion.venta_id)
  ]);
  const venta = ventas.find(v => v.id === asignacion.venta_id);
  const cliente = clientes.find(c => c.id === venta.cliente_id) || {};
  const articulosSeleccionados = detalle.map(item => {
    const art = articulos.find(a => a.id === item.articulo_id) || {};
    return {
      ...item,
      sku: art.sku,
      nombre: art.nombre
    };
  });
  loading.value = false;
  await generarNotaVentaPDF({
    venta,
    cliente,
    articulos: articulosSeleccionados,
    empresa: {
      nombre: 'GPSubicacion.com',
      direccion: 'Guadalajara',
      rfc: 'RFC123456'
    }
  });
}

function modificarOrden(asignacion) {
  console.log('Modificar orden de servicio:', asignacion);
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