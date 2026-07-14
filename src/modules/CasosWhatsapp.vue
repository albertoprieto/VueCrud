<template>
  <div class="casos-container">
    <h2 class="casos-title">Casos de WhatsApp — Bot</h2>

    <!-- Resumen por categoría (clickeable, filtra) -->
    <div class="resumen-card">
      <div class="resumen-header">
        <h3>Categorías</h3>
        <span class="resumen-total">{{ casos.length }} caso{{ casos.length === 1 ? '' : 's' }}</span>
      </div>
      <div class="categoria-grid">
        <button
          v-for="cat in CATEGORIAS"
          :key="cat.value"
          type="button"
          class="categoria-card"
          :class="{ activa: filtroCategoria === cat.value }"
          :style="{ '--serie-color': cat.color }"
          @click="toggleCategoria(cat.value)"
        >
          <span class="categoria-nombre"><span class="categoria-dot"></span>{{ cat.label }}</span>
          <span class="categoria-count">{{ contarPorCategoria(cat.value) }}</span>
        </button>
      </div>
    </div>

    <!-- Filtro por estado -->
    <div class="estado-tabs">
      <button
        v-for="est in [{ value: '', label: 'Todos' }, ...ESTADOS]"
        :key="est.value || 'todos'"
        type="button"
        class="estado-tab"
        :class="{ activo: filtroEstado === est.value }"
        @click="filtroEstado = est.value"
      >
        {{ est.label }}
        <span v-if="est.value" class="estado-tab-count">{{ contarPorEstado(est.value) }}</span>
      </button>
    </div>

    <div v-if="loading" style="text-align:center;padding:3rem;">
      <i class="pi pi-spin pi-spinner" style="font-size:2rem;"></i>
    </div>
    <div v-else-if="!casosFiltrados.length" class="casos-empty">
      No hay casos que coincidan con el filtro.
    </div>
    <div v-else class="casos-grid">
      <article
        v-for="caso in casosFiltrados"
        :key="caso.id"
        class="caso-card"
        :style="{ '--serie-color': estadoColor(caso.estado), '--cat-color': categoriaColor(caso.categoria) }"
        @click="abrirDetalle(caso)"
      >
        <header class="caso-header">
          <span class="caso-telefono">{{ caso.nombre_contacto || caso.telefono }}</span>
          <span :class="'badge-estado badge-' + caso.estado">{{ estadoLabel(caso.estado) }}</span>
        </header>
        <div class="caso-categoria">
          <span class="categoria-dot cat"></span>{{ categoriaLabel(caso.categoria) }}
          <span v-if="caso.referencia_tipo" class="referencia-tag">
            {{ REFERENCIA_LABELS[caso.referencia_tipo] || caso.referencia_tipo }}<template v-if="caso.referencia_id"> #{{ caso.referencia_id }}</template>
          </span>
        </div>
        <p class="caso-resumen">{{ caso.resumen || 'Sin mensajes registrados aún.' }}</p>
        <footer class="caso-footer">
          <span>{{ tiempoRelativo(caso.ultima_actividad) }}</span>
          <span v-if="caso.atendido_por" class="caso-atendido"><i class="pi pi-user" /> {{ caso.atendido_por }}</span>
        </footer>
      </article>
    </div>

    <!-- Dialog detalle -->
    <Dialog v-model:visible="detalleVisible" :header="casoActivo ? (casoActivo.nombre_contacto || casoActivo.telefono) : ''" :modal="true" :style="{ width: '600px', maxWidth: '95vw' }" :draggable="false">
      <template v-if="casoActivo">
        <div class="detalle-form">
          <div class="detalle-field">
            <label>Estado</label>
            <Dropdown v-model="casoActivo.estado" :options="ESTADOS" optionLabel="label" optionValue="value" class="w-full" @change="guardarEstado" />
          </div>
          <div class="detalle-field">
            <label>Categoría</label>
            <Dropdown v-model="casoActivo.categoria" :options="CATEGORIAS" optionLabel="label" optionValue="value" class="w-full" @change="guardarCategoria" />
          </div>
          <div class="detalle-field">
            <label>Atendido por</label>
            <div style="display:flex;gap:0.5rem;">
              <InputText v-model="atendidoPorInput" class="w-full" placeholder="Nombre de quien da seguimiento" />
              <Button icon="pi pi-save" class="p-button-sm" @click="guardarAsignado" />
            </div>
          </div>
        </div>

        <h4 style="margin:1.25rem 0 0.5rem;">Conversación</h4>
        <div v-if="loadingDetalle" style="text-align:center;padding:1rem;">
          <i class="pi pi-spin pi-spinner"></i>
        </div>
        <div v-else-if="!casoActivo.mensajes || !casoActivo.mensajes.length" class="sin-mensajes">
          Sin mensajes registrados para este caso.
        </div>
        <div v-else class="mensajes-timeline">
          <div v-for="m in casoActivo.mensajes" :key="m.id" :class="['mensaje-bubble', m.direccion === 'out' ? 'out' : 'in']">
            <div class="mensaje-texto">{{ m.texto }}</div>
            <div class="mensaje-fecha">{{ formatFechaHora(m.fecha) }}</div>
          </div>
        </div>
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import Dialog from 'primevue/dialog';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { useToast } from 'primevue/usetoast';
import {
  getCasos,
  getCasoDetalle,
  actualizarEstadoCaso,
  actualizarCategoriaCaso,
  asignarCaso,
} from '@/services/whatsappCasosService';

