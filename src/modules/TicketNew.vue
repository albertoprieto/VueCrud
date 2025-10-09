<template>
  <div class="ticket-page">
    <h2 class="title">Nuevo Ticket</h2>
    <form @submit.prevent="submit">
      <div class="grid">
        <div class="col">
          <label>Reporte de servicio</label>
          <AutoComplete
            v-model="selectedReporte"
            :suggestions="reporteOptions"
            optionLabel="__label"
            :minLength="1"
            :delay="200"
            :dropdown="true"
            forceSelection
            placeholder="Busca por folio, cliente, id..."
            class="w-100"
            @complete="searchReportes"
            @item-select="onReporteSelect"
          />
          <small v-if="ctx">Folio: {{ ctx.folio_reporte || '-' }} · Venta: {{ ctx.folio_venta || '-' }} · Cliente: {{ ctx.nombre_cliente || ctx.cliente_nombre || '-' }}</small>
        </div>
        <div class="col">
          <label>Título</label>
          <input v-model="titulo" type="text" required class="p-inputtext" placeholder="Resumen corto"/>
        </div>
      </div>
      <div class="grid">
        <div class="col">
          <label>Descripción</label>
          <textarea v-model="descripcion" class="p-inputtextarea" rows="5" required placeholder="Describe el problema"/>
        </div>
        <div class="col">
          <label>Prioridad</label>
          <Dropdown v-model="prioridad" :options="prioridadOptions" optionLabel="label" optionValue="value" class="w-100" />
          <label class="mt-2">Tipo</label>
          <Dropdown v-model="tipo" :options="tipoOptions" optionLabel="label" optionValue="value" class="w-100" />
        </div>
      </div>

      <div class="mt-2 card">
        <div class="section-title">IMEIs del reporte</div>
        <div class="chips">
          <span v-for="i in imeis" :key="i" class="chip">{{ i }}</span>
          <span v-if="!imeis.length" class="muted">(sin IMEIs en contexto)</span>
        </div>
      </div>

      <div class="mt-3 actions">
        <button class="p-button" type="submit"><span class="pi pi-save mr-2"/>Crear</button>
        <router-link to="/tickets" class="p-button p-button-text ml-2">Cancelar</router-link>
      </div>
    </form>
    <Toast/>
    <ConfirmDialog/>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { useTicketsStore } from '@/stores/ticketsStore';
import AutoComplete from 'primevue/autocomplete';
import { getReportesServicioTodos } from '@/services/reportesService';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Dropdown from 'primevue/dropdown';
import { useLoginStore } from '@/stores/loginStore';
import { getTickets as apiGetTickets } from '@/services/ticketsService';

const router = useRouter();
const route = useRoute();
const store = useTicketsStore();
const toast = useToast();
const confirm = useConfirm();
const login = useLoginStore();

const reporteId = ref(Number(route.query.reporteId) || undefined);
const selectedReporte = ref(null);
const reporteOptions = ref([]);
const ctx = ref(null);
const imeis = ref([]);

const titulo = ref('');
const descripcion = ref('');
const prioridad = ref('media');
const tipo = ref('soporte');
const autor = ref(login?.user?.username || login?.user?.nombre || login?.user?.email || '');
const prioridadOptions = [
  { label: 'Baja', value: 'baja' },
  { label: 'Media', value: 'media' },
  { label: 'Alta', value: 'alta' },
  { label: 'Crítica', value: 'crítica' },
];
const tipoOptions = [
  { label: 'Soporte', value: 'soporte' },
  { label: 'Garantía', value: 'garantía' },
  { label: 'Posventa', value: 'posventa' },
  { label: 'Otro', value: 'otro' },
];

async function loadContext() {
  if (!reporteId.value) { ctx.value = null; imeis.value = []; return; }
  const c = await store.getContext(reporteId.value);
  ctx.value = c || null;
  // Soportar imeis_json (array) o imeis_concat
  if (Array.isArray(c?.imeis_json)) imeis.value = c.imeis_json.filter(Boolean);
  else if (typeof c?.imeis_concat === 'string' && c.imeis_concat.length) imeis.value = c.imeis_concat.split(',').map(s=>s.trim()).filter(Boolean);
  else imeis.value = [];
}

if (reporteId.value) loadContext();

