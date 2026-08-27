<template>
  <section class="util-page">
    <header class="util-hero">
      <h1>SIM ESPAÑOL</h1>
      <p>Listado de SIMs. Usa los filtros dentro de la tabla para buscar en el histórico.</p>
    </header>

<!--     <div class="util-card">
      <div class="section-head">
        <div>
          <h2>Carga inicial SIMPRO</h2>
          <p>Trae todos los números registrados en la plataforma y los agrega como borrador para que completes IMEI, plataforma, etc. Se puede correr varias veces: lo que ya existe no se duplica.</p>
        </div>
      </div>
      <div class="actions">
        <Button
          :label="importando ? 'Importando...' : 'Cargar todos los números (SIMPRO)'"
          icon="pi pi-cloud-download"
          :loading="importando"
          :disabled="importando"
          @click="importarSimpro()"
        />
        <Button
          :label="completando ? 'Completando...' : 'Completar datos faltantes (SIMPRO)'"
          icon="pi pi-database"
          severity="secondary"
          :loading="completando"
          :disabled="completando"
          @click="completarDatos()"
        />
        <Button
          :label="refrescando ? (refrescarProgreso || 'Refrescando...') : 'Refrescar estado y consumo (SIMPRO)'"
          icon="pi pi-sync"
          severity="secondary"
          outlined
          :loading="refrescando"
          :disabled="refrescando"
          @click="refrescarSimpro()"
        />
      </div>
      <p class="hint">
        "Completar datos" recorre los registros incompletos que tienen ICCID, consulta SIMPRO en tandas
        y llena solo lo que esté vacío (activación, vigencia, usuario, cliente, IMEI, estado). Deduce la
        plataforma cruzando el IMEI con reportes de servicio. Se puede correr varias veces.
      </p>
    </div> -->

      <p v-if="message" :class="['status', messageError ? 'is-error' : 'is-ok']">{{ message }}</p>

      <div class="result">
        <h2>Resultados</h2>
        <DataTable
          :value="rows"
          stripedRows
          size="small"
          sortMode="single"
          @sort="onSort"
          responsiveLayout="scroll"
        >
          <template #header>
            <div class="table-tools">
              <div class="table-tools__summary">
                <span class="summary-pill">Histórico: {{ historicalRecords }}</span>
                <span class="summary-pill">Filtrados: {{ filteredRecords }}</span>
                <button
                  v-for="opt in filterTipoOptions"
                  :key="opt.value"
                  type="button"
                  class="summary-pill summary-pill--tipo"
                  :class="{ 'is-active': filters.tipo === opt.value }"
                  @click="toggleTipoFiltro(opt.value)"
                >
                  {{ opt.label }}: {{ countsByTipo[opt.value] || 0 }}
                </button>
              </div>
              <div class="table-tools__filters">
                <Dropdown
                  v-model="filters.tipo"
                  :options="filterTipoOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Tipo"
                  showClear
                />
                <InputText v-model="filters.deaccount" placeholder="Usuario" @keyup.enter="aplicarFiltros" />
                <InputText v-model="filters.plataforma" placeholder="Plataforma" @keyup.enter="aplicarFiltros" />
                <InputText v-model="filters.imei" placeholder="IMEI" @keyup.enter="aplicarFiltros" />
                <Calendar
                  v-model="filters.fecha_desde"
                  dateFormat="yy-mm-dd"
                  placeholder="Fecha desde"
                  showIcon
                  iconDisplay="input"
                  showButtonBar
                />
                <Calendar
                  v-model="filters.fecha_hasta"
                  dateFormat="yy-mm-dd"
                  placeholder="Fecha hasta"
                  showIcon
                  iconDisplay="input"
                  showButtonBar
                />
                <Dropdown
                  v-model="filters.vigencia_sim"
                  :options="vigenciaSimOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Vigencia SIM"
                  showClear
                />
                <Dropdown
                  v-model="filters.estado_simpro"
                  :options="estadoSimproOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Estado SIMPRO"
                  @change="aplicarFiltros"
                />
                <div class="table-tools__buttons">
                  <Button label="Buscar" icon="pi pi-search" @click="aplicarFiltros" :loading="loading" />
                  <Button label="Limpiar" icon="pi pi-filter-slash" severity="secondary" outlined @click="limpiarFiltros" :disabled="loading" />
                  <Button
                    :label="refrescando ? (refrescarProgreso || 'Actualizando...') : 'Actualizar desde SIMPRO'"
                    icon="pi pi-sync"
                    severity="secondary"
                    :loading="refrescando"
                    :disabled="refrescando"
                    @click="refrescarSimpro"
                  />
                </div>
              </div>
            </div>
          </template>
          <Column field="tipo" header="TIPO" sortable>
            <template #body="{ data }">
              <Tag :value="TIPO_LABELS[data.tipo] || data.tipo" :severity="tipoSeverity(data.tipo)" />
            </template>
          </Column>
          <Column field="activation_date" header="Fecha. Act" sortable>
            <template #body="{ data }">{{ data.activation_date || '-' }}</template>
          </Column>
          <Column field="deaccount" header="USUARIO" sortable>
            <template #body="{ data }">{{ data.deaccount || '-' }}</template>
          </Column>
          <Column field="accountName" header="CLIENTE" sortable>
            <template #body="{ data }">{{ data.accountName || '-' }}</template>
          </Column>
          <Column field="plataforma" header="PLATAFORMA" sortable>
            <template #body="{ data }">{{ data.plataforma || '-' }}</template>
          </Column>
          <Column field="imei" header="IMEI" sortable>
            <template #body="{ data }">{{ data.imei || '-' }}</template>
          </Column>
          <Column field="iccid" header="ICCID" sortable>
            <template #body="{ data }">{{ data.iccid || '-' }}</template>
          </Column>
          <Column field="deviceMobile" header="SIM ESPAÑOL" sortable>
            <template #body="{ data }">{{ data.deviceMobile || '-' }}</template>
          </Column>
          <Column field="vigencia_sim" header="VIGENCIA SIM" sortable>
            <template #body="{ data }">
              <span>{{ data.vigencia_sim || '-' }}</span>
              <Tag v-if="esVencido(data.vigencia_sim)" value="Vencido" severity="danger" style="margin-left: 6px;" />
            </template>
          </Column>
          <Column header="ESTADO SIMPRO" style="min-width: 150px">
            <template #body="{ data }">
              <Tag
                v-if="data.sim_state === 'suspendido_temporal'"
                value="Suspendido temporal"
                severity="warning"
              />
              <Tag
                v-else-if="data.sim_state === 'cancelacion_programada'"
                value="Cancelación programada"
                severity="danger"
              />
              <span v-else-if="data.sim_customer_status">{{ data.sim_customer_status }}</span>
              <span v-else class="muted">—</span>
              <div v-if="data.verificado_en" class="muted-small">rev. {{ fechaCorta(data.verificado_en) }}</div>
            </template>
          </Column>
          <Column header="CONSUMO" style="min-width: 120px">
            <template #body="{ data }">
              <span v-if="data.data_usage_mb != null">{{ data.data_usage_mb }} MB</span>
              <span v-else class="muted">—</span>
              <Tag v-if="data.sin_trafico" value="Sin tráfico" severity="danger" style="margin-left:6px;" />
            </template>
          </Column>
          <Column header="ACCIONES" style="min-width: 180px">
            <template #body="{ data }">
              <div class="row-actions">
                <Button icon="pi pi-pencil" text rounded severity="info" @click="openEdit(data)" v-tooltip.top="'Editar'" />
                <Button icon="pi pi-server" text rounded severity="secondary" @click="abrirAccionesSimpro(data)" v-tooltip.top="'Acciones SIMPRO'" />
              </div>
            </template>
          </Column>
        </DataTable>
        <div v-if="loadingMore" class="loading-more">Cargando más registros...</div>
        <div v-else-if="!hasMore && rows.length" class="loading-more">No hay más registros.</div>
      </div>

    <Dialog v-model:visible="showEditDialog" header="Editar registro" :style="{ width: '520px' }" modal>
      <div class="edit-grid">
        <div class="field">
          <label>Tipo</label>
          <Dropdown v-model="editRow.tipo" :options="tiposOptions" optionLabel="label" optionValue="value" />
        </div>
        <div class="field">
          <label>Fecha. Act</label>
          <InputText v-model="editRow.activation_date" />
        </div>
        <div class="field">
          <label>Usuario</label>
          <InputText v-model="editRow.deaccount" />
        </div>
        <div class="field">
          <label>Cliente</label>
          <InputText v-model="editRow.accountName" />
        </div>
        <div class="field">
          <label>Plataforma</label>
          <InputText v-model="editRow.plataforma" />
        </div>
        <div class="field">
          <label>IMEI</label>
          <InputText v-model="editRow.imei" />
        </div>
        <div class="field">
          <label>ICCID</label>
          <InputText v-model="editRow.iccid" />
        </div>
        <div class="field">
          <label>SIM ESPAÑOL</label>
          <InputText v-model="editRow.deviceMobile" />
        </div>
        <div class="field">
          <label>VIGENCIA SIM</label>
          <InputText v-model="editRow.vigencia_sim" />
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" text @click="showEditDialog = false" />
        <Button :label="editRow.id ? 'Guardar' : 'Guardar nuevo'" icon="pi pi-save" @click="saveEdit" />
      </template>
    </Dialog>

  </section>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useRouter } from 'vue-router';