const toast = useToast();

const CATEGORIAS = [
  { value: 'tramite',            label: 'Trámite (reporte/nota/factura)', color: '#2a78d6' },
  { value: 'soporte_equipo_app', label: 'Soporte — Equipo y app',        color: '#1baf7a' },
  { value: 'soporte_dudas',      label: 'Soporte — Dudas',                color: '#eda100' },
  { value: 'soporte_accesos',    label: 'Soporte — Accesos',              color: '#4a3aa7' },
  { value: 'otro',               label: 'Otro',                           color: '#898781' },
];

const REFERENCIA_LABELS = { reporte: 'Reporte', nota: 'Nota', factura: 'Factura' };

const ESTADOS = [
  { value: 'abierto',            label: 'Abierto',           color: '#2a78d6' },
  { value: 'en_progreso',        label: 'En progreso',       color: '#fab219' },
  { value: 'esperando_cliente',  label: 'Esperando cliente', color: '#eb6834' },
  { value: 'resuelto',           label: 'Resuelto',          color: '#0ca30c' },
  { value: 'cerrado',            label: 'Cerrado',           color: '#898781' },
];

const loading = ref(true);
const loadingDetalle = ref(false);
const casos = ref([]);
const filtroCategoria = ref('');
const filtroEstado = ref('');
const detalleVisible = ref(false);
const casoActivo = ref(null);
const atendidoPorInput = ref('');

const casosFiltrados = computed(() => {
  return casos.value.filter(c => {
    if (filtroCategoria.value && c.categoria !== filtroCategoria.value) return false;
    if (filtroEstado.value && c.estado !== filtroEstado.value) return false;
    return true;
  });
});

function categoriaColor(valor) {
  return CATEGORIAS.find(c => c.value === valor)?.color || '#898781';
}
function estadoColor(valor) {
  return ESTADOS.find(e => e.value === valor)?.color || '#898781';
}
function categoriaLabel(valor) {
  return CATEGORIAS.find(c => c.value === valor)?.label || valor || '-';
}
function estadoLabel(valor) {
  return ESTADOS.find(e => e.value === valor)?.label || valor || '-';
}
function contarPorCategoria(valor) {
  return casos.value.filter(c => c.categoria === valor).length;
}
function contarPorEstado(valor) {
  return casos.value.filter(c => c.estado === valor).length;
}
function toggleCategoria(valor) {
  filtroCategoria.value = filtroCategoria.value === valor ? '' : valor;
}

function tiempoRelativo(fecha) {
  if (!fecha) return '-';
  const diffMs = Date.now() - new Date(fecha).getTime();
  const min = Math.floor(diffMs / 60000);
  if (min < 1) return 'ahora mismo';
  if (min < 60) return `hace ${min} min`;
  const horas = Math.floor(min / 60);
  if (horas < 24) return `hace ${horas} h`;
  const dias = Math.floor(horas / 24);
  return `hace ${dias} día${dias === 1 ? '' : 's'}`;
}

