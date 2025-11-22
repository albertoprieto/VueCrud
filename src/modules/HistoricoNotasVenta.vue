<template>
  <div class="historico-notas-container">
    <h2 class="historico-title">Consultar Orden de Servicio</h2>
    <!-- Agrega esto antes del DataTable -->
    <div class="filtros" style="display: flex; gap: 1rem; margin-bottom: 1.5rem; flex-wrap: wrap;">
      <InputText v-model="filtroFolio" placeholder="Buscar por folio..." class="filtro-input" clearable />
      <Dropdown
        v-model="filtroCliente"
        :options="clientesUnicos"
        placeholder="Filtrar por cliente"
        class="filtro-dropdown"
        showClear
        filter
      />
      <Dropdown
        v-model="filtroTecnico"
        :options="tecnicosUnicos"
        placeholder="Filtrar por asignado a"
        class="filtro-dropdown"
        showClear
        filter
      />
      <Dropdown
        v-model="filtroStatus"
        :options="statusUnicos"
        placeholder="Filtrar por status"
        class="filtro-dropdown"
        showClear
        filter
      />
      <Dropdown
        v-model="filtroTerminosPago"
        :options="terminosPagoUnicos"
        placeholder="Filtrar por términos de pago"
        class="filtro-dropdown"
        showClear
        filter
      />
      <!-- <Calendar
        v-model="filtroFecha"
        selectionMode="range"
        dateFormat="yy-mm-dd"
        placeholder="Filtrar por fecha"
        class="filtro-calendar"
        showIcon
      /> -->
      <InputText v-model="filtroImei" placeholder="Buscar por IMEI..." class="filtro-input" clearable />
      <Button label="Limpiar" icon="pi pi-times" class="p-button-secondary" @click="() => {
        filtroFolio = '';
        filtroCliente = '';
        filtroTecnico = '';
        filtroStatus = '';
        filtroTerminosPago = '';
        filtroFecha = [];
        filtroImei = '';
      }" />
    </div>
    <DataTable
      :value="ventasFiltradas"
      :loading="loading"
      responsiveLayout="scroll"
      class="historico-table"
    >
      <Column field="folio" header="Folio" />
      <Column field="cliente_nombre" header="Cliente" />
      <Column field="tecnicoNombre" header="Asignado a">
        <template #body="slotProps">
          <span v-if="slotProps.data.tecnicoNombre" class="chip chip-asignado">
            {{ slotProps.data.tecnicoNombre }}
          </span>
          <span v-else class="chip chip-sinasignar">Sin asignar</span>
        </template>
      </Column>
      <Column field="status" header="Status">
        <template #body="slotProps">
          <span
            class="chip"
            :class="{
              'chip-asignado': slotProps.data.tecnicoNombre,
              'chip-sinasignar': !slotProps.data.tecnicoNombre
            }"
          >
            {{ slotProps.data.tecnicoNombre ? 'Asignado' : 'Sin asignar' }}
          </span>
        </template>
      </Column>
        <!-- Columna de atención por reporte de servicio -->
        <Column field="statusAtencion" header="Atención">
          <template #body="slotProps">
            <span :style="{color: slotProps.data.statusAtencion === 'Atendido' ? 'green' : 'orange', fontWeight: 'bold'}">
              {{ slotProps.data.statusAtencion }}
            </span>
          </template>
        </Column>
      <Column field="terminos_pago" header="Términos de Pago">
        <template #body="slotProps">
          {{ slotProps.data.terminos_pago || '-' }}
        </template>
      </Column>
      <Column header="Artículos">
        <template #body="slotProps">
          <Button text raised label="Ver Artículos" icon="pi pi-list" class="p-button-sm p-button-info" @click="verArticulos(slotProps.data)" />
        </template>
      </Column>
      <Column header="Fecha/Hora Servicio">
        <template #body="slotProps">
          <span v-if="slotProps.data.status === 'Asignado'">
            <AsyncAsignacionCell :ventaId="slotProps.data.id" @edit="abrirEditarAsignacion" />
          </span>
          <span v-else>-</span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button
            :icon="slotProps.data.tecnicoNombre ? 'pi pi-user-edit' : 'pi pi-user-plus'"
            :label="slotProps.data.tecnicoNombre ? 'Cambiar técnico' : 'Asignar técnico'"
            class="p-button-sm p-button-info"
            @click="abrirAsignarTecnico(slotProps.data)"
          />
          <Button
            v-if="slotProps.data.tecnicoNombre"
            icon="pi pi-trash"
            label="Eliminar asignación"
            class="p-button-sm p-button-danger ml-2"
            @click="eliminarAsignacion(slotProps.data)"
          />
          <Button
            v-if="slotProps.data.status === 'Asignado'"
            icon="pi pi-file-pdf"
            label="Orden de Servicio"
            class="p-button-sm p-button-success ml-2"
            @click="descargarPDF(slotProps.data)"
          />
          <!-- Nueva acción: descargar constancia fiscal -->
          <a
            v-if="slotProps.data.constancia_path"
            :href="getConstanciaUrl(slotProps.data.constancia_path)"
            download
            class="p-button p-button-sm p-button-warning ml-2"
            :title="slotProps.data.rfc ? 'Descargar Constancia RFC ' + slotProps.data.rfc : 'Descargar constancia fiscal'"
          >
            <i class="pi pi-file-pdf"></i>
            <span class="p-button-label">Constancia Fiscal</span>
          </a>
          <i v-else class="pi pi-file-pdf ml-2" style="opacity:0.25" :title="'Sin constancia'" />
          <Button
            icon="pi pi-times"
            label="Eliminar orden"
            class="p-button-sm p-button-danger ml-2"
            @click="confirmarEliminarOrden(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
    <Dialog v-model:visible="showDialog" header="Nota de Venta" :modal="true" class="historico-dialog">
      <Button label="Cerrar" icon="pi pi-times" @click="showDialog = false" class="mt-3" />
    </Dialog>
    
  <Dialog v-model:visible="showAsignarDialog" header="Asignar Técnico" :modal="true" :closable="false" class="asignar-dialog">
      <form class="asignar-form" @submit.prevent="asignarTecnico">
        <div class="asignar-grid">
          <div class="asignar-col">
            <label>Teléfonos <span class="req">*</span></label>
            <input v-model="ordenClienteInfo.telefonos" required class="asignar-input" placeholder="Teléfonos" />
          </div>
          <div class="asignar-col">
            <label>Usuario(s) <span class="req">*</span></label>
            <input v-model="ordenClienteInfo.usuario" required class="asignar-input" placeholder="Usuario(s)" />
          </div>
        </div>
        <div class="asignar-col">
          <label>Plataforma <span class="req">*</span></label>
          <Dropdown
            v-model="ordenClienteInfo.plataforma"
            :options="plataformasCliente"
            placeholder="Selecciona plataforma"
            class="asignar-input plataforma-dropdown"
            :required="true"
            :invalid="!ordenClienteInfo.plataforma"
          />
        </div>
        <div class="asignar-col">
          <label>Descripción <span class="req">*</span></label>
          <Textarea v-model="ordenClienteInfo.descripcion" required class="asignar-input" placeholder="Descripción" />
        </div>
        <div class="asignar-grid">
          <div class="asignar-col">
            <label>Técnico <span class="req">*</span></label>
            <Dropdown
              v-model="tecnicoSeleccionado"
              :options="tecnicos"
              optionLabel="nombre"
              optionValue="id"
              placeholder="Selecciona técnico"
              class="asignar-input"
              :required="true"
              :invalid="!tecnicoSeleccionado"
            />
          </div>
          <div class="asignar-col">
            <label>Fecha servicio <span class="req">*</span></label>
            <Calendar
              v-model="fechaServicio"
              dateFormat="yy-mm-dd"
              placeholder="Fecha servicio"
              class="asignar-input"
              :required="true"
              :invalid="!fechaServicio"
            />
          </div>
          <div class="asignar-col">
            <label>Hora inicio <span class="req">*</span></label>
            <Calendar
              v-model="horaServicio"
              timeOnly
              hourFormat="24"
              iconDisplay="input"
              placeholder="Hora inicio"
              class="asignar-input"
              :required="true"
              :invalid="!horaServicio"
            />
          </div>
          <div class="asignar-col">
            <label>Hora fin <span class="req">*</span></label>
            <Calendar
              v-model="horaFin"
              timeOnly
              hourFormat="24"
              iconDisplay="input"
              placeholder="Hora fin"
              class="asignar-input"
              :required="true"
              :invalid="!horaFin"
            />
          </div>
        </div>
        <div class="asignar-grid">
          <div class="asignar-col">
            <label>Dirección <span class="req">*</span></label>
            <input v-model="direccionServicio" required class="asignar-input" placeholder="Dirección" />
          </div>
          <div class="asignar-col">
            <label>Código Postal <span class="req">*</span></label>
            <input v-model="cpServicio" required class="asignar-input" placeholder="Código Postal" />
          </div>
          <div class="asignar-col">
            <label>Link Ubicación (Maps) <span class="req">*</span></label>
            <input v-model="linkUbicacion" required class="asignar-input" placeholder="Link Ubicación (Maps)" />
          </div>
        </div>
        <div class="asignar-actions">
          <Button label="Asignar" icon="pi pi-check" type="submit"
            :disabled="!tecnicoSeleccionado || !fechaServicio || !horaServicio || !horaFin || !ordenClienteInfo.plataforma || !ordenClienteInfo.telefonos || !ordenClienteInfo.usuario || !ordenClienteInfo.descripcion || !direccionServicio || !cpServicio || !linkUbicacion"
            class="p-button-success" />
          <Button label="Cancelar" icon="pi pi-times" @click="showAsignarDialog = false" class="p-button-secondary ml-2" />
        </div>
      </form>
    </Dialog>
    <Dialog v-model:visible="showResponseDialog" header="Resultado" :modal="true">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ responseMessage }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="showResponseDialog = false" class="mt-3" />
    </Dialog>
    <Dialog v-model:visible="showArticulosDialog" header="Artículos" :modal="true">
      <div v-if="articulosDialogList && articulosDialogList.length">
        <ul>
          <li v-for="(art, idx) in articulosDialogList" :key="idx">
            {{ art.sku }} - Cantidad: {{ art.cantidad }}
          </li>
        </ul>
      </div>
      <span v-else>No hay artículos para esta venta.</span>
      <Button label="Cerrar" icon="pi pi-times" @click="showArticulosDialog = false" class="mt-3" />
    </Dialog>
    <Dialog v-model:visible="showEliminarDialog" header="¿Eliminar orden de servicio?" :modal="true">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Seguro que deseas eliminar la orden <b>{{ ventaAEliminar?.folio || ventaAEliminar?.id }}</b>?</span>
      </div>
      <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger mt-3" @click="eliminarOrdenConfirmada" />
      <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary mt-3 ml-2" @click="showEliminarDialog = false" />
    </Dialog>
    <Dialog v-model:visible="showEliminarResultado" header="Resultado" :modal="true">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ eliminarResultado }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="showEliminarResultado = false" class="mt-3" />
    </Dialog>
  </div>
