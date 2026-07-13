<template>
  <section class="util-page">
    <header class="util-hero">
      <h1>SIM ESPAÑOL</h1>
      <p>Agrega un nuevo registro arriba y usa los filtros dentro de la tabla para buscar en el histórico.</p>
    </header>

    <div class="util-card util-form-card">
      <div class="section-head">
        <div>
          <h2>Nuevo registro</h2>
          <p>Captura IMEI y plataforma para consultar y guardar un nuevo movimiento.</p>
        </div>
      </div>

      <div class="util-grid">
        <div class="field">
          <label for="tipo">Tipo</label>
          <Dropdown
            id="tipo"
            v-model="tipo"
            :options="tiposOptions"
            optionLabel="label"
            optionValue="value"
            class="w-full"
          />
        </div>

        <div class="field">
          <label for="imei">IMEI</label>
          <InputText
            id="imei"
            v-model="imei"
            placeholder="Ej. 353549093223336"
            @input="sanitizeImei"
            inputmode="numeric"
          />
        </div>

        <div class="field">
          <label for="simTelefono">SIM ESPAÑOL (teléfono)</label>
          <InputText
            id="simTelefono"
            v-model="simTelefono"
            placeholder="Ej. 8713056103"
            @input="sanitizeSimTelefono"
            inputmode="numeric"
          />
        </div>

        <div class="field">
          <label for="plataforma">Plataforma</label>
          <Dropdown
            id="plataforma"
            v-model="plataforma"
            :options="plataformas"
            optionLabel="label"
            optionValue="value"
            placeholder="Selecciona una plataforma"
            class="w-full"
          />
        </div>
      </div>

      <div class="actions">
        <Button :label="loading ? 'Agregando...' : 'Agregar'" icon="pi pi-search" :loading="loading" :disabled="loading" @click="consultar" />
        <Button label="Exportar Excel" icon="pi pi-file-excel" :disabled="!rows.length || loading" @click="exportarExcel" />
        <Button label="Limpiar" icon="pi pi-eraser" severity="secondary" outlined :disabled="loading" @click="limpiar" />
      </div>
    </div>

    <!-- <div class="util-card">
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
      </div>
    </div> -->

      <p v-if="message" :class="['status', messageError ? 'is-error' : 'is-ok']">{{ message }}</p>

      <div class="result">
        <h2>Resultados</h2>
        <DataTable
          :value="rows"
          stripedRows
          size="small"
          paginator
          :rows="pageSize"
          :totalRecords="totalRecords"
          lazy
          @page="onPage"
          responsiveLayout="scroll"
        >
          <template #header>
            <div class="table-tools">
              <div class="table-tools__summary">
                <span class="summary-pill">Histórico: {{ historicalRecords }}</span>
                <span class="summary-pill">Filtrados: {{ filteredRecords }}</span>
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
                <Dropdown
                  v-model="filters.vigencia_sim"
                  :options="vigenciaSimOptions"
                  optionLabel="label"
                  optionValue="value"
                  placeholder="Vigencia SIM"
                  showClear
                />
                <div class="table-tools__buttons">
                  <Button label="Buscar" icon="pi pi-search" @click="aplicarFiltros" :loading="loading" />
                  <Button label="Limpiar" icon="pi pi-filter-slash" severity="secondary" outlined @click="limpiarFiltros" :disabled="loading" />
                </div>
              </div>
            </div>
          </template>
          <Column field="tipo" header="TIPO">
            <template #body="{ data }">
              <Tag
                :value="data.tipo"
                :severity="data.tipo === 'activacion' ? 'success' : data.tipo === 'renovacion' ? 'info' : 'danger'"
              />
            </template>
          </Column>
          <Column field="activation_date" header="Fecha. Act">
            <template #body="{ data }">{{ data.activation_date || '-' }}</template>
          </Column>
          <Column field="deaccount" header="USUARIO">
            <template #body="{ data }">{{ data.deaccount || '-' }}</template>
          </Column>
          <Column field="accountName" header="CLIENTE">
            <template #body="{ data }">{{ data.accountName || '-' }}</template>
          </Column>
          <Column field="plataforma" header="PLATAFORMA">
            <template #body="{ data }">{{ data.plataforma || '-' }}</template>
          </Column>
          <Column field="imei" header="IMEI">
            <template #body="{ data }">{{ data.imei || '-' }}</template>
          </Column>
          <Column field="iccid" header="ICCID">
            <template #body="{ data }">{{ data.iccid || '-' }}</template>
          </Column>
          <Column field="deviceMobile" header="SIM ESPAÑOL">
            <template #body="{ data }">{{ data.deviceMobile || '-' }}</template>
          </Column>
          <Column field="vigencia_sim" header="VIGENCIA SIM">
            <template #body="{ data }">
              <span>{{ data.vigencia_sim || '-' }}</span>
              <Tag v-if="esVencido(data.vigencia_sim)" value="Vencido" severity="danger" style="margin-left: 6px;" />
            </template>
          </Column>
          <Column header="ESTADO" style="min-width: 120px">
            <template #body="{ data }">
              <Tag v-if="isIncompleto(data)" value="Sin datos" severity="danger" />
              <Tag v-else value="Completo" severity="success" />
            </template>
          </Column>
          <Column header="ACCIONES" style="min-width: 140px">
            <template #body="{ data }">
              <div class="row-actions">
                <Button icon="pi pi-pencil" text rounded severity="info" @click="openEdit(data)" />
                <Button icon="pi pi-trash" text rounded severity="danger" @click="removeRecord(data)" />
              </div>
            </template>
          </Column>
        </DataTable>
      </div>

    <Dialog v-model:visible="showEditDialog" :header="editRow.id ? 'Editar Registro' : 'Nuevo Registro Manual'" :style="{ width: '520px' }" modal>
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
import { onMounted, ref } from 'vue';
import * as XLSX from 'xlsx';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
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
  updateConsultaSim
} from '@/services/utilidadesImeiService';