import * as XLSX from 'xlsx';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import {
  deleteConsultaSim,
  getConsultasSim,
  getDispositivoPorPlataforma,
  getSimDetails,
  getUtilidadesPlataformas,
  importarSimsSimpro,
  saveConsultaSim,
  updateConsultaSim,
  completarDatosSims,
  refrescarSimproSims,
  getCustomerSolutions,
  getBillingAccounts,
  activarSimsSimpro,
  getAlertasConsumoSimpro,
  getFacturasSimpro
} from '@/services/utilidadesImeiService';

const router = useRouter();

const imei = ref('');
const simTelefono = ref('');
const plataforma = ref('');
const plataformas = ref([]);
const tipo = ref('activacion');
const tiposOptions = [
  { label: 'Activación', value: 'activacion' },
  { label: 'Renovación', value: 'renovacion' },
  { label: 'Cancelado', value: 'cancelado' },
  { label: 'Desinstalado', value: 'desinstalado' },
  { label: 'Reutilizado', value: 'reutilizado' }
];
const filterTipoOptions = tiposOptions;
const TIPO_LABELS = Object.fromEntries(tiposOptions.map(o => [o.value, o.label]));
function tipoSeverity(t) {
  return {
    activacion: 'success',
    renovacion: 'info',
    cancelado: 'danger',
    desinstalado: 'warning',
    reutilizado: 'contrast'
  }[t] || null;
}
const estadoSimproOptions = [
  { label: 'Solo activos', value: 'activos' },
  { label: 'Solo cancelados / cesados', value: 'baja' },
  { label: 'Todos', value: '' },
];
const vigenciaSimOptions = [
  { label: 'Vencidos (7+ días)', value: 'vencidos_7_dias' }
];
const rows = ref([]);
const loading = ref(false);
const message = ref('');
const messageError = ref(false);
const totalRecords = ref(0);
const historicalRecords = ref(0);
const filteredRecords = ref(0);
const countsByTipo = ref({});
const pageSize = ref(30);
const currentPage = ref(1);
const hasMore = ref(true);
const loadingMore = ref(false);
const sortField = ref(null);
const sortOrder = ref(null);
const showEditDialog = ref(false);
const editRow = ref({});
const importando = ref(false);
const completando = ref(false);
const refrescando = ref(false);
const refrescarProgreso = ref('');
const solucionesSimpro = ref([]);
const cargandoSoluciones = ref(false);

