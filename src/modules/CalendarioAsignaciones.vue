<template>
  <div class="asignaciones-lista">
    <h2>Asignaciones a Técnicos</h2>
    <div style="display:flex; justify-content:flex-end; margin-bottom:1rem; gap:1rem;">
      <Button
        label="Vista Calendario"
        icon="pi pi-calendar"
        class="p-button-text"
        :class="{ 'p-button-outlined': vistaActual === 'calendario' }"
        @click="vistaActual = 'calendario'"
      />
      <Button
        label="Vista Lista"
        icon="pi pi-list"
        class="p-button-text"
        :class="{ 'p-button-outlined': vistaActual === 'lista' }"
        @click="vistaActual = 'lista'"
      />
    </div>
    <transition name="fade" mode="out-in">
      <div v-if="vistaActual === 'calendario'" key="calendario">
        <FullCalendar :options="calendarOptions" />
        <Dialog v-model:visible="showDialog" :header="dialogTitle" :modal="true" :closable="true" :style="{ width: '420px' }">
          <div v-if="selectedEvent">
            <div class="dialog-section">
              <strong>Técnico:</strong> {{ selectedEvent.extendedProps?.tecnico || '-' }}
            </div>
            <div class="dialog-section">
              <strong>Cliente:</strong> {{ selectedEvent.extendedProps?.cliente || selectedEvent.extendedProps?.cliente_id || '-' }}
            </div>
            <div class="dialog-section">
              <strong>Nota de Venta:</strong> {{ selectedEvent.extendedProps?.venta_folio || selectedEvent.extendedProps?.venta_id || '-' }}
            </div>
            <div class="dialog-section">
              <strong>Fecha de Servicio:</strong> {{ selectedEvent.startStr?.slice(0,10) || '-' }}
            </div>
            <div class="dialog-section">
              <strong>Descripcion:</strong> {{ selectedEvent.extendedProps?.descripcion || 'Sin descripción' }}
            </div>
            <div class="dialog-section" v-if="selectedEvent.extendedProps?.hora_servicio">
              <strong>Hora Servicio:</strong> {{ selectedEvent.extendedProps.hora_servicio }}
            </div>
            <div class="dialog-section" v-if="selectedEvent.extendedProps?.direccion">
              <strong>Dirección:</strong> {{ selectedEvent.extendedProps.direccion }}
            </div>
            <div class="dialog-section" v-if="selectedEvent.extendedProps?.cp">
              <strong>CP:</strong> {{ selectedEvent.extendedProps.cp }}
            </div>
            <div class="dialog-section" v-if="selectedEvent.extendedProps?.link_ubicacion">
              <strong>Link:</strong>
              <a :href="selectedEvent.extendedProps.link_ubicacion" target="_blank">Abrir</a>
            </div>
            <div class="dialog-section" v-if="parsedClienteInfo">
              <strong>Cliente Info:</strong>
              <ul style="margin:.25rem 0 0 .75rem; padding:0; list-style:disc;">
                <li v-if="parsedClienteInfo.telefonos">Tel: {{ parsedClienteInfo.telefonos }}</li>
                <li v-if="parsedClienteInfo.usuario">Usuario: {{ parsedClienteInfo.usuario }}</li>
                <li v-if="parsedClienteInfo.plataforma">Plataforma: {{ parsedClienteInfo.plataforma }}</li>
                <li v-if="parsedClienteInfo.descripcion">Desc: {{ parsedClienteInfo.descripcion }}</li>
              </ul>
            </div>
            <div class="dialog-actions" style="display:flex; gap:1rem; margin-top:1.5rem;">
              <Button label="Agregar Reporte" icon="pi pi-plus" class="p-button-success p-button-sm" @click="irReporteServicio(selectedEvent.extendedProps)" />
              <Button label="Descargar Orden" icon="pi pi-file-pdf" class="p-button-secondary p-button-sm" @click="descargarNota(selectedEventData)" v-if="selectedEventData.venta_id" />
            </div>
          </div>
        </Dialog>
      </div>
      <div v-else key="lista">
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
          <Button icon="pi pi-search" class="p-button-text" @click="abrirTecladoBusquedaCliente" />
          <InputText
            v-model="busqueda"
            placeholder="Buscar..."
            class="mr-2"
          />
        </div>
        <DataTable :value="asignacionesFiltradasOrdenadas" :loading="loading" responsiveLayout="scroll">
          <Column field="fecha_servicio" header="Fecha" sortable />
          <Column field="hora_servicio" header="Hora" sortable />
          <Column field="tecnico" header="Técnico" sortable />
          <Column field="cliente" header="Cliente" sortable />
          <Column field="direccion" header="Dirección" />
          <Column header="Acciones">
            <template #body="slotProps">
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
            </template>
          </Column>
        </DataTable>
      </div>
    </transition>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch, defineProps } from 'vue';