function formatFechaHora(f) {
  if (!f) return '';
  const d = new Date(f);
  return `${String(d.getDate()).padStart(2, '0')}/${String(d.getMonth() + 1).padStart(2, '0')}/${d.getFullYear()} ${String(d.getHours()).padStart(2, '0')}:${String(d.getMinutes()).padStart(2, '0')}`;
}

async function cargar() {
  loading.value = true;
  try {
    casos.value = await getCasos();
  } catch {
    casos.value = [];
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los casos.', life: 4000 });
  }
  loading.value = false;
}

async function abrirDetalle(caso) {
  detalleVisible.value = true;
  loadingDetalle.value = true;
  casoActivo.value = { ...caso, mensajes: [] };
  atendidoPorInput.value = caso.atendido_por || '';
  try {
    casoActivo.value = await getCasoDetalle(caso.id);
    atendidoPorInput.value = casoActivo.value.atendido_por || '';
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo cargar el detalle del caso.', life: 4000 });
  }
  loadingDetalle.value = false;
}

async function guardarEstado() {
  if (!casoActivo.value) return;
  try {
    await actualizarEstadoCaso(casoActivo.value.id, casoActivo.value.estado);
    const local = casos.value.find(c => c.id === casoActivo.value.id);
    if (local) local.estado = casoActivo.value.estado;
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Estado actualizado.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el estado.', life: 4000 });
  }
}

async function guardarCategoria() {
  if (!casoActivo.value) return;
  try {
    await actualizarCategoriaCaso(casoActivo.value.id, casoActivo.value.categoria);
    const local = casos.value.find(c => c.id === casoActivo.value.id);
    if (local) local.categoria = casoActivo.value.categoria;
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Categoría actualizada.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar la categoría.', life: 4000 });
  }
}

async function guardarAsignado() {
  if (!casoActivo.value) return;
  try {
    await asignarCaso(casoActivo.value.id, atendidoPorInput.value);
    casoActivo.value.atendido_por = atendidoPorInput.value;
    const local = casos.value.find(c => c.id === casoActivo.value.id);
    if (local) local.atendido_por = atendidoPorInput.value;
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Caso asignado.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo asignar el caso.', life: 4000 });
  }
}

onMounted(cargar);
</script>