// Administración SIMPRO
const showAdmin = ref(false);
const adminBusy = ref('');
const cuentasSimpro = ref([]);
const cargandoCuentas = ref(false);
const activarIccids = ref('');
const activarSolucion = ref('');
const activarCuenta = ref('');
const alertasTexto = ref('');
const facturasCuenta = ref('');
const facturasTexto = ref('');
const filters = ref({
  tipo: '',
  deaccount: '',
  plataforma: '',
  imei: '',
  vigencia_sim: '',
  fecha_desde: null,
  fecha_hasta: null,
  estado_simpro: 'activos',
});

function sanitizeImei() {
  imei.value = String(imei.value || '').replace(/\D+/g, '');
}

function sanitizeSimTelefono() {
  simTelefono.value = String(simTelefono.value || '').replace(/\D+/g, '');
}

async function loadPlataformas() {
  try {
    const data = await getUtilidadesPlataformas();
    plataformas.value = data?.plataformas || [
      { label: 'IOP', value: 'IOP' },
      { label: 'Tracksolid', value: 'TRACKSOLID' }
    ];
  } catch (_) {
    plataformas.value = [
      { label: 'IOP', value: 'IOP' },
      { label: 'Tracksolid', value: 'TRACKSOLID' }
    ];
  }

  if (!plataforma.value && plataformas.value.length) {
    plataforma.value = plataformas.value[0].value;
  }

  await cargarDesdeDB();
}

async function cargarDesdeDB() {
  try {
    const historicalData = await getConsultasSim(1, 1, {});
    historicalRecords.value = historicalData.total || 0;

    currentPage.value = 1;
    const sort = sortField.value ? { field: sortField.value, order: sortOrder.value } : {};
    const data = await getConsultasSim(currentPage.value, pageSize.value, activeFilters(), sort);
    totalRecords.value = data.total || 0;
    filteredRecords.value = data.total || 0;
    countsByTipo.value = data.counts_by_tipo || {};
    const mapped = (data.items || []).map(mapDbRow);
    rows.value = sortField.value ? mapped : sortRows(mapped);
    hasMore.value = rows.value.length < totalRecords.value;
  } catch (_) {
    // tabla aún no creada o error de red — no interrumpir
  }
}

async function cargarMasDesdeDB() {
  if (loadingMore.value || loading.value || !hasMore.value) return;
  loadingMore.value = true;
  try {
    const nextPage = currentPage.value + 1;
    const sort = sortField.value ? { field: sortField.value, order: sortOrder.value } : {};
    const data = await getConsultasSim(nextPage, pageSize.value, activeFilters(), sort);
    const mapped = (data.items || []).map(mapDbRow);
    totalRecords.value = data.total || totalRecords.value;
    filteredRecords.value = data.total || filteredRecords.value;

    if (mapped.length) {
      currentPage.value = nextPage;
      const combined = [...rows.value, ...mapped];
      rows.value = sortField.value ? combined : sortRows(combined);
    }
    hasMore.value = mapped.length > 0 && rows.value.length < totalRecords.value;
  } catch (_) {
    // se reintentará en el próximo scroll
  } finally {
    loadingMore.value = false;
  }
}