</template>

<script setup>
import { computed, ref, onMounted, nextTick } from 'vue';
import { getReportesServicioTodos } from '@/services/reportesService';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Textarea from 'primevue/textarea';
import Divider from 'primevue/divider';
import { getVentas, getDetalleVenta, asignarTecnicoVenta, getTecnicoVenta, deleteAsignacionTecnico, eliminarOrdenServicio } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUsuarios } from '@/services/usuariosService';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';
import { getAsignacionVenta } from '@/services/asignacionesService';
import AsyncAsignacionCell from '@/components/AsyncAsignacionCell.vue';

const ventas = ref([]);
const loading = ref(true);
const showDialog = ref(false);
const ventaSeleccionada = ref(null);
const clienteSeleccionado = ref(null);
const articulosSeleccionados = ref([]);
const empresa = {
  nombre: 'GPSubicacion.com',
  direccion: 'Guadalajara',
  rfc: 'RFC123456'
};
const showAsignarDialog = ref(false);
const ventaParaAsignar = ref(null);
const tecnicos = ref([]);
const tecnicoSeleccionado = ref(null);
const fechaServicio = ref(null); // NUEVO: fecha de servicio
const horaServicio = ref(null); // NUEVO: hora de inicio
const horaFin = ref(null); // NUEVO: hora de fin
// Nuevos campos adicionales
const direccionServicio = ref('');
const cpServicio = ref('');
const linkUbicacion = ref('');
// Eliminados coordLat y coordLng (mapa removido)
// Datos cliente/orden mostrados en dialog
const ordenClienteInfo = ref({ telefonos: '', usuario: '', plataforma: '', descripcion: '' });
const plataformasCliente = ref([]);

