<template>
  <div class="ticket-page" v-if="ticket">
    <div class="ticket-card">
      <div class="ticket-header">
        <div class="ticket-title">
          Ticket #{{ ticket.id }}
          <span class="muted">· Reporte #{{ ticket.reporteId }}</span>
        </div>
        <div class="ticket-badges">
          <span :class="['badge','badge-state', `state-${estado}`]">{{ estado.replace('_',' ') }}</span>
          <span :class="['badge','badge-prio', `prio-${ticket.prioridad}`]">{{ ticket.prioridad }}</span>
          <span class="badge">{{ ticket.tipo }}</span>
        </div>
      </div>

      <div class="ticket-grid">
        <div class="card-section">
          <div class="field-row"><label>ID</label><div class="value">{{ ticket.id }}</div></div>
          <div class="field-row"><label>Título</label><div class="value">{{ ticket.titulo }}</div></div>
          <div class="field-row"><label>Descripción</label><div class="value">{{ ticket.descripcion }}</div></div>
          <div class="field-row"><label>Prioridad</label><div class="value">{{ ticket.prioridad }}</div></div>
          <div class="field-row"><label>Tipo</label><div class="value">{{ ticket.tipo }}</div></div>
          <div class="field-row"><label>Estado</label><div class="value">{{ ticket.estado }}</div></div>
          <div class="field-row"><label>Cliente</label><div class="value">{{ ticket.cliente || '-' }}</div></div>
          <div class="field-row"><label>Teléfono</label><div class="value">{{ ticket.telefono || '-' }}</div></div>
          <div class="field-row"><label>Usuario plataforma</label><div class="value">{{ ticket.usuario_plataforma || '-' }}</div></div>
          <div class="field-row"><label>Autor</label><div class="value">{{ ticket.autor || '-' }}</div></div>
          <div class="field-row"><label>ID usuario creador</label><div class="value">{{ ticket.created_by_user_id || '-' }}</div></div>
          <div class="field-row"><label>Creado</label><div class="value">{{ (ticket.created_at || '').replace('T',' ').slice(0,19) }}</div></div>
          <div class="field-row"><label>Actualizado</label><div class="value">{{ (ticket.updated_at || '').replace('T',' ').slice(0,19) }}</div></div>
        </div>

        <div class="card-section">
          <div class="section-title">IMEIs</div>
          <div class="chips">
            <span v-for="i in ticket.imeis || []" :key="i" class="chip">{{ i }}</span>
            <span v-if="!ticket.imeis?.length" class="muted">(sin IMEIs)</span>
          </div>
        </div>
      </div>
    </div>

    <div class="ticket-card">
      <div class="section-title">Comentarios</div>
      <div class="comments">
        <div v-for="c in ticket.comentarios || []" :key="c.id" class="comment">
          <div class="when">{{ (c.created_at || c.createdAt || '').replace('T',' ').slice(0,19) }}</div>
          <div class="text">{{ c.text }}</div>
          <div class="usuario muted">por {{ c.usuario || '-' }}</div>
        </div>
        <div v-if="!(ticket.comentarios && ticket.comentarios.length)" class="muted">Sin comentarios.</div>
      </div>
      <form class="comment-form" @submit.prevent="sendComment">
        <input v-model="comment" class="input" placeholder="Escribe un comentario"/>
        <button class="p-button p-button-sm" type="submit">Enviar</button>
      </form>
    </div>

    <div class="actions">
      <router-link to="/tickets" class="p-button p-button-text p-button-sm">Volver</router-link>
    </div>
    <Toast/>
    <ConfirmDialog/>
  </div>
  <Loader v-else/>
  
</template>

<script setup>
import { ref, onMounted, watch } from 'vue';
import { useRoute } from 'vue-router';
import { useTicketsStore } from '@/stores/ticketsStore';
import Loader from '@/components/Loader.vue';
import { useToast } from 'primevue/usetoast';
import { useConfirm } from 'primevue/useconfirm';
import Dropdown from 'primevue/dropdown';
import { useLoginStore } from '@/stores/loginStore';

const route = useRoute();
const store = useTicketsStore();
const toast = useToast();
const confirm = useConfirm();
const ticket = ref(null);
const comment = ref('');
const estado = ref('nuevo');
const estadoOptions = [
  { label: 'nuevo', value: 'nuevo' },
  { label: 'en_progreso', value: 'en_progreso' },
  { label: 'en_espera', value: 'en_espera' },
  { label: 'resuelto', value: 'resuelto' },
  { label: 'cerrado', value: 'cerrado' }
];
const ctxDetail = ref(null);

async function load() {
  const id = route.params.id;
  const t = await store.fetchOne(id);
  ticket.value = t;
  estado.value = t?.estado || 'nuevo';
  if (t?.reporteId) {
    try {
      const ctx = await store.getContext(t.reporteId);
      ctxDetail.value = ctx || null;
      console.log('[TicketDetail] contexto reporte', ctx);
    } catch (e) {
      ctxDetail.value = null;
    }
  }
}