function onWindowScroll() {
  const scrollPosition = window.innerHeight + window.scrollY;
  const threshold = document.documentElement.scrollHeight - 300;
  if (scrollPosition >= threshold) {
    cargarMasDesdeDB();
  }
}

async function onSort(event) {
  sortField.value = event.sortField || null;
  sortOrder.value = event.sortOrder || null;
  currentPage.value = 1;
  await cargarDesdeDB();
}

function toIsoDate(value) {
  if (!value) return '';
  const d = value instanceof Date ? value : new Date(value);
  if (Number.isNaN(d.getTime())) return '';
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  return `${y}-${m}-${day}`;
}

function activeFilters() {
  const payload = {};
  Object.entries(filters.value).forEach(([key, value]) => {
    if (key === 'fecha_desde' || key === 'fecha_hasta') return;
    const cleaned = String(value || '').trim();
    if (cleaned) payload[key] = cleaned;
  });

  const desde = toIsoDate(filters.value.fecha_desde);
  const hasta = toIsoDate(filters.value.fecha_hasta);
  if (desde) payload.activation_date_from = desde;
  if (hasta) payload.activation_date_to = hasta;

  return payload;
}

function sortRows(list) {
  return [...list].sort((a, b) => {
    const dateA = toSortableDate(a.activation_date);
    const dateB = toSortableDate(b.activation_date);
    if (dateA !== dateB) return dateB - dateA;

    const createdA = toSortableDate(a.creado_en);
    const createdB = toSortableDate(b.creado_en);
    if (createdA !== createdB) return createdB - createdA;

    return String(b.id || 0).localeCompare(String(a.id || 0), undefined, { numeric: true });
  });
}

function toSortableDate(value) {
  const parsed = Date.parse(value || '');
  return Number.isNaN(parsed) ? 0 : parsed;
}

function mapDbRow(r) {
  return {
    id: r.id,
    tipo: r.tipo || 'activacion',
    activation_date: r.activation_date || '',
    creado_en: r.creado_en || '',
    deaccount: r.deaccount || '',
    accountName: r.account_name || '',
    userName: r.account_name || '',
    plataforma: r.plataforma || '',
    imei: r.imei || '',
    iccid: r.iccid || '',
    deviceMobile: r.device_mobile || '',
    vigencia_sim: r.vigencia_sim || '',
    sim_state: r.sim_state || '',
    sim_customer_status: r.sim_customer_status || '',
    suspendido_desde: r.suspendido_desde || '',
    verificado_en: r.verificado_en || '',
    data_usage_mb: r.data_usage_mb ?? null,
    sin_trafico: !!r.sin_trafico
  };
}

function fechaCorta(v) {
  if (!v) return '';
  return String(v).slice(0, 10);
}

async function cargarSolucionesSimpro() {
  if (solucionesSimpro.value.length || cargandoSoluciones.value) return;
  cargandoSoluciones.value = true;
  try {
    const data = await getCustomerSolutions();
    const arr = Array.isArray(data) ? data : (data?.customer_solutions || data?.solutions || []);
    solucionesSimpro.value = arr.map(s => {
      const name = s.customer_solution || s.name || String(s);
      return { label: name, value: name };
    });
  } catch {
    solucionesSimpro.value = [];
  }
  cargandoSoluciones.value = false;
}

async function cargarCuentasSimpro() {
  if (cuentasSimpro.value.length || cargandoCuentas.value) return;
  cargandoCuentas.value = true;
  try {
    const data = await getBillingAccounts();
    const arr = Array.isArray(data) ? data : (data?.billing_accounts || []);
    cuentasSimpro.value = arr.map(a => ({
      label: `${a.account_number || ''} ${a.name || ''}`.trim() || String(a),
      value: a.account_number || ''
    }));
  } catch {
    cuentasSimpro.value = [];
  }
  cargandoCuentas.value = false;
}

function abrirAccionesSimpro(rowData) {
  router.push({ name: 'acciones-simpro', params: { id: rowData.id } });
}

function toggleAdmin() {
  showAdmin.value = !showAdmin.value;
  if (showAdmin.value) {
    cargarSolucionesSimpro();
    cargarCuentasSimpro();
  }
}

