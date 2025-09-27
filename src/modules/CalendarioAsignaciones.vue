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
              <a :href="normalizedLink(selectedEvent.extendedProps.link_ubicacion)" target="_blank" rel="noopener noreferrer" title="Abrir ubicación">Abrir</a>
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
            <div class="dialog-actions" style="display:flex; gap:1rem; margin-top:1.5rem; flex-wrap:wrap;">
              <template v-if="!reporteDeAsignacion(selectedEvent.extendedProps.asignacion)">
                <Button label="Agregar Reporte" icon="pi pi-plus" class="p-button-success p-button-sm" @click="irReporteServicio(selectedEvent.extendedProps.asignacion)" />
              </template>
              <template v-else>
                <Button label="Consultar Reporte" icon="pi pi-file-pdf" class="p-button-warning p-button-sm" @click="consultarReporte(selectedEvent.extendedProps.asignacion)" />
                <a v-if="reporteDeAsignacion(selectedEvent.extendedProps.asignacion)?.comprobante_path" :href="urlComprobante(reporteDeAsignacion(selectedEvent.extendedProps.asignacion))" target="_blank" rel="noopener noreferrer">
                  <Button label="Ver Comprobante" icon="pi pi-download" class="p-button-secondary p-button-sm" />
                </a>
                <Button label="Eliminar Reporte" icon="pi pi-trash" class="p-button-danger p-button-sm" @click="eliminarReporte(selectedEvent.extendedProps.asignacion)" />
              </template>
              <Button label="Descargar Orden" icon="pi pi-file-pdf" class="p-button-secondary p-button-sm" @click="descargarNota(selectedEvent.extendedProps.asignacion)" v-if="selectedEvent.extendedProps.asignacion?.venta_id" />
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
          <!-- Nueva columna: Ubicación con ícono -->
          <Column header="Ubicación">
            <template #body="slotProps">
              <div v-if="slotProps.data.link_ubicacion" style="display:flex; align-items:center; gap:.5rem;">
                <a :href="normalizedLink(slotProps.data.link_ubicacion)" target="_blank" rel="noopener noreferrer" title="Abrir en Google Maps">
                  <Button icon="pi pi-map-marker" class="p-button-rounded p-button-text p-button-sm" />
                </a>
              </div>
              <span v-else>-</span>
            </template>
          </Column>
          <Column header="Acciones">
            <template #body="slotProps">
              <template v-if="!reporteDeAsignacion(slotProps.data)">
                <Button
                  label="Agregar Reporte"
                  icon="pi pi-plus"
                  class="p-button-success mr-2"
                  @click="irReporteServicio(slotProps.data)"
                />
              </template>
              <template v-else>
                <Button
                  label="Consultar Reporte"
                  icon="pi pi-file-pdf"
                  class="p-button-warning mr-2"
                  @click="consultarReporte(slotProps.data)"
                />
                <a v-if="reporteDeAsignacion(slotProps.data)?.comprobante_path" :href="urlComprobante(reporteDeAsignacion(slotProps.data))" target="_blank" rel="noopener noreferrer">
                  <Button
                    label="Ver Comprobante"
                    icon="pi pi-download"
                    class="p-button-secondary mr-2"
                  />
                </a>
                <Button
                  label="Eliminar Reporte"
                  icon="pi pi-trash"
                  class="p-button-danger mr-2"
                  @click="eliminarReporte(slotProps.data)"
                />
              </template>
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
import axios from 'axios'
import { getTodosReportes } from '@/services/reportesServicio.js'
import { generarReporteServicioPDF } from '@/services/reporteServicioPdfService.js'

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
  console.log('Evento click:', {
    event: info.event,
    extendedProps: info.event.extendedProps,
    asignacion: info.event.extendedProps?.asignacion
  });
  // Usar el objeto de asignación completo si existe, si no, usar extendedProps
  selectedEventData.value = info.event.extendedProps?.asignacion || info.event.extendedProps || {};
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


