<template>
  <section class="util-page">
    <header class="util-hero">
      <h1>SIM ESPAÑOL</h1>
      <p>Listado de SIMs. Usa los filtros dentro de la tabla para buscar en el histórico.</p>
    </header>

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
<!--                 <Dropdown
                  v-model="filters.salud"
                  :options="saludOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Salud"
                  showClear
                  @change="aplicarFiltros"
                /> -->
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
            <template #body="{ data }">{{ fechaMes(data.activation_date) }}</template>
          </Column>
          <Column field="vigencia_sim" header="VIGENCIA SIM" sortable>
            <template #body="{ data }">
              <span>{{ fechaMes(data.vigencia_sim) }}</span>
              <Tag v-if="esVencido(data.vigencia_sim)" value="Vencido" severity="danger" style="margin-left: 6px;" />
            </template>
          </Column>
          <Column field="dias_restantes" header="DIAS RESTANTES">
            <template #body="{ data }">
              <span v-if="data.dias_restantes != null" :class="{ 'is-error': data.dias_restantes < 0 }">
                {{ data.dias_restantes }}
              </span>
              <span v-else class="muted">—</span>
            </template>
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
<!--             <template #body="{ data }">
              {{ data.imei || '-' }}
              <Tag
                v-if="imeiMismatch(data.network_imei, data.imei)"
                value="≠ red"
                severity="danger"
                style="margin-left:6px;"
                v-tooltip.top="`SIMPRO ve el IMEI ${data.network_imei} en la red`"
              />
            </template> -->
          </Column>
          <Column field="iccid" header="ICCID" sortable>
            <template #body="{ data }">{{ data.iccid || '-' }}</template>
          </Column>
          <Column field="deviceMobile" header="SIM ESPAÑOL" sortable>
            <template #body="{ data }">{{ data.deviceMobile || '-' }}</template>
          </Column>

          <Column field="tecnico" header="TECNICO" sortable>
            <template #body="{ data }">{{ data.tecnico || '-' }}</template>
          </Column>
<!--           <Column field="num_cliente" header="NUM. CLIENTE" sortable>
            <template #body="{ data }">{{ data.num_cliente || '-' }}</template>
          </Column> -->
          <Column field="comentarios" header="COMENTARIOS">
            <template #body="{ data }">{{ data.comentarios || '-' }}</template>
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
        <div class="field">
          <label>Técnico</label>
          <InputText v-model="editRow.tecnico" />
        </div>
<!--         <div class="field">
          <label>Núm. cliente</label>
          <InputText v-model="editRow.num_cliente" />
        </div> -->
        <div class="field" style="grid-column: 1 / -1;">
          <label>Comentarios</label>
          <InputText v-model="editRow.comentarios" />
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
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Calendar from 'primevue/calendar';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Tag from 'primevue/tag';
import Dialog from 'primevue/dialog';
import {
  getConsultasSim,
  saveConsultaSim,
  updateConsultaSim,
  refrescarSimproSims
} from '@/services/utilidadesImeiService';

const router = useRouter();

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
const saludOptions = [
  { label: 'OK', value: 'ok' },
  { label: 'Sin conexión', value: 'sin_conexion' },
  { label: 'Sin tráfico', value: 'sin_trafico' },
  { label: 'Bloqueado', value: 'bloqueado' },
  { label: 'Suspendido', value: 'suspendido' },
  { label: 'Baja', value: 'baja' },
  { label: 'Desconocido', value: 'desconocido' }
];
const SALUD_TAG = {
  ok: { value: 'OK', severity: 'success' },
  sin_conexion: { value: 'Sin conexión', severity: 'danger' },
  sin_trafico: { value: 'Sin tráfico', severity: 'warning' },
  bloqueado: { value: 'Bloqueado', severity: 'danger' },
  suspendido: { value: 'Suspendido', severity: 'warning' },
  baja: { value: 'Baja', severity: 'secondary' },
  desconocido: { value: '—', severity: 'contrast' }
};
function saludTag(s) {
  return SALUD_TAG[s] || SALUD_TAG.desconocido;
}
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
const refrescando = ref(false);
const refrescarProgreso = ref('');
const filters = ref({
  tipo: '',
  deaccount: '',
  plataforma: '',
  imei: '',
  vigencia_sim: '',
  fecha_desde: null,
  fecha_hasta: null,
  estado_simpro: '',
  salud: '',
});