import { useRouter } from 'vue-router';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import AutoComplete from 'primevue/autocomplete';
import InputText from 'primevue/inputtext';
import FullCalendar from '@fullcalendar/vue3';
import dayGridPlugin from '@fullcalendar/daygrid';
import timeGridPlugin from '@fullcalendar/timegrid';
import interactionPlugin from '@fullcalendar/interaction';
import esLocale from '@fullcalendar/core/locales/es';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { getClientes } from '@/services/clientesService';
import { getVentas, getDetalleVenta } from '@/services/ventasService';
import { getTodosArticulos } from '@/services/articulosService';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';
import Dialog from 'primevue/dialog';
import { useLoginStore } from '@/stores/loginStore';

const props = defineProps({
  vista: {
    type: String,
    default: 'tabla',
  },
});
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

function handleEventClick(info) {
  selectedEvent.value = info.event;
  dialogTitle.value = info.event.title;
  selectedEventData.value = info.event.extendedProps;
  const raw = info.event.extendedProps?.cliente_info;
  if (raw) {
    try {
      parsedClienteInfo.value = typeof raw === 'string' ? JSON.parse(raw) : raw;
    } catch (e) {
      parsedClienteInfo.value = null;
    }
  } else {
    parsedClienteInfo.value = null;
  }
  showDialog.value = true;
}

const calendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'dayGridMonth',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay',
  },
  events: [],
  eventClick: handleEventClick,
  height: 'auto',
  locale: esLocale,
  selectable: true,
  editable: false,
});
const events = ref([]);
const showDialog = ref(false);
const selectedEvent = ref(null);
const dialogTitle = ref('Detalle de Asignación');
const selectedEventData = ref({});
const parsedClienteInfo = ref(null);

const loginStore = useLoginStore();
const user = computed(() => loginStore.user || {});

const vistaActual = ref('lista'); // Por defecto entra la vista lista

const asignacionesFiltradasOrdenadas = computed(() => {
  let lista = [...asignacionesFiltradas.value];
  lista.sort((a, b) => {
    const fechaA = new Date(a.fecha_servicio + (a.hora_servicio ? 'T' + a.hora_servicio : ''));
    const fechaB = new Date(b.fecha_servicio + (b.hora_servicio ? 'T' + b.hora_servicio : ''));
    return fechaA - fechaB;
  });
  return lista;
});

