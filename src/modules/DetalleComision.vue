<template>
  <div class="detalle-comision-container">
    <Button
      v-if="!esTecnicoRestringido"
      icon="pi pi-arrow-left"
      label="Volver a Comprobantes"
      class="p-button-text mb-3"
      @click="router.push(`/comisiones?tab=${tipo}`)"
    />

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>

    <template v-else>
      <div class="resumen-card">
        <span class="resumen-nombre">{{ nombre }}</span>
        <span class="resumen-tipo">{{ tipo === 'tecnico' ? 'Técnico' : 'Vendedor / Responsable' }}</span>

        <div class="resumen-totales">
          <div class="resumen-item">
            <span class="resumen-label">Reportes con comprobante</span>
            <span class="resumen-valor con">{{ totales.reportesConComprobante }}<span class="resumen-valor-de">/{{ reportesPersona.length }}</span></span>
            <span v-if="tipo === 'vendedor'" class="resumen-subvalor">{{ formatTotal(totales.totalConComprobante) }} vendido</span>
          </div>
          <div v-if="tipo === 'tecnico'" class="resumen-item">
            <span class="resumen-label">Cobrado por el Técnico — con comprobante</span>
            <span class="resumen-valor con">{{ formatTotal(totales.montoTecnicoConComprobante) }}</span>
          </div>
          <div v-if="tipo === 'tecnico'" class="resumen-item">
            <span class="resumen-label">Cobrado por el Técnico — sin comprobante</span>
            <span class="resumen-valor sin">{{ formatTotal(totales.montoTecnicoSinComprobante) }}</span>
          </div>
          <div class="resumen-item">
            <span class="resumen-label">Sin nota/factura</span>
            <span class="resumen-valor sin">{{ totales.reportesSinNota }}</span>
          </div>
          <div class="resumen-item">
            <span class="resumen-label">Con nota, sin comprobante</span>
            <span class="resumen-valor sin">{{ totales.reportesSinComprobante }}</span>
          </div>
          <div class="resumen-item">
            <span class="resumen-label">Con permiso (excusado)</span>
            <span class="resumen-valor con">{{ totales.reportesPermisoPendiente }}</span>
          </div>
        </div>
      </div>

      <div class="filtro-mes-wrap">
        <label for="filtro-mes">Mes</label>
        <select id="filtro-mes" v-model="filtroMes" class="filtro-mes-select">
          <option value="todos">Todos</option>
          <option v-for="m in meses" :key="m.value" :value="m.value">{{ m.label }}</option>
        </select>
      </div>

      <div class="filtros">
        <button type="button" class="filtro-btn" :class="{ activo: filtroEstado === 'todos' }" @click="filtroEstado = 'todos'">Todos ({{ reportesPersona.length }})</button>
        <button type="button" class="filtro-btn" :class="{ activo: filtroEstado === 'con_comprobante' }" @click="filtroEstado = 'con_comprobante'">Con comprobante ({{ totales.reportesConComprobante }})</button>
        <button type="button" class="filtro-btn" :class="{ activo: filtroEstado === 'sin_comprobante' }" @click="filtroEstado = 'sin_comprobante'">Con nota, sin comprobante ({{ totales.reportesSinComprobante }})</button>
        <button type="button" class="filtro-btn" :class="{ activo: filtroEstado === 'sin_nota' }" @click="filtroEstado = 'sin_nota'">Sin nota/factura ({{ totales.reportesSinNota }})</button>
        <button type="button" class="filtro-btn" :class="{ activo: filtroEstado === 'permiso_pendiente' }" @click="filtroEstado = 'permiso_pendiente'">Con permiso ({{ totales.reportesPermisoPendiente }})</button>
      </div>

      <div v-if="filasSeleccionadas.length" class="seleccion-bulk-bar">
        <span>{{ filasSeleccionadas.length }} seleccionado{{ filasSeleccionadas.length === 1 ? '' : 's' }}</span>
        <Button
          icon="pi pi-clock" label="Marcar permiso a seleccionados" class="p-button-sm"
          @click="abrirMarcarPermisoBulk"
        />
        <Button label="Quitar selección" class="p-button-sm p-button-text" @click="filasSeleccionadas = []" />
      </div>

      <DataTable
        :value="reportesFiltrados" responsiveLayout="scroll" :paginator="reportesFiltrados.length > 15" :rows="15"
        v-model:selection="filasSeleccionadas" dataKey="id"
      >
        <Column selectionMode="multiple" style="width:3rem" />
        <Column header="Reporte" style="width:64px">
          <template #body="{ data }">
            <Button
              icon="pi pi-file-pdf"
              class="p-button-sm p-button-text p-button-warning btn-icon-only"
              :loading="pdfEnCurso === data.id"
              v-tooltip.top="data.folio || `Reporte #${data.id}`"
              @click="abrirPdfNuevaPestana(data)"
            />
          </template>
        </Column>
        <Column field="nombre_cliente" header="Cliente" />
        <Column v-if="tipo === 'tecnico'" header="Responsable">
          <template #body="{ data }">{{ data.vendedor || 'NA' }}</template>
        </Column>
        <Column field="tipo_servicio" header="Servicio" />
        <Column v-if="tipo !== 'tecnico'" header="Total" style="width:100px">
          <template #body="{ data }">{{ formatTotal(data.total) }}</template>
        </Column>
        <Column v-if="tipo === 'tecnico'" header="Monto Técnico" style="width:100px">
          <template #body="{ data }">{{ formatTotal(data.monto_tecnico) }}</template>
        </Column>
        <Column header="Banco" style="width:130px">
          <template #body="{ data }">
            <span v-if="data.referencia?.lugarPago">{{ data.referencia.lugarPago }}</span>
            <span v-else style="color:var(--color-border);">—</span>
          </template>
        </Column>
        <Column header="Fecha" style="width:80px">
          <template #body="{ data }">{{ formatFechaCorta(data.fecha) }}</template>
        </Column>
        <Column header="Permiso" style="width:150px">
          <template #body="{ data }">
            <span
              v-if="data.estado === 'permiso_pendiente'"
              class="badge badge-permiso-vigente"
              v-tooltip.top="`Hasta ${formatFechaCorta(data.permiso_pendiente_fecha)} — marcado por ${data.permiso_pendiente_por || '—'}. Clic para quitar.`"
              style="cursor:pointer;"
              @click="quitarPermiso(data)"
            >{{ data.permiso_pendiente_tipo === 'tecnico' ? 'Técnico' : 'Cliente' }} <i class="pi pi-times" style="font-size:0.65rem;" /></span>
            <span
              v-else-if="data.permisoVencido"
              class="badge badge-permiso-vencido"
              v-tooltip.top="`Venció ${formatFechaCorta(data.permiso_pendiente_fecha)} — marcado por ${data.permiso_pendiente_por || '—'}`"
            >Vencido</span>
            <Button
              v-if="data.estado === 'sin_comprobante' || data.estado === 'sin_nota'"
              icon="pi pi-clock" label="Marcar" class="p-button-sm p-button-text btn-permiso"
              @click="abrirMarcarPermiso(data)"
            />
          </template>
        </Column>
        <Column v-if="tipo === 'vendedor'" header="Transferir" style="width:60px">
          <template #body="{ data }">
            <Button
              v-if="data.estado === 'sin_nota' || data.estado === 'sin_comprobante'"
              icon="pi pi-send"
              class="p-button-sm p-button-text btn-icon-only"
              v-tooltip.top="'Transferir a otro vendedor'"
              @click="abrirTransferir(data)"
            />
          </template>
        </Column>
        <Column header="Detalle" style="width:60px">
          <template #body="{ data }">
            <Button
              icon="pi pi-eye"
              class="p-button-sm p-button-text btn-icon-only"
              v-tooltip.top="'Ver detalle completo'"
              @click="abrirDetalle(data)"
            />
          </template>
        </Column>
      </DataTable>
    </template>

    <!-- Dialog: detalle completo (reporte + nota/factura + comprobantes) -->
    <Dialog
      v-model:visible="detalleDialogVisible"
      :header="`${reporteSeleccionado?.folio || reporteSeleccionado?.id || ''} — ${reporteSeleccionado?.nombre_cliente || ''}`"
      :modal="true"
      :style="{ width: '900px', maxWidth: '95vw' }"
      :draggable="false"
    >
      <div v-if="reporteSeleccionado" class="detalle-dialog">
        <!-- Reporte de servicio -->
        <div class="seccion">
          <div class="seccion-header">
            <h3><i class="pi pi-file-edit" /> Reporte de Servicio</h3>
            <Button
              icon="pi pi-file-pdf"
              label="Ver PDF"
              class="p-button-sm p-button-warning"
              :loading="pdfEnCurso === reporteSeleccionado.id"
              @click="abrirPdfNuevaPestana(reporteSeleccionado)"
            />
          </div>
          <div class="mini-card">
            <div class="mini-row"><strong>Folio:</strong> {{ reporteSeleccionado.folio || reporteSeleccionado.id }}</div>
            <div class="mini-row"><strong>Tipo de servicio:</strong> {{ reporteSeleccionado.tipo_servicio || '-' }}</div>
            <div class="mini-row"><strong>Cliente:</strong> {{ reporteSeleccionado.nombre_cliente || '-' }}</div>
            <div class="mini-row"><strong>Fecha:</strong> {{ formatFechaCorta(reporteSeleccionado.fecha) }}</div>
            <div class="mini-row"><strong>Total:</strong> {{ formatTotal(reporteSeleccionado.total) }}</div>
            <div class="mini-row"><strong>Técnico:</strong> {{ reporteSeleccionado.nombre_instalador || '-' }}</div>
            <div class="mini-row"><strong>Vendedor:</strong> {{ reporteSeleccionado.vendedor || '-' }}</div>
            <div class="mini-row"><strong>Plataforma:</strong> {{ reporteSeleccionado.plataforma || '-' }}</div>
            <div class="mini-row">
              <strong>IMEI:</strong> {{ reporteSeleccionado.imei || '-' }}
              <template v-if="reporteSeleccionado.imei">
                <i v-if="cargandoArticulo" class="pi pi-spin pi-spinner" style="font-size:0.8rem;" />
                <span v-else-if="articuloImei" class="badge badge-articulo">{{ articuloImei }}</span>
                <span v-else class="imei-no-encontrado">no está en nuestra plataforma</span>
              </template>
            </div>
          </div>
        </div>

        <!-- Nota / Factura -->
        <div class="seccion">
          <div class="seccion-header">
            <h3><i class="pi pi-receipt" /> {{ reporteSeleccionado.referencia?.tipo === 'factura' ? 'Factura' : 'Nota de pago' }}</h3>
            <Button
              v-if="reporteSeleccionado.referencia"
              icon="pi pi-arrow-up-right"
              label="Abrir en Pagos"
              class="p-button-sm p-button-outlined"
              @click="irAPago"
            />
          </div>

          <div v-if="!reporteSeleccionado.referencia" class="vacio-mini">
            Este reporte todavía no tiene nota ni factura asociada.
          </div>
          <div v-else-if="notaFacturaCompleta" class="mini-card">
            <div class="mini-row"><strong>#{{ notaFacturaCompleta.id }}</strong></div>
            <div class="mini-row"><strong>Órdenes:</strong> {{ (notaFacturaCompleta.ordenes || []).join(', ') || '-' }}</div>
            <div class="mini-row"><strong>Cliente:</strong> {{ notaFacturaCompleta.cliente || '-' }}</div>
            <div class="mini-row"><strong>Total:</strong> {{ formatTotal(notaFacturaCompleta.total) }}</div>
            <div class="mini-row"><strong>Fecha:</strong> {{ formatFechaCorta(notaFacturaCompleta.fecha) }}</div>
            <div class="mini-row">
              <strong>Banco / Lugar de pago:</strong>
              <span v-if="notaFacturaCompleta.lugar_pago" class="badge badge-banco">{{ notaFacturaCompleta.lugar_pago }}</span>
              <span v-else style="color:var(--color-border);">Sin asignar</span>
            </div>
            <div class="mini-row"><strong>Estatus:</strong> {{ notaFacturaCompleta.status }}</div>
          </div>
        </div>

        <!-- Comprobante de pago -->
        <div class="seccion">
          <h3><i class="pi pi-file" /> Comprobante de pago</h3>
          <div v-if="!reporteSeleccionado.referencia" class="vacio-mini">Sin nota/factura, no hay comprobante que revisar.</div>
          <div v-else-if="!(reporteSeleccionado.referencia.comprobantes || []).length" class="vacio-mini">
            No se ha cargado comprobante de pago todavía.
          </div>
          <div v-else class="comprobantes-grid">
            <a
              v-for="(comp, idx) in reporteSeleccionado.referencia.comprobantes"
              :key="idx"
              :href="urlComprobante(comp)"
              target="_blank"
              rel="noopener noreferrer"
              class="comprobante-preview"
            >
              <img v-if="esImagen(comp)" :src="urlComprobante(comp)" :alt="`comprobante ${idx + 1}`" />
              <div v-else class="comprobante-pdf-icon"><i class="pi pi-file-pdf" /></div>
              <span>{{ nombreArchivo(comp) }}</span>
            </a>
          </div>
        </div>
      </div>
    </Dialog>

    <!-- Dialog: marcar permiso de pendiente (Técnico/Cliente) -->
    <Dialog
      v-model:visible="permisoDialogVisible"
      header="Marcar permiso de pendiente"
      :modal="true"
      :style="{ width: '420px', maxWidth: '95vw' }"
      :draggable="false"
    >
      <div v-if="reportesParaPermiso.length" class="permiso-dialog">
        <p v-if="reportesParaPermiso.length === 1" class="permiso-reporte-info">
          {{ reportesParaPermiso[0].folio || `Reporte #${reportesParaPermiso[0].id}` }} — {{ reportesParaPermiso[0].nombre_cliente || '-' }}
        </p>
        <template v-else>
          <p class="permiso-reporte-info">{{ reportesParaPermiso.length }} reportes seleccionados:</p>
          <ul class="permiso-lista-bulk">
            <li v-for="r in reportesParaPermiso" :key="r.id">{{ r.folio || `Reporte #${r.id}` }} — {{ r.nombre_cliente || '-' }}</li>
          </ul>
        </template>

        <div v-if="!ventanaAbierta" class="permiso-ventana-cerrada">
          <i class="pi pi-exclamation-triangle" />
          Ya pasó el día 25 del mes — fuera de ventana para marcar permisos nuevos. Los pendientes de esta última semana deben resolverse para cerrar el mes.
        </div>
        <template v-else>
          <div class="field">
            <label>Motivo</label>
            <Dropdown v-model="permisoTipo" :options="opcionesPermisoTipo" optionLabel="label" optionValue="value" placeholder="Selecciona motivo" class="w-full" />
          </div>
          <div class="field">
            <label>Fecha compromiso (máximo día 25 de este mes)</label>
            <Calendar v-model="permisoFecha" :minDate="hoyDate" :maxDate="limiteFechaPermiso" dateFormat="dd/mm/yy" showIcon class="w-full" />
          </div>
        </template>

        <div class="modal-actions">
          <Button
            v-if="ventanaAbierta"
            label="Guardar" icon="pi pi-check"
            :loading="guardandoPermiso"
            :disabled="!permisoTipo || !permisoFecha"
            @click="guardarPermiso"
          />
          <Button label="Cancelar" class="p-button-secondary" @click="permisoDialogVisible = false" type="button" />
        </div>
      </div>
    </Dialog>

    <!-- Dialog: transferir reporte a otro vendedor -->
    <Dialog
      v-model:visible="transferDialogVisible"
      header="Transferir a otro vendedor"
      :modal="true"
      :style="{ width: '420px', maxWidth: '95vw' }"
      :draggable="false"
    >
      <div v-if="reporteParaTransferir" class="permiso-dialog">
        <p class="permiso-reporte-info">
          {{ reporteParaTransferir.folio || `Reporte #${reporteParaTransferir.id}` }} — {{ reporteParaTransferir.nombre_cliente || '-' }}
        </p>
        <div class="field">
          <label>Nuevo vendedor</label>
          <Dropdown
            v-model="nuevoVendedor"
            :options="vendedoresDisponibles"
            editable
            placeholder="Selecciona o escribe un nombre"
            class="w-full"
          />
        </div>
        <div class="modal-actions">
          <Button
            label="Transferir" icon="pi pi-send"
            :loading="transfiriendo"
            :disabled="!nuevoVendedor.trim()"
            @click="confirmarTransferir"
          />
          <Button label="Cancelar" class="p-button-secondary" @click="transferDialogVisible = false" type="button" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import axios from 'axios';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';
