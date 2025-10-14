<template>
  <div class="ticket-page">
    <h2 class="title">Nuevo Ticket</h2>
    <form @submit.prevent="submit">
      <div class="grid">
        <div class="col">
          <label>Cliente</label>
          <input v-model="cliente" type="text" class="p-inputtext" placeholder="Nombre del cliente (opcional)" />
        </div>
        <div class="col">
          <label>Teléfono de contacto</label>
          <input v-model="telefono" type="text" required class="p-inputtext" placeholder="Teléfono de contacto" />
        </div>
      </div>
      <div class="grid">
        <div class="col">
          <label>Usuario Plataforma</label>
          <input v-model="usuarioPlataforma" type="text" required class="p-inputtext" placeholder="Usuario plataforma" />
        </div>
        <div class="col">
          <label>IMEIs asociados</label>
          <textarea v-model="imeisManual" class="p-inputtextarea" rows="2" required placeholder="Captura los IMEIs separados por coma o salto de línea" />
        </div>
      </div>
      <div class="grid">
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

      <!-- <div class="mt-2 card">
        <div class="section-title">IMEIs del reporte</div>
        <div class="chips">
          <span v-for="i in imeis" :key="i" class="chip">{{ i }}</span>
          <span v-if="!imeis.length" class="muted">(sin IMEIs en contexto)</span>
        </div>
      </div> -->

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
const cliente = ref('');
const telefono = ref('');
const usuarioPlataforma = ref('');
const imeisManual = ref('');
import { ref } from 'vue';
import { useRouter, useRoute } from 'vue-router';
import { createTicket, getTickets, addComment } from '@/services/ticketsService';
import AutoComplete from 'primevue/autocomplete';
import { getReportesServicioTodos } from '@/services/reportesService';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Dropdown from 'primevue/dropdown';
import { useLoginStore } from '@/stores/loginStore';
import { getTickets as apiGetTickets } from '@/services/ticketsService';

const router = useRouter();
const route = useRoute();
// Eliminado: store, ahora se usa API directa
const toast = useToast();
const confirm = useConfirm();
const login = useLoginStore();
const tipoOptions = [
  { label: 'Soporte', value: 'soporte' },
  { label: 'Garantía', value: 'garantía' },
  { label: 'Posventa', value: 'posventa' },
  { label: 'Otro', value: 'otro' },
];
const reporteId = ref(Number(route.query.reporteId) || undefined);
const selectedReporte = ref(null);
const reporteOptions = ref([]);
const ctx = ref(null);
const imeis = ref([]);

const titulo = ref('');
const descripcion = ref('');
const prioridad = ref('baja');
const tipo = ref('soporte');
const autor = ref(login?.user?.username || login?.user?.nombre || login?.user?.email || '');
const prioridadOptions = [
  { label: 'Baja', value: 'baja' },
  { label: 'Media', value: 'media' },
  { label: 'Alta', value: 'alta' },
  { label: 'Crítica', value: 'crítica' }
];
function submit() {
  // ...validaciones y confirm.require...
  // Validar campos obligatorios
  if (!telefono.value) {
    toast.add({ severity: 'warn', summary: 'Falta teléfono', detail: 'El teléfono de contacto es obligatorio', life: 2500 });
    return;
  }
  if (!usuarioPlataforma.value) {
    toast.add({ severity: 'warn', summary: 'Falta usuario plataforma', detail: 'El usuario plataforma es obligatorio', life: 2500 });
    return;
  }
  if (!descripcion.value) {
    toast.add({ severity: 'warn', summary: 'Falta descripción', detail: 'La descripción del problema es obligatoria', life: 2500 });
    return;
  }
  // Validar IMEIs
  const imeisArray = imeisManual.value.split(/[,\n]+/).map(i => i.trim()).filter(Boolean);
  if (!imeisArray.length) {
    toast.add({ severity: 'warn', summary: 'Faltan IMEIs', detail: 'Debes capturar al menos un IMEI', life: 2500 });
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
          cliente: cliente.value,
          telefono: telefono.value,
          usuario_plataforma: usuarioPlataforma.value,
          titulo: titulo.value,
          descripcion: descripcion.value,
          prioridad: prioridad.value,
          tipo: tipo.value,
          imeis: imeisArray,
          autor: autor.value,
          created_by_user_id: login?.user?.id,
        };
        const t = await createTicket(payload);
        toast.add({ severity: 'success', summary: 'Ticket creado', detail: `Ticket #${t.id}`, life: 2500 });
        // router.push(`/tickets/${t.id}`);
// Ejemplo de función para agregar comentario con usuario
async function comentarTicket(ticketId, textoComentario) {
  const usuarioActual = login?.user?.username || '';
  await addComment(ticketId, { comment: textoComentario, usuario: usuarioActual });
}
      } catch (err) {
        toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo crear el ticket', life: 3000 });
      }
    }
  });
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