onMounted(async () => {
  loading.value = true;
  const [asignacionesRaw, clientesRaw, ventasRaw] = await Promise.all([
    getAsignacionesTecnicos(),
    getClientes(),
    getVentas()
  ]);
  clientesMap.value = Object.fromEntries(clientesRaw.map(c => [c.id, c.nombre]));
  ventasMap.value = Object.fromEntries(ventasRaw.map(v => [v.id, v.folio]));
  let todasAsignaciones = asignacionesRaw.map(a => ({
    ...a,
    cliente: clientesMap.value[a.cliente_id] || a.cliente_nombre || a.cliente_id || '',
    tecnico: a.tecnico || a.tecnico_nombre || '',
    venta_folio: ventasMap.value[a.venta_id] || ''
  }));
  // Filtrar por técnico si el usuario es técnico
  if (user.value.perfil === 'Tecnico') {
    todasAsignaciones = todasAsignaciones.filter(a => {
      // Comparar por username o nombre según cómo se guarde el técnico
      return (
        (a.tecnico && a.tecnico.toLowerCase() === (user.value.username || '').toLowerCase()) ||
        (a.tecnico_nombre && a.tecnico_nombre.toLowerCase() === (user.value.username || '').toLowerCase())
      );
    });
  }
  asignaciones.value = todasAsignaciones;
  tecnicos.value = [...new Set(asignaciones.value.map(a => a.tecnico).filter(Boolean))].map(t => ({ tecnico: t }));
  clientes.value = [...new Set(asignaciones.value.map(a => a.cliente).filter(Boolean))].map(c => ({ cliente: c }));
  loading.value = false;
  events.value = asignaciones.value.map(a => ({
    title: a.tecnico ? `Técnico: ${a.tecnico}` : 'Asignación',
    start: a.fecha_servicio,
    description: `Cliente: ${a.cliente || a.cliente_id || ''}\nVenta: ${a.venta_folio || a.venta_id || ''}`,
    id: a.id ?? a.venta_id,
    ...a
  }));
  calendarOptions.value.events = events.value;
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
  const id = asignacion.id ?? asignacion.venta_id;
  // No validar si ya existe reporte, solo navegar
  if (props.onAgregarReporte) {
    props.onAgregarReporte(id);
  } else {
    router.push(`/reporte-servicio/${id}`);
  }
}
async function descargarNota(asignacion) {
  if (!asignacion.venta_id) return;
  loading.value = true;
  try {
    // 1. Obtener venta
    const ventas = await getVentas();
    const venta = ventas.find(v => v.id === asignacion.venta_id);
    if (!venta) throw new Error('No se encontró la venta');
    // 2. Obtener detalle y cliente
    const detalle = await getDetalleVenta(venta.id);
    const clientes = await getClientes();
    const cliente = clientes.find(c => c.id === venta.cliente_id) || {};
    // 3. Artículos seleccionados igual que HistoricoNotasVenta
    const articulos = await getTodosArticulos();
    const articulosSeleccionados = detalle.map(item => {
      const art = articulos.find(a => a.id === item.articulo_id) || {};
      return {
        ...item,
        sku: art.sku,
        nombre: art.nombre
      };
    });
    // 4. Obtener asignación actual desde backend
    let asignacionBackend = null;
    try {
      const { getAsignacionVenta } = await import('@/services/asignacionesService');
      asignacionBackend = await getAsignacionVenta(venta.id);
    } catch (e) {
      // Si no existe, ignora
    }
    // 5. Construir payload igual que HistoricoNotasVenta
    const empresa = {
      nombre: 'GPSubicacion.com',
      direccion: 'Guadalajara',
      rfc: 'RFC123456'
    };
    const payload = {
      venta: { ...venta, ...(asignacionBackend || {}) },
      cliente,
      articulos: articulosSeleccionados,
      empresa
    };
    // 6. Generar PDF
    await generarNotaVentaPDF(payload);
  } catch (e) {
    window.toast && window.toast.add({ severity: 'error', summary: 'Error PDF', detail: String(e), life: 5000 });
  } finally {
    loading.value = false;
  }
}

function modificarOrden(asignacion) {
  //
}

function abrirTecladoBusquedaCliente() {
  window.scrollTo(0, 0);
  document.querySelector('input[placeholder="Filtrar por cliente"]')?.focus();
}
</script>

<style scoped>
.asignaciones-lista {
  max-width: 1000px;
  margin: 2rem auto;
  background: var(--color-bg);
  color: var(--color-text);
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
.fade-enter-active, .fade-leave-active {
  transition: opacity 0.3s;
}
.fade-enter-from, .fade-leave-to {
  opacity: 0;
}
</style>