import { getReportesServicioTodos, marcarPermisoPendiente, quitarPermisoPendiente, transferirVendedor } from '@/services/reportesService';
import { getNotas, getFacturas } from '@/services/pagosService';
import {
  indexarNotasFacturas, reportesDePersona, agruparPorPersona, mesesDisponibles, filtrarPorMes, mesActual, ESTADOS,
  limitePermisoPendiente, ventanaPermisoPendienteAbierta,
} from '@/utils/comisiones';

const toast = useToast();

const props = defineProps({
  tipo: { type: String, required: true },   // 'tecnico' | 'vendedor'
  nombre: { type: String, required: true },
});
const route = useRoute();
const router = useRouter();
const loginStore = useLoginStore();
const user = computed(() => loginStore.user || {});

const tipo = computed(() => props.tipo || route.params.tipo);
const nombre = computed(() => props.nombre || route.params.nombre);

// Un Técnico no puede ver la comisión de alguien más cambiando la URL a mano.
const esTecnicoRestringido = computed(() => (user.value.perfil || '') === 'Tecnico');

const loading = ref(true);
const reportes = ref([]);
const notas = ref([]);
const facturas = ref([]);
const filtroEstado = ref('todos');
const filtroMes = ref('todos');

const API_URL = (import.meta.env.VITE_API_URL || '').replace(/\/$/, '');