function buildOrdenClienteInfo(venta, cliente) {
  const telefonos = Array.isArray(cliente?.telefonos) ? cliente.telefonos.filter(Boolean).join(', ') : (cliente?.telefono || '');
  const usuariosArr = Array.isArray(cliente?.usuarios) ? cliente.usuarios.filter(Boolean) : [];
  const usuario = cliente?.usuario || (usuariosArr.length ? usuariosArr.join(', ') : (cliente?.username || ''));
  const plataformas = Array.isArray(cliente?.plataformas) ? cliente.plataformas.filter(Boolean).join(', ') : (cliente?.plataforma || '');
  const descripcion = venta?.descripcion || venta?.observaciones || venta?.notas_cliente || cliente?.descripcion || '';
  const info = { telefonos, usuario, plataforma: plataformas, descripcion };
  console.log('[DEBUG buildOrdenClienteInfo] info:', info, { venta, cliente });
  return info;
}

// Funciones de mapa eliminadas
const showResponseDialog = ref(false);
const responseMessage = ref('');
const showArticulosDialog = ref(false);
const articulosDialogList = ref([]);

// Debug removido

// Filtros
const filtroFolio = ref('');
const filtroCliente = ref('');
const filtroTecnico = ref('');
const filtroStatus = ref('');
const filtroTerminosPago = ref('');
const filtroFecha = ref([]);
const filtroImei = ref('');

