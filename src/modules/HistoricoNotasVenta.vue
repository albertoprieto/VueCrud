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
            icon="pi pi-file-pdf"
            label="PDF"
            class="p-button-sm p-button-success ml-2"
            @click="descargarPDF(slotProps.data)"
          />
        </template>
      </Column>
    </DataTable>
    <Dialog v-model:visible="showDialog" header="Nota de Venta" :modal="true" class="historico-dialog">
      <Button label="Cerrar" icon="pi pi-times" @click="showDialog = false" class="mt-3" />
    </Dialog>
    
  <Dialog v-model:visible="showAsignarDialog" header="Asignar Técnico" :modal="true" :closable="false" class="asignar-dialog">
      <!-- Datos de la orden / cliente (solo lectura) -->
      <div class="grid-info">
        <div class="field">
          <label>Teléfonos</label>
          <div class="field-read">{{ ordenClienteInfo.telefonos || '-' }}</div>
        </div>
        <div class="field">
          <label>Usuario(s)</label>
          <div class="field-read">{{ ordenClienteInfo.usuario || '-' }}</div>
        </div>
        <div class="field">
          <label>Plataforma(s)</label>
          <div class="field-read">{{ ordenClienteInfo.plataforma || '-' }}</div>
        </div>
        <div class="field field-full">
          <label>Descripción</label>
          <Textarea v-model="ordenClienteInfo.descripcion" rows="2" class="w-full" />
        </div>
      </div>
      <Divider />
      <!-- Campos para asignación -->
      <Dropdown
        v-model="tecnicoSeleccionado"
        :options="tecnicos"
        optionLabel="nombre"
        optionValue="id"
        placeholder="Selecciona técnico"
        class="w-full mb-3"
      />
      <div class="flex gap-3 mb-3 flex-wrap">
        <Calendar
          v-model="fechaServicio"
          dateFormat="yy-mm-dd"
          placeholder="Fecha servicio"
          class="flex-1 min-w-40"
        />
        <Calendar
          v-model="horaServicio"
          timeOnly
          hourFormat="24"
          iconDisplay="input"
          placeholder="Hora"
          class="flex-1 min-w-40"
        />
      </div>
      <div style="display:flex; flex-direction:column; gap:.5rem; margin-bottom:1rem;">
        <input v-model="direccionServicio" placeholder="Dirección" style="padding:.5rem; border:1px solid #666; border-radius:4px; background:#111; color:#fff;" />
        <input v-model="cpServicio" placeholder="Código Postal" style="padding:.5rem; border:1px solid #666; border-radius:4px; background:#111; color:#fff;" />
        <input v-model="linkUbicacion" placeholder="Link Ubicación (Maps)" style="padding:.5rem; border:1px solid #666; border-radius:4px; background:#111; color:#fff;" />
      </div>
      <Button label="Asignar" icon="pi pi-check" @click="asignarTecnico" :disabled="!tecnicoSeleccionado || !fechaServicio" />
      <Button label="Cancelar" icon="pi pi-times" @click="showAsignarDialog = false" class="p-button-secondary ml-2" />
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
  </div>
</template>

<script setup>
import { computed, ref, onMounted, nextTick } from 'vue';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Textarea from 'primevue/textarea';
import Divider from 'primevue/divider';
import { getVentas, getDetalleVenta, asignarTecnicoVenta, getTecnicoVenta, deleteAsignacionTecnico } from '@/services/ventasService';
import { getClientes } from '@/services/clientesService';
import { getTodosArticulos } from '@/services/articulosService';
import { getUsuarios } from '@/services/usuariosService';
import { generarNotaVentaPDF } from '@/services/NotaVentaPdfService.js';

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
const horaServicio = ref(null); // NUEVO: hora de servicio
// Nuevos campos adicionales
const direccionServicio = ref('');
const cpServicio = ref('');
const linkUbicacion = ref('');
// Eliminados coordLat y coordLng (mapa removido)
// Datos cliente/orden mostrados en dialog (solo lectura)
const ordenClienteInfo = ref({ telefonos: '', usuario: '', plataforma: '', descripcion: '' });

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
  const ventasRaw = await getVentas();
  // Para cada venta, consulta el técnico asignado
  const ventasConTecnico = await Promise.all(
    ventasRaw.map(async v => {
      const tecnico = await getTecnicoVenta(v.id);
      return {
        ...v,
        cliente_nombre: String(v.cliente_nombre ?? ''),
        tecnicoNombre: tecnico ? String(tecnico.username) : '',
        status: tecnico ? 'Asignado' : 'Sin asignar'
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
  const payload = { venta, cliente, articulos: articulosSeleccionados, empresa };
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

  const payloadExtendido = {
    tecnico_id: tecnicoSeleccionado.value,
    fecha_servicio: fechaFormateada,
    hora_servicio: horaFormateada || null,
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
</script>

<style scoped>
.historico-notas-container {
  margin: 2rem auto;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
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
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
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