onMounted(load);
watch(() => route.params.id, load);

async function sendComment() {
  const txt = (comment.value || '').trim();
  if (!txt) return;
  const loginStore = useLoginStore();
  const usuario = loginStore.user?.username;
  if (!usuario) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No hay usuario firmado. No se puede comentar.', life: 3000 });
    return;
  }
  try {
    // Llamar el servicio directamente, sin store
    const { addComment } = await import('@/services/ticketsService');
    await addComment(ticket.value.id, { comment: txt, usuario });
    comment.value = '';
    toast.add({ severity: 'success', summary: 'Comentario agregado', life: 2200 });
    await load();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo agregar el comentario', life: 3000 });
  }
}

function onEstadoChange(e) {
  if (!ticket.value) return;
  const nuevo = e?.value ?? estado.value;
  const previo = ticket.value.estado;
  const doPatch = async () => {
    try {
      await store.patch(ticket.value.id, { estado: nuevo });
      ticket.value.estado = nuevo;
      toast.add({ severity: 'success', summary: 'Estado actualizado', detail: `Ahora: ${nuevo.replace('_',' ')}`, life: 2200 });
    } catch (e) {
      estado.value = previo;
      toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el estado', life: 3000 });
    }
  };

  if (nuevo === 'cerrado') {
    confirm.require({
      message: '¿Seguro que deseas cerrar este ticket? Ya no podrá editarse.',
      header: 'Cerrar ticket',
      icon: 'pi pi-exclamation-triangle',
      acceptLabel: 'Cerrar',
      rejectLabel: 'Cancelar',
      accept: doPatch,
      reject: () => { estado.value = previo; }
    });
  } else {
    doPatch();
  }
}
</script>

<style scoped>
.ticket-page { padding: 12px; max-width: 1000px; margin: 0 auto; }
.ticket-card {
  background: var(--color-card);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  border-radius: 14px;
  padding: 16px;
  box-shadow: 0 2px 10px rgba(0,0,0,0.06);
  margin-bottom: 16px;
}
.ticket-header { display: flex; flex-wrap: wrap; align-items: center; justify-content: space-between; gap: 10px; }
.ticket-title { font-size: 1.4rem; font-weight: 800; color: var(--color-title); }
.ticket-badges { display: flex; gap: 8px; flex-wrap: wrap; }
.badge { display: inline-block; padding: 4px 10px; border-radius: 999px; font-size: 0.8rem; border: 1px solid var(--color-border); background: var(--color-bg); }
.badge-state.state-nuevo { background: #e3f2fd; color: #0d47a1; border-color: #bbdefb; }
.badge-state.state-en_progreso { background: #fff3e0; color: #e65100; border-color: #ffe0b2; }
.badge-state.state-en_espera { background: #f3e5f5; color: #6a1b9a; border-color: #e1bee7; }
.badge-state.state-resuelto { background: #e8f5e9; color: #1b5e20; border-color: #c8e6c9; }
.badge-state.state-cerrado { background: #eceff1; color: #37474f; border-color: #cfd8dc; }
.badge-prio.prio-baja { background: #e0f2f1; color: #004d40; border-color: #b2dfdb; }
.badge-prio.prio-media { background: #ede7f6; color: #4527a0; border-color: #d1c4e9; }
.badge-prio.prio-alta { background: #ffebee; color: #b71c1c; border-color: #ffcdd2; }
.badge-prio.prio-crítica { background: #ffeb3b; color: #212121; border-color: #fdd835; }

.ticket-grid { display: grid; grid-template-columns: 1fr; gap: 16px; margin-top: 12px; }
@media (min-width: 900px) { .ticket-grid { grid-template-columns: 1fr 1fr; } }
.card-section { background: var(--color-bg); border: 1px solid var(--color-border); border-radius: 10px; padding: 12px; }
.section-title { font-weight: 700; color: var(--color-title); margin-bottom: 8px; }
.field-row { display: grid; grid-template-columns: 140px 1fr; gap: 10px; align-items: center; padding: 6px 0; }
.field-row label { font-weight: 600; color: var(--color-title); }
.value { word-break: break-word; }
.select { width: 100%; max-width: 260px; }
.chips { display: flex; flex-wrap: wrap; gap: 6px; }
.chip { background: var(--color-card); border: 1px solid var(--color-border); border-radius: 12px; padding: 4px 10px; font-size: 0.9rem; }
.comments { display: flex; flex-direction: column; gap: 10px; }
.comment { background: var(--color-bg); border: 1px solid var(--color-border); border-radius: 10px; padding: 10px 12px; }
.comment .when { font-size: 0.85rem; color: var(--color-border); margin-bottom: 4px; }
.comment-form { display: flex; gap: 8px; margin-top: 10px; flex-wrap: wrap; }
.comment-form .input { flex: 1 1 280px; padding: 10px 12px; border-radius: 8px; border: 1px solid var(--color-border); background: var(--color-card); color: var(--color-text); }
.actions { display: flex; justify-content: flex-end; margin-top: 8px; }
.muted { color: var(--color-border); }
</style>