// Cargar ventas y técnicos asignados
onMounted(async () => {
  loading.value = true;
  const [ventasRaw, clientes, reportes] = await Promise.all([
    getVentas(),
    getClientes(),
    getReportesServicioTodos()
  ]);
  // Indexar reportes por folio para búsqueda rápida
  const reportesPorFolio = Array.isArray(reportes)
    ? reportes.reduce((acc, r) => {
        if (r.folio) acc[r.folio] = true;
        return acc;
      }, {})
    : {};
  const ventasConTecnico = await Promise.all(
    ventasRaw.map(async v => {
      const tecnico = await getTecnicoVenta(v.id);
      const cliente = clientes.find(c => c.id === v.cliente_id);
      // Consultar si tiene reporte de servicio asociado por folio
      let statusAtencion = 'No atendido';
      const folioVenta = v.folio ?? v.id;
      if (folioVenta && reportesPorFolio[folioVenta]) {
        statusAtencion = 'Atendido';
      }
      return {
        ...v,
        cliente_nombre: String(v.cliente_nombre ?? ''),
        tecnicoNombre: tecnico ? String(tecnico.username) : '',
        status: tecnico ? 'Asignado' : 'Sin asignar',
        constancia_path: cliente?.constancia_path || null,
        rfc: cliente?.rfc || null,
        statusAtencion // NUEVO
      };
    })
  );
  ventas.value = ventasConTecnico;
  loading.value = false;
});

const clientesUnicos = computed(() => {
  const set = new Set();
  ventas.value.forEach(v => v.cliente_nombre && set.add(v.cliente_nombre));
  return Array.from(set);
});

const tecnicosUnicos = computed(() => {
  const set = new Set();
  ventas.value.forEach(v => v.tecnicoNombre && set.add(v.tecnicoNombre));
  return Array.from(set);
});

const statusUnicos = computed(() => {
  const set = new Set();
  ventas.value.forEach(v => v.status && set.add(v.status));
  return Array.from(set);
});

const terminosPagoUnicos = computed(() => {
  const set = new Set();
  ventas.value.forEach(v => v.terminos_pago && set.add(v.terminos_pago));
  return Array.from(set);
});

const ventasFiltradas = computed(() => {
  return ventas.value.filter(v => {
    const folioBase = v.folio ?? v.id;
    const folioOk = !filtroFolio.value || String(folioBase).toLowerCase().includes(filtroFolio.value.toLowerCase());
    const clienteOk = !filtroCliente.value || v.cliente_nombre === filtroCliente.value;
    const tecnicoOk = !filtroTecnico.value || v.tecnicoNombre === filtroTecnico.value;
    const statusOk = !filtroStatus.value || v.status === filtroStatus.value;
    const terminosOk = !filtroTerminosPago.value || v.terminos_pago === filtroTerminosPago.value;

    // Fecha (rango)
    let fechaOk = true;
    if (filtroFecha.value && filtroFecha.value.length === 2 && filtroFecha.value[0] && filtroFecha.value[1]) {
      const fechaVenta = new Date(v.fecha);
      const desde = new Date(filtroFecha.value[0]);
      const hasta = new Date(filtroFecha.value[1]);
      fechaOk = fechaVenta >= desde && fechaVenta <= hasta;
    }

    // IMEI (en detalle)
    const imeiOk = !filtroImei.value ||
      (v.detalle && v.detalle.some(item =>
        item.imei &&
        (
          item.imei.includes(filtroImei.value) ||
          item.imei.slice(-5) === filtroImei.value
        )
      ));

  return folioOk && clienteOk && tecnicoOk && statusOk && terminosOk && fechaOk && imeiOk;
  });
});