const formatoMoneda = new Intl.NumberFormat('es-MX', {
  style: 'currency', currency: 'MXN', minimumFractionDigits: 2, maximumFractionDigits: 2,
});
function formatTotal(value) { return formatoMoneda.format(Number(value) || 0); }
function formatFechaCorta(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${String(d.getFullYear()).slice(-2)}`;
}
function urlComprobante(path) {
  if (!path) return '';
  const p = path.startsWith('/') ? path : `/${path}`;
  return `${API_URL}${p}`;
}
function nombreArchivo(path) {
  if (!path) return 'comprobante';
  return path.split('/').pop();
}
function esImagen(path) {
  return /\.(png|jpe?g|webp|gif)$/i.test(path || '');
}

const indice = computed(() => indexarNotasFacturas(notas.value, facturas.value));
const campo = computed(() => (tipo.value === 'tecnico' ? 'nombre_instalador' : 'vendedor'));

const reportesPersonaTodos = computed(() => {
  const base = reportesDePersona(reportes.value, indice.value, campo.value, nombre.value);
  return base.map(r => ({ ...r, tieneComprobante: r.estado === ESTADOS.CON_COMPROBANTE }));
});
const meses = computed(() => mesesDisponibles(reportesPersonaTodos.value));
const reportesPersona = computed(() => filtrarPorMes(reportesPersonaTodos.value, filtroMes.value));

const reportesFiltrados = computed(() => {
  if (filtroEstado.value === 'todos') return reportesPersona.value;
  return reportesPersona.value.filter(r => r.estado === filtroEstado.value);
});

const totales = computed(() => {
  const t = {
    totalVendido: 0, totalConComprobante: 0, totalSinComprobante: 0, totalSinNota: 0,
    reportesConComprobante: 0, reportesSinComprobante: 0, reportesSinNota: 0,
    montoTecnicoConComprobante: 0, montoTecnicoSinComprobante: 0,
    reportesPermisoPendiente: 0,
  };
  for (const r of reportesPersona.value) {
    const total = Number(r.total) || 0;
    const montoTecnico = Number(r.monto_tecnico) || 0;
    t.totalVendido += total;
    if (r.estado === ESTADOS.CON_COMPROBANTE) {
      t.totalConComprobante += total;
      t.reportesConComprobante += 1;
      t.montoTecnicoConComprobante += montoTecnico;
    } else if (r.estado === ESTADOS.SIN_COMPROBANTE) {
      t.totalSinComprobante += total;
      t.reportesSinComprobante += 1;
      t.montoTecnicoSinComprobante += montoTecnico;
    } else if (r.estado === ESTADOS.SIN_NOTA) {
      t.totalSinNota += total;
      t.reportesSinNota += 1;
      t.montoTecnicoSinComprobante += montoTecnico;
    } else if (r.estado === ESTADOS.PERMISO_PENDIENTE) {
      t.reportesPermisoPendiente += 1;
    }
  }
  return t;
});

async function cargar() {
  loading.value = true;
  try {
    [reportes.value, notas.value, facturas.value] = await Promise.all([
      getReportesServicioTodos(),
      getNotas(),
      getFacturas(),
    ]);
  } catch {
    reportes.value = [];
    notas.value = [];
    facturas.value = [];
  }
  // Default: mes en curso, si esta persona tiene reportes ese mes. Si no,
  // mejor "Todos" que una tabla vacía sin explicación.
  const actual = mesActual();
  filtroMes.value = meses.value.some(m => m.value === actual) ? actual : 'todos';
  loading.value = false;
}

onMounted(() => {
  if (esTecnicoRestringido.value && tipo.value === 'tecnico' &&
      (nombre.value || '').toLowerCase() !== (user.value.username || '').toLowerCase()) {
    router.replace({ name: 'detalle-comision', params: { tipo: 'tecnico', nombre: user.value.username } });
    return;
  }
  cargar();
});

watch([tipo, nombre], () => {
  if (esTecnicoRestringido.value && tipo.value === 'tecnico' &&
      (nombre.value || '').toLowerCase() !== (user.value.username || '').toLowerCase()) {
    router.replace({ name: 'detalle-comision', params: { tipo: 'tecnico', nombre: user.value.username } });
  }
});

// ── Acciones: PDF del reporte y comprobante, siempre en pestaña nueva ──
const pdfEnCurso = ref(null);

async function abrirPdfNuevaPestana(reporte) {
  pdfEnCurso.value = reporte.id;
  try {
    const { generarReporteServicioPDF } = await import('@/components/GeneraReporteServicioPDF.js');
    const url = await generarReporteServicioPDF({ reporte, mode: 'bloburl' });
    window.open(url, '_blank', 'noopener');
  } catch {
    // silencioso — el botón queda disponible para reintentar
  }
  pdfEnCurso.value = null;
}

// ── Dialog de detalle completo — nota/factura ya está en memoria (notas.value
// / facturas.value), no hace falta pedir nada al servidor para abrirlo. ──
const detalleDialogVisible = ref(false);
const reporteSeleccionado = ref(null);

const notaFacturaCompleta = computed(() => {
  const ref_ = reporteSeleccionado.value?.referencia;
  if (!ref_) return null;
  const lista = ref_.tipo === 'factura' ? facturas.value : notas.value;
  return lista.find(x => x.id === ref_.id) || null;
});

// Nombre del artículo (no descripción) si el IMEI está dado de alta en
// nuestra plataforma — mismo endpoint que usa BuscarImei.vue.
const articuloImei = ref(null);
const cargandoArticulo = ref(false);

async function buscarArticuloImei(imei) {
  articuloImei.value = null;
  if (!imei) return;
  cargandoArticulo.value = true;
  try {
    const res = await axios.get(`${API_URL}/buscar-imei`, { params: { digitos: imei } });
    const match = (res.data || []).find(r => r.imei === imei) || res.data?.[0];
    articuloImei.value = match?.articulo_nombre || null;
  } catch {
    articuloImei.value = null;
  }
  cargandoArticulo.value = false;
}

function abrirDetalle(reporte) {
  reporteSeleccionado.value = reporte;
  detalleDialogVisible.value = true;
  buscarArticuloImei(reporte.imei);
}

function irAPago() {
  if (!reporteSeleccionado.value?.referencia) return;
  const { tipo: refTipo, id } = reporteSeleccionado.value.referencia;
  if (refTipo === 'factura') {
    router.push({ name: 'detalle-factura', params: { id } });
  } else {
    router.push({ name: 'detalle-pago', params: { tipo: 'nota', id } });
  }
}

// ── Permiso de pendiente (Técnico/Cliente) — excusa temporal para que un
// reporte no cuente como pendiente real en la comisión, hasta una fecha
// compromiso tope día 25 del mes en curso. Ver utils/comisiones.js. ──
const permisoDialogVisible = ref(false);
const reportesParaPermiso = ref([]);
const permisoTipo = ref(null);
const permisoFecha = ref(null);
const guardandoPermiso = ref(false);
const filasSeleccionadas = ref([]);

const opcionesPermisoTipo = [
  { label: 'Técnico', value: 'tecnico' },
  { label: 'Cliente', value: 'cliente' },
];

const ventanaAbierta = computed(() => ventanaPermisoPendienteAbierta());
const hoyDate = computed(() => new Date());
const limiteFechaPermiso = computed(() => limitePermisoPendiente());

function abrirMarcarPermiso(reporte) {
  reportesParaPermiso.value = [reporte];
  permisoTipo.value = null;
  permisoFecha.value = null;
  permisoDialogVisible.value = true;
}

function abrirMarcarPermisoBulk() {
  const elegibles = filasSeleccionadas.value.filter(r => r.estado === 'sin_comprobante' || r.estado === 'sin_nota');
  if (!elegibles.length) {
    toast.add({ severity: 'warn', summary: 'Nada que marcar', detail: 'Ningún reporte seleccionado admite permiso (ya tiene comprobante, ya tiene permiso, o está vencido).', life: 4500 });
    return;
  }
  if (elegibles.length < filasSeleccionadas.value.length) {
    toast.add({ severity: 'info', summary: 'Selección parcial', detail: `${elegibles.length} de ${filasSeleccionadas.value.length} seleccionados admiten permiso — el resto se ignora.`, life: 4500 });
  }
  reportesParaPermiso.value = elegibles;
  permisoTipo.value = null;
  permisoFecha.value = null;
  permisoDialogVisible.value = true;
}

async function guardarPermiso() {
  if (!reportesParaPermiso.value.length || !permisoTipo.value || !permisoFecha.value) return;
  guardandoPermiso.value = true;
  const fechaStr = permisoFecha.value.toISOString().slice(0, 10);
  let exitosos = 0;
  let fallidos = 0;
  for (const reporte of reportesParaPermiso.value) {
    try {
      await marcarPermisoPendiente(reporte.id, {
        tipo: permisoTipo.value,
        fecha_compromiso: fechaStr,
        usuario: user.value.username || null,
      });
      Object.assign(reporte, {
        permiso_pendiente_tipo: permisoTipo.value,
        permiso_pendiente_fecha: fechaStr,
        permiso_pendiente_por: user.value.username || null,
      });
      exitosos += 1;
    } catch {
      fallidos += 1;
    }
  }
  if (exitosos) {
    toast.add({
      severity: fallidos ? 'warn' : 'success',
      summary: exitosos > 1 ? 'Permisos marcados' : 'Permiso marcado',
      detail: fallidos
        ? `${exitosos} marcados, ${fallidos} fallaron.`
        : 'El reporte ya no cuenta como pendiente hasta la fecha compromiso.',
      life: 4000
    });
  } else {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo marcar el permiso.', life: 4500 });
  }
  permisoDialogVisible.value = false;
  filasSeleccionadas.value = [];
  await cargar();
  guardandoPermiso.value = false;
}

async function quitarPermiso(reporte) {
  try {
    await quitarPermisoPendiente(reporte.id);
    toast.add({ severity: 'success', summary: 'Permiso quitado', life: 3000 });
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo quitar el permiso.', life: 4500 });
  }
}

// ── Transferir a otro vendedor — reasigna reportes.vendedor. Sin nota de
// auditoría: el reporte pasa completo al nuevo vendedor. Solo aplica a
// vendedor (no técnico, ahí no hay "responsable" a quien transferir). ──
const transferDialogVisible = ref(false);
const reporteParaTransferir = ref(null);
const nuevoVendedor = ref('');
const transfiriendo = ref(false);

const vendedoresDisponibles = computed(() => {
  if (tipo.value !== 'vendedor') return [];
  return agruparPorPersona(reportes.value, indice.value, 'vendedor')
    .map(p => p.nombre)
    .filter(n => n && n !== nombre.value)
    .sort((a, b) => a.localeCompare(b));
});

function abrirTransferir(reporte) {
  reporteParaTransferir.value = reporte;
  nuevoVendedor.value = '';
  transferDialogVisible.value = true;
}

async function confirmarTransferir() {
  const destino = (nuevoVendedor.value || '').trim();
  if (!reporteParaTransferir.value || !destino) return;
  transfiriendo.value = true;
  try {
    await transferirVendedor(reporteParaTransferir.value.id, destino);
    toast.add({ severity: 'success', summary: 'Transferido', detail: `Reporte movido a ${destino}.`, life: 3500 });
    transferDialogVisible.value = false;
    await cargar();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo transferir el reporte.', life: 4500 });
  }
  transfiriendo.value = false;
}
</script>

<style scoped>
.detalle-comision-container {
  margin: 1.5rem auto;
  padding: 1.5rem 2rem;
  max-width: none;
  width: 100%;
  box-sizing: border-box;
}
.mb-3 { margin-bottom: 1rem; }
.resumen-card {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 2rem;
  margin-bottom: 1.5rem;
  border-radius: 16px;
  background: var(--color-card);
  border: 1px solid var(--color-border);
}
.resumen-nombre {
  font-size: 1.4rem;
  font-weight: 800;
  color: var(--color-title);
}
.resumen-tipo {
  font-size: 0.8rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text);
  opacity: 0.65;
  margin-bottom: 0.5rem;
}
.resumen-totales {
  display: flex;
  flex-wrap: wrap;
  justify-content: center;
  gap: 2rem;
}
.resumen-item {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.2rem;
}
.resumen-label {
  font-size: 0.75rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.05em;
  color: var(--color-text);
  opacity: 0.7;
}
.resumen-valor {
  font-size: 1.5rem;
  font-weight: 800;
  color: var(--color-title);
}
.resumen-valor.con { color: var(--color-success); }
.resumen-valor.sin { color: var(--color-warning); }
.resumen-valor-de {
  font-size: 0.9rem;
  font-weight: 600;
  opacity: 0.5;
}
.resumen-subvalor {
  font-size: 0.78rem;
  color: var(--color-text);
  opacity: 0.65;
}
.filtro-mes-wrap {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.filtro-mes-wrap label {
  font-size: 0.82rem;
  font-weight: 700;
  color: var(--color-text);
  opacity: 0.75;
}
.filtro-mes-select {
  padding: 0.4rem 0.8rem;
  border-radius: 8px;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-text);
  font-size: 0.9rem;
}
.filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.seleccion-bulk-bar {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  padding: 0.6rem 0.9rem;
  margin-bottom: 0.75rem;
  border-radius: 8px;
  background: color-mix(in srgb, var(--color-primary) 8%, transparent);
  border: 1px solid color-mix(in srgb, var(--color-primary) 25%, transparent);
  font-size: 0.85rem;
}
.permiso-lista-bulk {
  max-height: 160px;
  overflow-y: auto;
  margin: 0 0 0.75rem;
  padding-left: 1.1rem;
  font-size: 0.82rem;
  color: var(--color-text);
  opacity: 0.85;
}
.filtro-btn {
  padding: 0.4rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
}
.filtro-btn.activo {
  background: var(--color-primary);
  border-color: var(--color-primary);
  color: var(--color-on-primary, #b63434);
}
.badge {
  display: inline-flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.25rem 0.7rem;
  border-radius: 1rem;
  font-size: 0.78rem;
  font-weight: bold;
  border: none;
}
.btn-icon-only :deep(.p-button-label) {
  display: none;
}
.badge-banco { background: color-mix(in srgb, var(--color-primary) 20%, transparent); color: var(--color-primary); }
.badge-articulo { background: color-mix(in srgb, var(--color-title) 14%, transparent); color: var(--color-title); }
.imei-no-encontrado {
  font-size: 0.78rem;
  color: var(--color-text);
  opacity: 0.55;
  font-style: italic;
}

.detalle-dialog {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}
.seccion h3 {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin: 0 0 0.75rem;
  color: var(--color-title);
  font-size: 1rem;
}
.seccion-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  gap: 0.75rem;
  flex-wrap: wrap;
  margin-bottom: 0.75rem;
}
.seccion-header h3 { margin: 0; }
.mini-card {
  background: var(--color-bg-light, color-mix(in srgb, var(--color-card) 60%, transparent));
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.9rem 1.1rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.mini-row {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  font-size: 0.9rem;
  color: var(--color-text);
}
.vacio-mini {
  color: var(--color-text);
  opacity: 0.65;
  font-size: 0.88rem;
  padding: 0.5rem 0;
}
.comprobantes-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
}
.comprobante-preview {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.4rem;
  width: 140px;
  text-decoration: none;
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 10px;
  padding: 0.6rem;
  transition: border-color 0.15s, transform 0.15s;
}
.comprobante-preview:hover {
  border-color: var(--color-primary);
  transform: translateY(-2px);
}
.comprobante-preview img {
  width: 100%;
  height: 90px;
  object-fit: cover;
  border-radius: 6px;
}
.comprobante-pdf-icon {
  width: 100%;
  height: 90px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 2rem;
  color: var(--color-error);
  background: color-mix(in srgb, var(--color-error) 10%, transparent);
  border-radius: 6px;
}
.comprobante-preview span {
  font-size: 0.72rem;
  text-align: center;
  word-break: break-all;
  opacity: 0.8;
}

@media (max-width: 768px) {
  .detalle-comision-container {
    margin: 1rem auto;
    padding: 1rem 0.75rem;
  }
}

.badge-permiso-vigente { background: color-mix(in srgb, var(--color-primary) 18%, transparent); color: var(--color-primary); }
.badge-permiso-vencido { background: color-mix(in srgb, var(--color-warning) 20%, transparent); color: var(--color-warning); }
.btn-permiso :deep(.p-button-label) { font-size: 0.8rem; }

.permiso-dialog {
  display: flex;
  flex-direction: column;
  gap: 1rem;
}
.permiso-reporte-info {
  margin: 0;
  font-weight: 700;
  color: var(--color-title);
}
.permiso-ventana-cerrada {
  display: flex;
  align-items: flex-start;
  gap: 0.5rem;
  padding: 0.9rem 1rem;
  border-radius: 10px;
  background: color-mix(in srgb, var(--color-warning) 12%, transparent);
  color: var(--color-warning);
  font-size: 0.88rem;
}
.permiso-dialog .field {
  display: flex;
  flex-direction: column;
  gap: 0.35rem;
}
.permiso-dialog .field label {
  font-size: 0.8rem;
  font-weight: 700;
  color: var(--color-text);
  opacity: 0.75;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 0.75rem;
  margin-top: 0.5rem;
}
</style>