async function ejecutarActivar() {
  const iccids = activarIccids.value.split(/[\s,;]+/).map(s => s.trim()).filter(Boolean);
  if (!iccids.length || !activarSolucion.value) return;
  adminBusy.value = 'activar';
  message.value = '';
  try {
    await activarSimsSimpro({
      iccids,
      customerSolution: activarSolucion.value,
      billingAccountNumber: activarCuenta.value || undefined
    });
    message.value = `Activación solicitada para ${iccids.length} SIM(s).`;
    messageError.value = false;
    activarIccids.value = '';
  } catch (error) {
    message.value = error?.response?.data?.detail || error?.message || 'No se pudo activar.';
    messageError.value = true;
  } finally {
    adminBusy.value = '';
  }
}

async function cargarAlertas() {
  adminBusy.value = 'alertas';
  try {
    const data = await getAlertasConsumoSimpro();
    alertasTexto.value = JSON.stringify(data, null, 2).slice(0, 4000);
  } catch (error) {
    alertasTexto.value = 'Error: ' + (error?.response?.data?.detail || error?.message || 'falló');
  } finally {
    adminBusy.value = '';
  }
}

async function cargarFacturas() {
  adminBusy.value = 'facturas';
  try {
    const data = await getFacturasSimpro(facturasCuenta.value || undefined);
    facturasTexto.value = JSON.stringify(data, null, 2).slice(0, 4000);
  } catch (error) {
    facturasTexto.value = 'Error: ' + (error?.response?.data?.detail || error?.message || 'falló');
  } finally {
    adminBusy.value = '';
  }
}

async function aplicarFiltros() {
  currentPage.value = 1;
  await cargarDesdeDB();
}

async function toggleTipoFiltro(tipo) {
  filters.value.tipo = filters.value.tipo === tipo ? '' : tipo;
  currentPage.value = 1;
  await cargarDesdeDB();
}

async function limpiarFiltros() {
  filters.value = {
    tipo: '',
    deaccount: '',
    plataforma: '',
    imei: '',
    vigencia_sim: '',
    fecha_desde: null,
    fecha_hasta: null,
    estado_simpro: 'activos',
  };
  currentPage.value = 1;
  await cargarDesdeDB();
}

async function consultar() {
  sanitizeImei();
  sanitizeSimTelefono();

  if (!imei.value && !simTelefono.value) {
    message.value = 'Debes ingresar IMEI o SIM ESPAÑOL (telefono).';
    messageError.value = true;
    return;
  }

  if (!plataforma.value) {
    message.value = 'Debes seleccionar una plataforma.';
    messageError.value = true;
    return;
  }

  loading.value = true;
  message.value = '';
  messageError.value = false;

  try {
    if (!imei.value && simTelefono.value) {
      await prepararRegistroManualDesdeTelefono();
      return;
    }

    const data = await getDispositivoPorPlataforma(imei.value, plataforma.value);
    const row = await buildRowFromDispositivo(data);
    row.tipo = tipo.value;

    // SIMPRO reporta el SIM dado de baja pero se está registrando como
    // activación/renovación: ajustar a "cancelado" y avisar.
    let avisoBaja = '';
    if (esBajaSimpro(row.sim_customer_status) && ['activacion', 'renovacion'].includes(row.tipo)) {
      row.tipo = 'cancelado';
      avisoBaja = ` El SIM figura como "${row.sim_customer_status}" en SIMPRO — se guardó como Cancelado.`;
    }

    validateRow(row);

    await saveConsultaSim({
      tipo: row.tipo,
      activation_date: row.activation_date,
      deaccount: row.deaccount,
      account_name: row.accountName,
      plataforma: row.plataforma,
      imei: row.imei,
      iccid: row.iccid,
      device_mobile: row.deviceMobile,
      vigencia_sim: row.vigencia_sim
    });

    // Recargar página 1 desde BD
    currentPage.value = 1;
    await cargarDesdeDB();

    message.value = 'Consulta completada y guardada.' + avisoBaja;
    messageError.value = false;
  } catch (error) {
    message.value = error?.response?.data?.detail || error?.message || 'Error al consultar IMEI.';
    messageError.value = true;
  } finally {
    loading.value = false;
  }
}

function limpiar() {
  imei.value = '';
  simTelefono.value = '';
  message.value = '';
  messageError.value = false;
}

function validateRow(row) {
  const required = [
    row.tipo,
    row.activation_date,
    row.deaccount,
    row.accountName,
    row.plataforma,
    row.iccid,
    row.vigencia_sim
  ];
  if (required.some((v) => !String(v || '').trim())) {
    throw new Error('Datos incompletos; no se guardó el registro.');
  }

  const imeiVal = String(row.imei || '').trim();
  const simVal = String(row.deviceMobile || '').trim();
  if (!imeiVal && !simVal) {
    throw new Error('Debes capturar IMEI o SIM ESPAÑOL.');
  }
}

function openEdit(row) {
  editRow.value = { ...row };
  showEditDialog.value = true;
}