async function descargarPDF(venta) {
  loading.value = true;
  // 1. Obtener detalle de venta y cliente
  const detalle = await getDetalleVenta(venta.id);
  const clientes = await getClientes();
  const cliente = clientes.find(c => c.id === venta.cliente_id) || {};
  const articulos = await getTodosArticulos();
  const articulosSeleccionados = detalle.map(item => {
    const art = articulos.find(a => a.id === item.articulo_id) || {};
    return {
      ...item,
      sku: art.sku,
      nombre: art.nombre
    };
  });
  // 2. Obtener asignación actual desde backend
  let asignacion = null;
  try {
    asignacion = await getAsignacionVenta(venta.id);
    console.log('[DEBUG asignacion backend]', asignacion);
  } catch (e) {
    console.warn('No se pudo obtener asignación actual', e);
  }
  // 3. Construir payload para PDF usando asignacion si existe
  const payload = {
    venta: { ...venta, ...(asignacion || {}) },
    cliente,
    articulos: articulosSeleccionados,
    empresa
  };
  loading.value = false;
  await generarNotaVentaPDF(payload);
}

async function abrirAsignarTecnico(venta) {
  ventaParaAsignar.value = venta;
  const usuarios = await getUsuarios();
  tecnicos.value = usuarios.filter(u => u.perfil === 'Tecnico').map(u => ({
    nombre: u.username,
    id: u.id,
    perfil: u.perfil
  }));
  tecnicoSeleccionado.value = venta.tecnicoAsignado ?? null;
  fechaServicio.value = null; // Limpia la fecha al abrir
  horaServicio.value = null; // Limpia la hora al abrir
  direccionServicio.value = '';
  cpServicio.value = '';
  linkUbicacion.value = '';
  // Intentar obtener info cliente desde la propia venta o refetch de clientes
  try {
    const clientes = await getClientes();
    const cliente = clientes.find(c => String(c.id) === String(venta.cliente_id)) || {};
    // Ya no autocompletamos direccion / cp: el usuario los ingresará manualmente.
    ordenClienteInfo.value = buildOrdenClienteInfo(venta, cliente);
    // Extrae plataformas disponibles del cliente
    plataformasCliente.value = Array.isArray(cliente?.plataformas)
      ? cliente.plataformas.filter(Boolean)
      : cliente?.plataforma
        ? [cliente.plataforma]
        : [];
    // Si hay plataformas, selecciona la primera por defecto
    // if (plataformasCliente.value.length && !ordenClienteInfo.value.plataforma) {
    //   ordenClienteInfo.value.plataforma = plataformasCliente.value[0];
    // }
    console.log(plataformasCliente.value);
    
    console.log('[DEBUG abrirAsignarTecnico] cliente encontrado?', !!cliente.id);
  } catch (e) {
    console.warn('No se pudo cargar info cliente para dialog', e);
  }
  showAsignarDialog.value = true;
  await nextTick();
  console.log('[DEBUG DOM check] Telefonos mostrados:', ordenClienteInfo.value.telefonos);
}