async function searchReportes(e) {
  const q = String(e?.query || '').toLowerCase().trim();
  try {
    const all = await getReportesServicioTodos();
    const mapped = (Array.isArray(all) ? all : []).map(r => ({
      ...r,
      __label: makeReporteLabel(r)
    }));
    let out = mapped;
    if (q) {
      out = mapped.filter(r =>
        String(r.id || '').includes(q) ||
        String(r.folio || '').toLowerCase().includes(q) ||
        String(r.nombre_cliente || '').toLowerCase().includes(q) ||
        String(r.nombre_instalador || '').toLowerCase().includes(q)
      );
    }
    reporteOptions.value = out.slice(0, 25);
  } catch (err) {
    reporteOptions.value = [];
  }
}

function makeReporteLabel(r) {
  const id = r?.id ?? '-';
  const folio = r?.folio ?? '-';
  const cliente = r?.nombre_cliente ?? '-';
  const fecha = (r?.fecha || '').toString().slice(0, 10);
  return `#${id} · ${folio} · ${cliente} · ${fecha}`;
}

function onReporteSelect(ev) {
  const item = ev?.value;
  if (item?.id) {
    reporteId.value = Number(item.id);
    loadContext();
    checkOpenTicket();
  }
}

async function submit() {
  if (!reporteId.value) {
    toast.add({ severity: 'warn', summary: 'Falta reporte', detail: 'Selecciona un reporte de servicio', life: 2500 });
    return;
  }
  confirm.require({
    message: '¿Crear ticket con la información capturada?',
    header: 'Confirmar creación',
    icon: 'pi pi-question-circle',
    acceptLabel: 'Sí, crear',
    rejectLabel: 'Cancelar',
    accept: async () => {
      try {
        const payload = {
          reporteId: reporteId.value,
          titulo: titulo.value,
          descripcion: descripcion.value,
          prioridad: prioridad.value,
          tipo: tipo.value,
          imeis: imeis.value,
          clienteId: ctx.value?.cliente_id,
          clienteNombre: ctx.value?.nombre_cliente || ctx.value?.cliente_nombre || selectedReporte.value?.nombre_cliente,
          autor: autor.value || undefined,
          createdByUserId: login?.user?.id || undefined,
        };
        const t = await store.create(payload);
        toast.add({ severity: 'success', summary: 'Ticket creado', detail: `Ticket #${t.id}`, life: 2500 });
        router.push(`/tickets/${t.id}`);
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo crear el ticket', life: 3000 });
      }
    }
  });
}

async function checkOpenTicket() {
  try {
    if (!reporteId.value) return;
    const list = await apiGetTickets({ reporteId: reporteId.value });
    const abiertos = (Array.isArray(list) ? list : []).filter(t => ['nuevo','en_progreso','en_espera'].includes(t.estado));
    if (abiertos.length) {
      confirm.require({
        message: `Ya existe un ticket abierto para este reporte (p. ej. #${abiertos[0].id}).`,
        header: 'Ticket existente',
        icon: 'pi pi-info-circle',
        acceptLabel: 'Entendido',
        rejectClass: 'hidden',
        accept: () => {}
      });
    }
  } catch {
    // ignore
  }
}

if (reporteId.value) {
  // si llega preseleccionado por query, validar abiertos
  checkOpenTicket();
}
</script>

<style scoped>
.ticket-page { padding: 12px; max-width: 1200px; margin: 0 auto; }
.title { font-size: 1.6rem; font-weight: 800; color: var(--color-title); margin-bottom: 10px; }
.grid { display: grid; grid-template-columns: 1fr 1fr; gap: 16px; }
.col { display: flex; flex-direction: column; }
.p-inputtext, .p-inputtextarea, .p-dropdown { padding: 8px; }
.w-100 { width: 100%; }
.card { background: var(--color-card); border: 1px solid var(--color-border); border-radius: 10px; padding: 12px; }
.section-title { font-weight: 700; color: var(--color-title); margin-bottom: 6px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; margin-top: 6px; }
.chip { background: var(--color-card); border: 1px solid var(--color-border); border-radius: 12px; padding: 2px 8px; font-size: 0.9rem; }
.muted { color: var(--color-border); }
.actions { display: flex; align-items: center; gap: 8px; }
@media (max-width: 900px) { .grid { grid-template-columns: 1fr; } }
</style>