const acalendarOptions = ref({
  plugins: [dayGridPlugin, timeGridPlugin, interactionPlugin],
  initialView: 'timeGridWeek',
  headerToolbar: {
    left: 'prev,next today',
    center: 'title',
    right: 'dayGridMonth,timeGridWeek,timeGridDay'
  },
  // Configuración específica para vista de semana
  slotDuration: '01:00:00',
  slotMinTime: '06:00:00',
  slotMaxTime: '22:00:00',
  allDaySlot: false, // Ocultar "Todo el día"
  weekends: true,
  editable: false,
  selectable: false,
  events: [],
  eventClick: (info) => {
    // Mostrar información detallada del evento
    console.log('Evento clickeado:', info.event.extendedProps);
  },
  eventContent: (arg) => {
    // Personalizar cómo se ve el evento en el calendario
    return {
      html: `
        <div class="custom-event-content">
          <div class="event-title">${arg.event.title}</div>
          <div class="event-time">${arg.timeText}</div>
          <div class="event-client">${arg.event.extendedProps.cliente}</div>
        </div>
      `
    };
  }
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

const reportes = ref([])
const reportesPorAsignacion = ref({})

async function cargarReportesServicios() {
  try {
    const data = await getTodosReportes()
    reportes.value = Array.isArray(data) ? data : []
    const map = {}
    for (const r of reportes.value) {
      if (r.asignacion_id != null) {
        map[r.asignacion_id] = r
      }
    }
    reportesPorAsignacion.value = map
  } catch (e) {
    // silent
  }
}

function reporteDeAsignacion(asignacion) {
  console.log(asignacion);
  
  if (!asignacion) return null
  return reportesPorAsignacion.value[asignacion.id]
}

function urlComprobante(rep) {
  if (!rep?.comprobante_path) return '#'
  const base = import.meta.env.VITE_API_URL?.replace(/\/$/, '') || ''
  const path = rep.comprobante_path.startsWith('/') ? rep.comprobante_path : `/${rep.comprobante_path}`
  return `${base}${path}`
}

async function consultarReporte(asignacion) {
  const rep = reporteDeAsignacion(asignacion)
  if (!rep) return
  try {
    // Obtener venta y cliente asociados (opcional)
    let venta = null, cliente = null
    if (asignacion.venta_id) {
      const ventas = await getVentas()
      venta = ventas.find(v => v.id === asignacion.venta_id)
      if (venta) {
        const clientes = await getClientes()
        cliente = clientes.find(c => c.id === venta.cliente_id) || null
      }
    }
    const reporteCampos = {
      tipo_servicio: rep.tipo_servicio,
      lugar_instalacion: rep.lugar_instalacion,
      marca: rep.marca,
      submarca: rep.submarca,
      modelo: rep.modelo,
      placas: rep.placas,
      color: rep.color,
      numero_economico: rep.numero_economico,
      modelo_gps: rep.modelo_gps,
      imei: rep.imei,
      sim_serie: rep.sim_serie,
      accesorios: rep.accesorios,
      ubicacion_gps: rep.ubicacion_gps,
      ubicacion_bloqueo: rep.ubicacion_bloqueo,
      observaciones: rep.observaciones,
      subtotal: rep.subtotal,
      total: rep.total,
      forma_pago: rep.forma_pago,
      monto_tecnico: rep.monto_tecnico,
      viaticos: rep.viaticos,
      pagado: rep.pagado,
      nombre_cliente: rep.nombre_cliente,
      nombre_instalador: rep.nombre_instalador
    }
    await generarReporteServicioPDF({ reporte: reporteCampos, venta, cliente, empresa: { nombre: 'GPSubicacion.com' } })
  } catch (e) {
    window.toast && window.toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo generar el PDF', life: 4000 })
  }
}

async function eliminarReporte(asignacion) {
  const rep = reporteDeAsignacion(asignacion)
  if (!rep) return
  if (!confirm('¿Eliminar reporte?')) return
  try {
    await axios.delete(`${import.meta.env.VITE_API_URL}/reportes-servicio/${rep.id}`)
    await cargarReportesServicios()
  } catch (e) {
    window.toast && window.toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar', life: 4000 })
  }
}
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
  
  // CORRECCIÓN PRINCIPAL: Combinar fecha y hora
  events.value = asignaciones.value.map(a => {
    // Combinar fecha_servicio con hora_servicio
    const startDateTime = a.hora_servicio ? `${a.fecha_servicio}T${a.hora_servicio}` : a.fecha_servicio;
    // Calcular end time (asumiendo 1 hora de duración si hay hora_servicio)
    let endDateTime = null;
    if (a.hora_servicio) {
      const [hours, minutes] = a.hora_servicio.split(':');
      const endTime = new Date(`${a.fecha_servicio}T${a.hora_servicio}`);
      endTime.setHours(endTime.getHours() + 1); // Duración de 1 hora
      endDateTime = endTime.toISOString().slice(0, 16).replace('T', ' ');
    }
    return {
      title: a.tecnico ? `Técnico: ${a.tecnico}` : 'Asignación',
      start: startDateTime,
      end: endDateTime,
      description: `Cliente: ${a.cliente || a.cliente_id || ''}\nVenta: ${a.venta_folio || a.venta_id || ''}`,
      id: a.id ?? a.venta_id,
      extendedProps: {
        // Mover propiedades adicionales aquí
        fecha_servicio: a.fecha_servicio,
        hora_servicio: a.hora_servicio,
        direccion: a.direccion,
        link_ubicacion: a.link_ubicacion,
        cliente_info: a.cliente_info,
        venta_id: a.venta_id,
        cliente_id: a.cliente_id,
        tecnico: a.tecnico,
        fecha_venta: a.fecha_venta,
        cliente: a.cliente,
        venta_folio: a.venta_folio,
        asignacion: a // Guardar el objeto original
      }
    }
  });
  calendarOptions.value.events = events.value;
  console.log('Eventos mapeados:', events.value);
  await cargarReportesServicios();
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

function normalizedLink(link) {
  if (!link) return '#';
  const l = String(link).trim();
  // If already has a scheme (http, https, etc.) and is not a geo: URI
  if (/^[a-z]+:\/\//i.test(l) && !/^geo:/i.test(l)) {
    return l;
  }
  // Handle geo:lat,lng
  if (/^geo:/i.test(l)) {
    const m = l.match(/^geo:([\-\d.]+),([\-\d.]+)/i);
    if (m) {
      const q = `${m[1]},${m[2]}`;
      return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(q)}`;
    }
  }
  // If it looks like a Google Maps short link or domain without scheme
  if (/^(www\.|(google\.com\/maps|maps\.google\.com|goo\.gl\/maps|maps\.app\.goo\.gl))/i.test(l)) {
    return `https://${l.replace(/^www\./i, '')}`;
  }
  // If it's plain coordinates
  if (/^-?\d+(?:\.\d+)?\s*,\s*-?\d+(?:\.\d+)?$/.test(l)) {
    return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(l)}`;
  }
  // Fallback: treat as address/query
  return `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(l)}`;
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
.custom-event-content {
  padding: 2px;
  font-size: 11px;
  line-height: 1.2;
}

.event-title {
  font-weight: bold;
  margin-bottom: 2px;
}

.event-time {
  font-size: 10px;
  color: #666;
}

.event-client {
  font-size: 10px;
  color: #444;
}

/* Asegurar que los eventos se vean bien en la vista de semana */
.fc-time-grid-event .fc-content {
  padding: 1px;
}
</style>