async function asignarTecnico() {
  if (!ventaParaAsignar.value || !tecnicoSeleccionado.value || !fechaServicio.value) return;
  const fechaFormateada = fechaServicio.value instanceof Date
    ? fechaServicio.value.toISOString().slice(0, 10)
    : (typeof fechaServicio.value === 'string' && fechaServicio.value.includes('T'))
      ? fechaServicio.value.split('T')[0]
      : fechaServicio.value;

  const horaFormateada = horaServicio.value instanceof Date
    ? horaServicio.value.toTimeString().slice(0,5)
    : (typeof horaServicio.value === 'string' && horaServicio.value.match(/^[0-9]{2}:[0-9]{2}/))
      ? horaServicio.value.slice(0,5)
      : null;
  const horaFinFormateada = horaFin.value instanceof Date
    ? horaFin.value.toTimeString().slice(0,5)
    : (typeof horaFin.value === 'string' && horaFin.value.match(/^[0-9]{2}:[0-9]{2}/))
      ? horaFin.value.slice(0,5)
      : null;

  const payloadExtendido = {
    tecnico_id: tecnicoSeleccionado.value,
    fecha_servicio: fechaFormateada,
    hora_servicio: horaFormateada || null,
    hora_fin: horaFinFormateada || null,
    direccion: direccionServicio.value?.trim() || null,
    cp: cpServicio.value?.trim() || null,
    link_ubicacion: linkUbicacion.value?.trim() || null,
    cliente_info: ordenClienteInfo.value
  };
  console.log('[ASIGNAR] Payload a enviar =>', payloadExtendido);
  try {
    const resp = await asignarTecnicoVenta(ventaParaAsignar.value.id, tecnicoSeleccionado.value, fechaFormateada, payloadExtendido);
    console.log('[ASIGNAR] Respuesta API', resp?.data ?? resp);
  } catch (err) {
    const apiMsg = err?.response?.data || err.message;
    console.error('[ASIGNAR] Error API', apiMsg, err);
    responseMessage.value = 'Error asignando técnico: ' + (typeof apiMsg === 'string' ? apiMsg : JSON.stringify(apiMsg));
    showResponseDialog.value = true;
    return; // No continuar con actualización local si falló
  }
  const tecnico = tecnicos.value.find(t => t.id === tecnicoSeleccionado.value);
  const idx = ventas.value.findIndex(v => v.id === ventaParaAsignar.value.id);
  if (idx !== -1 && tecnico) {
    const nuevasVentas = [...ventas.value];
    nuevasVentas[idx] = { ...nuevasVentas[idx], tecnicoAsignado: tecnico.id, tecnicoNombre: tecnico.nombre, status: 'Asignado' };
    ventas.value = nuevasVentas;
  }
  showAsignarDialog.value = false;
  responseMessage.value = 'Técnico asignado';
  showResponseDialog.value = true;
}

async function eliminarAsignacion(venta) {
  if (!venta.id) return;
  await deleteAsignacionTecnico(venta.id);
  const idx = ventas.value.findIndex(v => v.id === venta.id);
  if (idx !== -1) {
    const nuevasVentas = [...ventas.value];
    nuevasVentas[idx] = { ...nuevasVentas[idx], tecnicoAsignado: null, tecnicoNombre: null, status: 'Sin asignar' };
    ventas.value = nuevasVentas;
  }
  responseMessage.value = 'Asignación eliminada';
  showResponseDialog.value = true;
}

async function verArticulos(venta) {
  const detalle = await getDetalleVenta(venta.id);
  const articulos = await getTodosArticulos();
  articulosDialogList.value = detalle.map(item => {
    const art = articulos.find(a => a.id === item.articulo_id) || {};
    return {
      ...item,
      sku: art.sku,
      nombre: art.nombre
    };
  });
  showArticulosDialog.value = true;
}

function abrirEditarAsignacion({ ventaId, asignacion }) {
  // Reutiliza el diálogo de asignación, precargando los datos actuales
  const venta = ventas.value.find(v => v.id === ventaId);
  if (!venta) return;
  ventaParaAsignar.value = venta;
  tecnicoSeleccionado.value = asignacion.tecnico_id || venta.tecnicoAsignado || null;
  fechaServicio.value = asignacion.fecha_servicio || null;
  horaServicio.value = asignacion.hora_servicio || null;
  horaFin.value = asignacion.hora_fin || null;
  direccionServicio.value = asignacion.direccion || '';
  cpServicio.value = asignacion.cp || '';
  linkUbicacion.value = asignacion.link_ubicacion || '';
  ordenClienteInfo.value = asignacion.cliente_info || {};
  showAsignarDialog.value = true;
}