<style scoped>
.casos-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  max-width: 1200px;
}
.casos-title {
  text-align: center;
  margin-bottom: 1.5rem;
  color: var(--color-title);
}
.resumen-card {
  padding: 1.25rem 1.5rem;
  margin-bottom: 1.25rem;
  border-radius: 14px;
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-1, 0 1px 4px rgba(0, 0, 0, 0.05));
}
.resumen-header {
  display: flex;
  align-items: baseline;
  justify-content: space-between;
  margin-bottom: 1rem;
}
.resumen-header h3 {
  margin: 0;
  font-size: 0.85rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: var(--color-text);
  opacity: 0.7;
}
.resumen-total {
  font-weight: 700;
  color: var(--color-title);
}
.categoria-grid {
  display: flex;
  flex-wrap: wrap;
  gap: 0.75rem;
}
.categoria-card {
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
  padding: 0.65rem 1rem;
  border-radius: 10px;
  border: 1px solid var(--color-border);
  border-top: 3px solid color-mix(in srgb, var(--serie-color) 65%, transparent);
  background: var(--color-card);
  cursor: pointer;
  min-width: 130px;
  transition: box-shadow 0.15s, transform 0.15s;
}
.categoria-card:hover { transform: translateY(-2px); box-shadow: var(--shadow-1, 0 2px 8px rgba(0,0,0,0.08)); }
.categoria-card.activa {
  border-top-color: var(--serie-color);
  box-shadow: 0 0 0 2px color-mix(in srgb, var(--serie-color) 30%, transparent);
}
.categoria-nombre {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.78rem;
  font-weight: 700;
  text-transform: uppercase;
  color: var(--color-text);
  opacity: 0.8;
}
.categoria-dot {
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--serie-color);
  flex-shrink: 0;
}
.categoria-dot.cat {
  background: var(--cat-color, var(--serie-color));
}
.categoria-count {
  font-size: 1.3rem;
  font-weight: 800;
  color: var(--color-title);
}
.estado-tabs {
  display: flex;
  gap: 0.5rem;
  flex-wrap: wrap;
  margin-bottom: 1.25rem;
}
.estado-tab {
  padding: 0.5rem 1rem;
  border-radius: 999px;
  border: 1px solid var(--color-border);
  background: var(--color-card);
  color: var(--color-text);
  cursor: pointer;
  font-size: 0.85rem;
  font-weight: 600;
}
.estado-tab.activo {
  background: var(--color-title);
  color: var(--color-bg);
  border-color: var(--color-title);
}
.estado-tab-count {
  margin-left: 0.35rem;
  opacity: 0.7;
}
.casos-empty {
  text-align: center;
  color: var(--color-text);
  opacity: 0.7;
  padding: 3rem;
}
.casos-grid {
  display: grid;
  grid-template-columns: repeat(auto-fill, minmax(260px, 1fr));
  gap: 1rem;
}
.caso-card {
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
  padding: 1rem 1.15rem;
  border-radius: 12px;
  border: 1px solid color-mix(in srgb, var(--serie-color) 35%, var(--color-border));
  border-left: 5px solid var(--serie-color);
  background: color-mix(in srgb, var(--serie-color) 5%, var(--color-card));
  cursor: pointer;
  box-shadow: var(--shadow-1, 0 1px 3px rgba(0, 0, 0, 0.05));
  transition: transform 0.15s, box-shadow 0.15s;
}
.caso-card:hover {
  transform: translateY(-3px);
  box-shadow: var(--shadow-2, 0 8px 20px rgba(0, 0, 0, 0.09));
}
.caso-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.5rem;
}
.caso-telefono {
  font-weight: 700;
  color: var(--color-title);
}
.caso-categoria {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.76rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text);
  opacity: 0.7;
}
.referencia-tag {
  margin-left: 0.15rem;
  padding: 0.1rem 0.5rem;
  border-radius: 999px;
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
  font-weight: 700;
  opacity: 1;
}
.caso-resumen {
  margin: 0;
  font-size: 0.85rem;
  color: var(--color-text);
  display: -webkit-box;
  -webkit-line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}
.caso-footer {
  display: flex;
  justify-content: space-between;
  font-size: 0.75rem;
  color: var(--color-text);
  opacity: 0.65;
}
.caso-atendido {
  display: flex;
  align-items: center;
  gap: 0.25rem;
}
.badge-estado {
  padding: 0.2rem 0.6rem;
  border-radius: 999px;
  font-size: 0.72rem;
  font-weight: 700;
  white-space: nowrap;
}
.badge-abierto { background: color-mix(in srgb, var(--color-primary) 20%, transparent); color: var(--color-primary); }
.badge-en_progreso { background: color-mix(in srgb, var(--color-warning) 25%, transparent); color: var(--color-warning); }
.badge-esperando_cliente { background: color-mix(in srgb, #eb6834 22%, transparent); color: #eb6834; }
.badge-resuelto { background: color-mix(in srgb, var(--color-success) 22%, transparent); color: var(--color-success); }
.badge-cerrado { background: color-mix(in srgb, var(--color-muted-bg, #898781) 30%, transparent); color: var(--color-text); }

.detalle-form {
  display: flex;
  flex-direction: column;
  gap: 0.9rem;
}
.detalle-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.3rem;
  font-size: 0.85rem;
}
.sin-mensajes {
  color: var(--color-text);
  opacity: 0.6;
  text-align: center;
  padding: 1rem;
}
.mensajes-timeline {
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
  max-height: 320px;
  overflow-y: auto;
  padding: 0.25rem;
}
.mensaje-bubble {
  max-width: 75%;
  padding: 0.5rem 0.75rem;
  border-radius: 12px;
  font-size: 0.85rem;
}
.mensaje-bubble.in {
  align-self: flex-start;
  background: var(--color-bg-light);
  border: 1px solid var(--color-border);
}
.mensaje-bubble.out {
  align-self: flex-end;
  background: color-mix(in srgb, var(--color-primary) 18%, transparent);
}
.mensaje-texto {
  white-space: pre-wrap;
  word-break: break-word;
}
.mensaje-fecha {
  margin-top: 0.25rem;
  font-size: 0.68rem;
  opacity: 0.6;
}
.w-full { width: 100%; }
</style>