async function saveEdit() {
  try {
    editRow.value.imei = onlyDigits(editRow.value.imei);
    editRow.value.deviceMobile = onlyDigits(editRow.value.deviceMobile);

    validateRow(editRow.value);
    const payload = {
      tipo: editRow.value.tipo,
      activation_date: editRow.value.activation_date,
      deaccount: editRow.value.deaccount,
      account_name: editRow.value.accountName,
      plataforma: editRow.value.plataforma,
      imei: editRow.value.imei,
      iccid: editRow.value.iccid,
      device_mobile: editRow.value.deviceMobile,
      vigencia_sim: editRow.value.vigencia_sim
    };

    if (editRow.value.id) {
      await updateConsultaSim(editRow.value.id, payload);
      message.value = 'Registro actualizado.';
    } else {
      await saveConsultaSim(payload);
      message.value = 'Registro guardado.';
      currentPage.value = 1;
    }

    showEditDialog.value = false;
    messageError.value = false;
    await cargarDesdeDB();
  } catch (error) {
    message.value = error?.response?.data?.detail || error?.message || 'No se pudo actualizar.';
    messageError.value = true;
  }
}

async function removeRecord(row) {
  const ok = window.confirm('¿Eliminar este registro?');
  if (!ok) return;
  try {
    await deleteConsultaSim(row.id);
    message.value = 'Registro eliminado.';
    messageError.value = false;
    await cargarDesdeDB();
  } catch (error) {
    message.value = error?.response?.data?.detail || error?.message || 'No se pudo eliminar.';
    messageError.value = true;
  }
}

async function loadAllHistorico() {
  const allRows = [];
  const pageSizeAll = 100;
  let page = 1;

  while (true) {
    const data = await getConsultasSim(page, pageSizeAll);
    const items = (data.items || []).map(mapDbRow);
    allRows.push(...items);

    if (items.length < pageSizeAll) break;
    page += 1;
  }

  return sortRows(allRows);
}

async function buildRowFromDispositivo(apiResponse) {
  const plat = String(apiResponse?.plataforma || plataforma.value || '').toUpperCase();
  const raw = Array.isArray(apiResponse?.dispositivo)
    ? (apiResponse.dispositivo[0] || {})
    : (apiResponse?.dispositivo || {});

  let deaccount = '';
  let accountName = '';
  let userName = '';
  let mobileRaw = '';

  if (plat === 'TRACKSOLID') {
    deaccount = String(raw.account || '');
    accountName = String(raw.customerName || '');
    userName = String(raw.customerName || '');
    mobileRaw = String(raw.sim || raw.simNum || '');
  } else {
    const account = raw.account && typeof raw.account === 'object' ? raw.account : {};
    const brief = raw.deviceBrief && typeof raw.deviceBrief === 'object' ? raw.deviceBrief : {};
    deaccount = String(account.accountName || '');
    accountName = String(account.accountName || '');
    userName = String(account.userName || '');
    mobileRaw = String(brief.deviceMobile || raw.sim || raw.simNum || '');
  }

  let deviceMobile = onlyDigits(mobileRaw);
  if (!deviceMobile) {
    deviceMobile = onlyDigits(simTelefono.value);
  }
  if (!deviceMobile) {
    throw new Error('No se pudo extraer deviceMobile/sim con solo números.');
  }

  const simInfo = await getSimDetails(deviceMobile);

  // contract_end_date puede venir en el top-level (server actualizado)
  // o dentro de items[0].active_connection (server aún sin reiniciar)
  const firstItem = Array.isArray(simInfo?.items) && simInfo.items.length ? simInfo.items[0] : null;
  const activeConn = firstItem?.active_connection || {};
  const vigencia = simInfo?.contract_end_date || activeConn?.contract_end_date || '';
  const customerStatus = simInfo?.customer_status
    || (typeof activeConn?.customer_status === 'object' ? activeConn.customer_status?.ident : activeConn?.customer_status)
    || '';

  return {
    activation_date: simInfo?.activation_date || activeConn?.activation_date || '',
    deaccount,
    accountName,
    userName,
    plataforma: plat || plataforma.value,
    imei: imei.value,
    iccid: simInfo?.iccid || firstItem?.iccid || '',
    deviceMobile,
    vigencia_sim: vigencia,
    sim_customer_status: String(customerStatus || '')
  };
}

const SIMPRO_ESTADOS_BAJA = ['ceased', 'cancelled', 'canceled', 'terminated', 'stopped'];
function esBajaSimpro(status) {
  return SIMPRO_ESTADOS_BAJA.includes(String(status || '').trim().toLowerCase());
}

async function prepararRegistroManualDesdeTelefono() {
  const sim = onlyDigits(simTelefono.value);
  let simInfo = null;

  if (sim) {
    try {
      simInfo = await getSimDetails(sim);
    } catch {
      simInfo = null;
    }
  }

  const firstItem = Array.isArray(simInfo?.items) && simInfo.items.length ? simInfo.items[0] : null;
  const activeConn = firstItem?.active_connection || {};

  editRow.value = {
    tipo: tipo.value,
    activation_date: simInfo?.activation_date || activeConn?.activation_date || '',
    deaccount: '',
    accountName: '',
    plataforma: plataforma.value || '',
    imei: '',
    iccid: simInfo?.iccid || firstItem?.iccid || '',
    deviceMobile: sim,
    vigencia_sim: simInfo?.contract_end_date || activeConn?.contract_end_date || ''
  };

  showEditDialog.value = true;
  message.value = 'Completa los campos faltantes y guarda el nuevo registro.';
  messageError.value = false;
}