const showEliminarDialog = ref(false);
const showEliminarResultado = ref(false);
const ventaAEliminar = ref(null);
const eliminarResultado = ref('');
function confirmarEliminarOrden(venta) {
  ventaAEliminar.value = venta;
  showEliminarDialog.value = true;
}
async function eliminarOrdenConfirmada() {
  if (!ventaAEliminar.value) return;
  showEliminarDialog.value = false;
  try {
    await eliminarOrdenServicio(ventaAEliminar.value.id);
    eliminarResultado.value = 'Orden eliminada correctamente.';
    ventas.value = ventas.value.filter(v => v.id !== ventaAEliminar.value.id);
  } catch (e) {
    eliminarResultado.value = 'Error eliminando orden: ' + (e?.response?.data || e.message);
  }
  showEliminarResultado.value = true;
}

// Nuevos refs para constancia fiscal
// const showConstanciaDialog = ref(false);
// const constanciaSeleccionada = ref(null);
// function verConstancia(v) {
//   constanciaSeleccionada.value = v;
//   showConstanciaDialog.value = true;
// }
// function esPdf(url) { return url && url.toLowerCase().includes('.pdf'); }

// const constanciaUrl = computed(() => {
//   if (!constanciaSeleccionada.value || !constanciaSeleccionada.value.constancia_path) return '';
//   return `${import.meta.env.VITE_API_URL}/${constanciaSeleccionada.value.constancia_path}`;
// });

function getConstanciaUrl(constanciaPath) {
  return `${import.meta.env.VITE_API_URL}/${constanciaPath}`;
}
</script>

<style scoped>
/* Estilos modernos para el diálogo de asignar técnico */
.asignar-form {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  /* background: #181818; */
  padding: 1.5rem;
  border-radius: 12px;
}
.asignar-grid {
  display: flex;
  gap: 1.2rem;
  flex-wrap: wrap;
}
.asignar-col {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.asignar-input {
  /* background: #222;
  color: #fff;
  border: 1.5px solid #444; */
  border-radius: 6px;
  font-size: 1em;
  padding: 0.5em 0.8em;
}
.asignar-input:focus {
  border-color: #ff4081;
  outline: none;
}
.plataforma-dropdown .p-dropdown {
  /* background: #222;
  color: #fff; */
  border: 1.5px solid #ff4081;
  border-radius: 6px;
  font-size: 1em;
}
.plataforma-dropdown .p-dropdown.p-invalid {
  border-color: #ff5252;
  box-shadow: 0 0 0 2px rgba(255,82,82,0.2);
}

.req {
  color: #ff5252;
  font-weight: bold;
}
.asignar-actions {
  display: flex;
  gap: 1rem;
  justify-content: flex-end;
  margin-top: 1.2rem;
}
/* Mejora visual para el dropdown de plataforma */
.plataforma-dropdown .p-dropdown {
  /* background: #181818;
  color: #fff; */
  border: 1.5px solid #ff4081;
  border-radius: 6px;
  font-size: 1em;
}
.plataforma-dropdown .p-dropdown.p-invalid {
  border-color: #ff5252;
  box-shadow: 0 0 0 2px rgba(255,82,82,0.2);
}

.historico-notas-container {
  margin: 2rem auto;
  background: var(--color-bg);
  border-radius: 12px;
  /* box-shadow: 0 4px 24px rgba(0,0,0,0.10); */
  padding: 2rem 1.5rem;
  color: var(--color-text);
}
.historico-title {
  color: var(--color-title, #ff4081);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: bold;
}
.historico-table {
  margin-bottom: 2rem;
  background: var(--color-card);
  border-radius: 8px;
  /* box-shadow: 0 2px 8px rgba(0,0,0,0.08); */
  padding: 1.5rem;
}
.historico-dialog :deep(.p-dialog-content) {
  background: var(--color-card);
  padding: 1.5rem 1rem;
  border-radius: 12px;
  color: var(--color-text);
}
.chip {
  display: inline-block;
  padding: 0.2em 0.8em;
  border-radius: 12px;
  font-size: 0.95em;
  font-weight: 500;
  margin-right: 0.2em;
  margin-bottom: 0.1em;
  vertical-align: middle;
}
.chip-asignado {
  background: var(--color-bg, #e0f7fa);
  color: var(--color-title, #00695c);
  border: 1px solid var(--color-title, #00695c);
}
.chip-sinasignar {
  background: var(--color-card, #ffe082);
  color: var(--color-text, #795548);
  border: 1px solid var(--color-text, #795548);
}
</style>
<!-- estilos de ubicación removidos -->