async function cargarDesdeDB() {
  loading.value = true;
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
  } finally {
    loading.value = false;
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
    dias_restantes: diasRestantes(r.vigencia_sim),
    tecnico: r.tecnico || '',
    num_cliente: r.num_cliente || '',
    comentarios: r.comentarios || '',
    sim_state: r.sim_state || '',
    sim_customer_status: r.sim_customer_status || '',
    suspendido_desde: r.suspendido_desde || '',
    verificado_en: r.verificado_en || '',
    data_usage_mb: r.data_usage_mb ?? null,
    sin_trafico: !!r.sin_trafico,
    imei_lock: r.imei_lock == null ? null : Number(r.imei_lock),
    imei_lock_imei: r.imei_lock_imei || '',
    network_imei: r.network_imei || '',
    last_seen: r.last_seen || '',
    salud: r.salud || 'desconocido'
  };
}

// Vigencia = fecha de activación + 365 días (fórmula del Excel SIM ESPAÑOL).
// Días restantes = vigencia - hoy. Negativo = vencida.
function diasRestantes(vigenciaSim) {
  const raw = String(vigenciaSim || '').slice(0, 10);
  const fecha = Date.parse(raw);
  if (Number.isNaN(fecha)) return null;
  const hoyUtc = Date.UTC(new Date().getFullYear(), new Date().getMonth(), new Date().getDate());
  return Math.round((fecha - hoyUtc) / (1000 * 60 * 60 * 24));
}

function fechaCorta(v) {
  if (!v) return '';
  return String(v).slice(0, 10);
}

const MESES_ES = ['Ene', 'Feb', 'Mar', 'Abr', 'May', 'Jun', 'Jul', 'Ago', 'Sep', 'Oct', 'Nov', 'Dic'];
// "2025-04-15" -> "15 Abr 2025"
function fechaMes(v) {
  const m = /^(\d{4})-(\d{2})-(\d{2})/.exec(String(v || ''));
  if (!m) return v || '-';
  return `${m[3]} ${MESES_ES[Number(m[2]) - 1] || m[2]} ${m[1]}`;
}

// Red = IMEISV 16 díg; registro = IMEI 15. Comparar núcleo de 14.
function imeiMismatch(redImei, regImei) {
  const a = String(redImei || '').replace(/\D+/g, '').slice(0, 14);
  const b = String(regImei || '').replace(/\D+/g, '').slice(0, 14);
  return !!a && !!b && a !== b;
}

function abrirAccionesSimpro(rowData) {
  router.push({ name: 'acciones-simpro', params: { id: rowData.id } });
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
    estado_simpro: '',
    salud: '',
  };
  currentPage.value = 1;
  await cargarDesdeDB();
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
      vigencia_sim: editRow.value.vigencia_sim,
      tecnico: editRow.value.tecnico || '',
      num_cliente: editRow.value.num_cliente || '',
      comentarios: editRow.value.comentarios || ''
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

function onlyDigits(v) {
  return String(v || '').replace(/\D+/g, '');
}

function esVencido(vigenciaSim) {
  const raw = String(vigenciaSim || '').slice(0, 10);
  const fecha = Date.parse(raw);
  if (Number.isNaN(fecha)) return false;

  const hoyUtc = Date.UTC(new Date().getFullYear(), new Date().getMonth(), new Date().getDate());
  const diasVencido = (hoyUtc - fecha) / (1000 * 60 * 60 * 24);
  return diasVencido >= 7;
}

async function refrescarSimpro() {
  refrescando.value = true;
  refrescarProgreso.value = '';
  message.value = '';
  messageError.value = false;
  try {
    // Solo da de alta los SIM nuevos de SIMPRO. No toca lo existente.
    const r = await refrescarSimproSims();
    message.value = `Actualización SIMPRO: ${r.nuevos || 0} SIM nuevo(s) (${r.ya_existian || 0} ya existían).`;
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