function onlyDigits(v) {
  return String(v || '').replace(/\D+/g, '');
}

function isIncompleto(row) {
  const required = [row.tipo, row.activation_date, row.deaccount, row.accountName, row.plataforma, row.iccid, row.vigencia_sim];
  return required.some((v) => !String(v || '').trim());
}

function esVencido(vigenciaSim) {
  const raw = String(vigenciaSim || '').slice(0, 10);
  const fecha = Date.parse(raw);
  if (Number.isNaN(fecha)) return false;

  const hoyUtc = Date.UTC(new Date().getFullYear(), new Date().getMonth(), new Date().getDate());
  const diasVencido = (hoyUtc - fecha) / (1000 * 60 * 60 * 24);
  return diasVencido >= 7;
}

async function importarSimpro() {
  importando.value = true;
  message.value = '';
  try {
    const result = await importarSimsSimpro();
    message.value = `SIMPRO: ${result.importados} nuevo(s) importado(s), ${result.omitidos} ya exist${result.omitidos === 1 ? 'ía' : 'ían'} (de ${result.total_simpro} en la plataforma).`;
    messageError.value = false;

    if (result.importados > 0) {
      currentPage.value = 1;
      await cargarDesdeDB();
    }
  } catch (error) {
    message.value = error?.response?.data?.detail || error?.message || 'No se pudo importar desde SIMPRO.';
    messageError.value = true;
  } finally {
    importando.value = false;
  }
}

async function refrescarSimpro() {
  refrescando.value = true;
  refrescarProgreso.value = '';
  message.value = '';
  messageError.value = false;
  let totalEstado = 0;
  let totalConsumo = 0;
  let totalProcesados = 0;
  let totalNuevos = 0;
  try {
    // Recorre TODO en tandas hasta que no queden pendientes (tope de vueltas
    // por seguridad).
    for (let vuelta = 0; vuelta < 40; vuelta++) {
      const r = await refrescarSimproSims();
      totalEstado += r.estado_ok || 0;
      totalConsumo += r.consumo_ok || 0;
      totalProcesados += r.procesados || 0;
      totalNuevos += r.nuevos || 0;
      refrescarProgreso.value = `Procesados ${totalProcesados}, faltan ${r.restantes}...`;
      if (!r.procesados || !r.restantes) break;
    }
    message.value = `Actualización SIMPRO: ${totalNuevos} SIM nuevo(s), estado en ${totalEstado}, consumo en ${totalConsumo} (${totalProcesados} revisados).`;
    currentPage.value = 1;
    await cargarDesdeDB();
  } catch (error) {
    message.value = error?.response?.data?.detail || error?.message || 'El refresco SIMPRO falló.';
    messageError.value = true;
  } finally {
    refrescando.value = false;
    refrescarProgreso.value = '';
  }
}

async function completarDatos() {
  completando.value = true;
  message.value = '';
  try {
    const r = await completarDatosSims();
    message.value = `Completar datos: ${r.actualizados} registro(s) actualizado(s) de ${r.procesados} revisado(s). Quedan ${r.restantes} incompleto(s)${r.restantes ? ' — vuelve a correr para seguir.' : '.'}`;
    messageError.value = false;
    currentPage.value = 1;
    await cargarDesdeDB();
  } catch (error) {
    message.value = error?.response?.data?.detail || error?.message || 'No se pudo completar datos.';
    messageError.value = true;
  } finally {
    completando.value = false;
  }
}

function exportarExcel() {
  if (!rows.value.length) return;

  loadAllHistorico()
    .then((historico) => {
      if (!historico.length) return;

      const rowsToExport = historico.map((r) => ({
    TIPO: r.tipo,
    'Fecha. Act': r.activation_date,
    USUARIO: r.deaccount,
    CLIENTE: r.accountName,
    PLATAFORMA: r.plataforma,
    IMEI: r.imei,
    ICCID: r.iccid,
    'SIM ESPAÑOL': r.deviceMobile,
    'VIGENCIA SIM': r.vigencia_sim
      }));

      const ws = XLSX.utils.json_to_sheet(rowsToExport);
      const wb = XLSX.utils.book_new();
      XLSX.utils.book_append_sheet(wb, ws, 'reporte');
      XLSX.writeFile(wb, `reporte_sim_${stamp()}.xlsx`);
    })
    .catch((error) => {
      message.value = error?.response?.data?.detail || error?.message || 'No se pudo exportar el histórico completo.';
      messageError.value = true;
    });
}