const imei = ref('');
const simTelefono = ref('');
const plataforma = ref('');
const plataformas = ref([]);
const tipo = ref('activacion');
const tiposOptions = [
  { label: 'Activación', value: 'activacion' },
  { label: 'Renovación', value: 'renovacion' },
  { label: 'Cancelado', value: 'cancelado' }
];
const filterTipoOptions = [
  { label: 'Activación', value: 'activacion' },
  { label: 'Renovación', value: 'renovacion' },
  { label: 'Cancelado', value: 'cancelado' }
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
const pageSize = ref(10);
const currentPage = ref(1);
const showEditDialog = ref(false);
const editRow = ref({});
const importando = ref(false);
const filters = ref({
  tipo: '',
  deaccount: '',
  plataforma: '',
  imei: '',
  vigencia_sim: '',
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

    const data = await getConsultasSim(currentPage.value, pageSize.value, activeFilters());
    totalRecords.value = data.total || 0;
    filteredRecords.value = data.total || 0;
    rows.value = sortRows((data.items || []).map(mapDbRow));
  } catch (_) {
    // tabla aún no creada o error de red — no interrumpir
  }
}

function activeFilters() {
  const payload = {};
  Object.entries(filters.value).forEach(([key, value]) => {
    const cleaned = String(value || '').trim();
    if (cleaned) payload[key] = cleaned;
  });
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
    vigencia_sim: r.vigencia_sim || ''
  };
}

async function onPage(event) {
  currentPage.value = event.page + 1;
  await cargarDesdeDB();
}

async function aplicarFiltros() {
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

    message.value = 'Consulta completada y guardada.';
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

  return {
    activation_date: simInfo?.activation_date || activeConn?.activation_date || '',
    deaccount,
    accountName,
    userName,
    plataforma: plat || plataforma.value,
    imei: imei.value,
    iccid: simInfo?.iccid || firstItem?.iccid || '',
    deviceMobile,
    vigencia_sim: vigencia
  };
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

onMounted(loadPlataformas);
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

.row-actions {
  display: flex;
  align-items: center;
  gap: 0.25rem;
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