function stamp() {
  const d = new Date();
  const y = d.getFullYear();
  const m = String(d.getMonth() + 1).padStart(2, '0');
  const day = String(d.getDate()).padStart(2, '0');
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const ss = String(d.getSeconds()).padStart(2, '0');
  return `${y}${m}${day}_${hh}${mm}${ss}`;
}

onMounted(() => {
  cargarDesdeDB();
  window.addEventListener('scroll', onWindowScroll);
});

onUnmounted(() => {
  window.removeEventListener('scroll', onWindowScroll);
});
</script>

<style scoped>
.util-page {
  padding: 1.25rem;
}

.util-hero h1 {
  margin: 0;
  color: var(--color-title);
}

.util-hero p {
  margin-top: 0.4rem;
  color: var(--color-text);
}

.util-card {
  margin-top: 1rem;
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
}

.filters-panel {
  margin-top: 1rem;
}

.util-grid {
  display: grid;
  grid-template-columns: repeat(3, minmax(180px, 1fr));
  gap: 1rem;
}

.field {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}

.field label {
  font-weight: 600;
}

.field input,
.field :deep(.p-inputtext),
.field :deep(.p-dropdown) {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  min-height: 40px;
  padding: 0.5rem 0.65rem;
}

.actions {
  margin-top: 1rem;
  display: flex;
  gap: 0.6rem;
  flex-wrap: wrap;
}

.btn {
  border: 0;
  border-radius: 8px;
  min-height: 40px;
  padding: 0.4rem 0.9rem;
  cursor: pointer;
}

.btn:disabled {
  opacity: 0.65;
  cursor: not-allowed;
}

.btn-primary {
  background: var(--color-title);
  color: var(--color-bg);
}

.btn-light {
  background: var(--color-bg);
  border: 1px solid var(--color-border);
  color: var(--color-text);
}

.status {
  margin-top: 0.8rem;
  font-weight: 600;
}

.is-ok {
  color: #238636;
}

.is-error {
  color: #d1242f;
}

.result {
  margin-top: 1rem;
  border-top: 1px solid var(--color-border);
  padding-top: 1rem;
}

.result h2 {
  margin: 0 0 0.8rem;
}

.result :deep(.p-datatable-table) {
  min-width: 980px;
}

.result :deep(.p-datatable-header) {
  background: transparent;
  border: 0;
  padding: 0 0 0.75rem;
}

.table-tools {
  display: grid;
  gap: 0.75rem;
}

.table-tools__summary {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.summary-pill {
  display: inline-flex;
  align-items: center;
  border-radius: 999px;
  padding: 0.3rem 0.7rem;
  background: var(--color-title);
  color: var(--color-bg);
  font-weight: 700;
  font-size: 0.85rem;
}

.summary-pill--tipo {
  border: 1px solid var(--color-border);
  background: var(--color-bg);
  color: var(--color-text);
  cursor: pointer;
}

.summary-pill--tipo.is-active {
  background: var(--color-title);
  color: var(--color-bg);
  border-color: var(--color-title);
}

.table-tools__filters {
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
}

.table-tools__filters :deep(.p-inputtext),
.table-tools__filters :deep(.p-dropdown) {
  width: 100%;
}

.table-tools__buttons {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
}

.loading-more {
  text-align: center;
  padding: 0.9rem 0;
  color: var(--color-text);
  font-weight: 600;
}

.row-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}

.hint {
  margin-top: 0.6rem;
  font-size: 0.8rem;
  color: var(--color-text);
  opacity: 0.75;
}

.filtro-check {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  white-space: nowrap;
}

.muted { color: var(--color-border); }
.muted-small { font-size: 0.72rem; color: var(--color-border); }

.admin-toggle {
  display: flex;
  align-items: center;
  justify-content: space-between;
  width: 100%;
  background: transparent;
  border: 0;
  cursor: pointer;
  font-weight: 700;
  color: var(--color-title);
  font-size: 1rem;
}
.admin-toggle span { display: flex; align-items: center; gap: 0.5rem; }
.admin-body {
  margin-top: 1rem;
  display: flex;
  flex-direction: column;
  gap: 1.25rem;
}
.admin-block {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.admin-block h3 {
  margin: 0;
  font-size: 0.9rem;
  color: var(--color-title);
}
.admin-block textarea {
  width: 100%;
  border: 1px solid var(--color-border);
  border-radius: 8px;
  padding: 0.5rem;
  font-family: inherit;
}
.admin-pre {
  background: var(--color-bg-light, #f5f5f5);
  border-radius: 8px;
  padding: 0.6rem;
  font-size: 0.75rem;
  max-height: 260px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}

.edit-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.8rem;
}

@media (max-width: 760px) {
  .util-grid {
    grid-template-columns: 1fr;
  }

  .table-tools__filters {
    grid-template-columns: 1fr;
  }
}
</style>
