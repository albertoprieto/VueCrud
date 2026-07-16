<template>
  <div class="wa-shell">
    <!-- ═══════ Rail de iconos, como WhatsApp Web ═══════ -->
    <aside v-if="!isMobile" class="wa-icon-rail">
      <span class="wa-rail-icon activo"><i class="pi pi-comments" /></span>
      <span class="wa-rail-spacer"></span>
      <span class="wa-rail-icon"><i class="pi pi-user" /></span>
    </aside>

    <!-- ═══════ Sidebar: lista de chats ═══════ -->
    <aside class="wa-sidebar" :class="{ 'wa-sidebar-oculto': isMobile && casoActivo }">
      <header class="wa-sidebar-header">
        <h1 class="wa-wordmark">Soporte IA</h1>
        <span class="wa-sidebar-count">{{ casosFiltrados.length }} de {{ casos.length }} casos</span>
      </header>

      <div class="wa-search">
        <i class="pi pi-search" />
        <input v-model="filtroTexto" type="text" placeholder="Buscar por nombre o teléfono..." />
      </div>

      <div class="wa-filter-row">
        <button
          v-for="cat in [{ value: '', short: 'Todos', color: null }, ...CATEGORIAS]"
          :key="'cat-' + (cat.value || 'todos')"
          type="button"
          class="wa-filter-chip"
          :class="{ activo: filtroCategoria === cat.value }"
          :style="cat.color ? { '--chip-color': cat.color } : {}"
          :title="cat.label"
          @click="toggleCategoria(cat.value)"
        >
          <span v-if="cat.color" class="wa-filter-dot"></span>{{ cat.short }}
          <span class="wa-filter-count">{{ cat.value ? contarPorCategoria(cat.value) : casos.length }}</span>
        </button>
      </div>
      <div class="wa-filter-row wa-filter-row-estado">
        <button
          v-for="est in [{ value: '', short: 'Todos' }, ...ESTADOS]"
          :key="'est-' + (est.value || 'todos')"
          type="button"
          class="wa-filter-chip wa-filter-chip-sm"
          :class="{ activo: filtroEstado === est.value }"
          :style="est.color ? { '--chip-color': est.color } : {}"
          :title="est.label"
          @click="filtroEstado = filtroEstado === est.value ? '' : est.value"
        >
          {{ est.short }}
        </button>
      </div>

      <div v-if="loading" class="wa-list-loading">
        <i class="pi pi-spin pi-spinner" />
      </div>
      <div v-else-if="!contactos.length" class="wa-list-empty">
        Sin casos que coincidan.
      </div>
      <ul v-else class="wa-chat-list">
        <li v-for="contacto in contactos" :key="contacto.telefono" class="wa-contacto">
          <div
            class="wa-chat-item"
            :class="{ activo: casoActivo && casoActivo.id === contacto.vigente.id, urgente: esUrgenteSinAsignar(contacto.vigente) }"
            @click="abrirDetalle(contacto.vigente)"
          >
            <span class="wa-avatar" :style="{ '--serie-color': estadoColor(contacto.vigente.estado) }">
              <img :src="getAvatarDataUri(contacto.telefono)" alt="" />
              <span v-if="esUrgenteSinAsignar(contacto.vigente)" class="wa-avatar-alert"><i class="pi pi-exclamation-triangle" /></span>
            </span>
            <div class="wa-chat-info">
              <div class="wa-chat-row1">
                <span class="wa-chat-nombre">{{ contacto.nombre_contacto || contacto.telefono }}</span>
                <span class="wa-chat-tiempo">{{ tiempoRelativo(contacto.vigente.ultima_actividad) }}</span>
              </div>
              <div class="wa-chat-row2">
                <span class="wa-chat-preview">{{ contacto.vigente.resumen || 'Sin mensajes registrados aún.' }}</span>
                <span class="wa-chat-dot cat" :style="{ '--cat-color': categoriaColor(contacto.vigente.categoria) }"></span>
              </div>
              <div class="wa-chat-row3">
                <span :class="'badge-estado badge-' + contacto.vigente.estado">{{ estadoLabel(contacto.vigente.estado) }}</span>
                <span class="wa-chat-categoria">{{ categoriaLabel(contacto.vigente.categoria) }}</span>
                <span v-if="contacto.vigente.referencia_tipo" class="referencia-tag">
                  {{ REFERENCIA_LABELS[contacto.vigente.referencia_tipo] || contacto.vigente.referencia_tipo }}<template v-if="contacto.vigente.referencia_id"> #{{ contacto.vigente.referencia_id }}</template>
                </span>
              </div>
            </div>
          </div>

          <button
            v-if="contacto.historial.length"
            type="button"
            class="wa-historial-toggle"
            @click.stop="toggleHistorial(contacto.telefono)"
          >
            <i :class="['pi', expandidos.has(contacto.telefono) ? 'pi-chevron-up' : 'pi-chevron-down']" />
            {{ contacto.historial.length }} caso{{ contacto.historial.length === 1 ? '' : 's' }} anterior{{ contacto.historial.length === 1 ? '' : 'es' }}
          </button>

          <ul v-if="expandidos.has(contacto.telefono)" class="wa-historial-list">
            <li
              v-for="caso in contacto.historial"
              :key="caso.id"
              class="wa-historial-item"
              :class="{ activo: casoActivo && casoActivo.id === caso.id }"
              @click.stop="abrirDetalle(caso)"
            >
              <span :class="'badge-estado badge-' + caso.estado">{{ estadoLabel(caso.estado) }}</span>
              <span class="wa-historial-fecha">{{ tiempoRelativo(caso.ultima_actividad) }}</span>
              <span class="wa-historial-preview">{{ caso.resumen || '-' }}</span>
            </li>
          </ul>
        </li>
      </ul>
    </aside>

    <!-- ═══════ Panel: conversación ═══════ -->
    <section class="wa-panel" :class="{ 'wa-panel-oculto': isMobile && !casoActivo }">
      <div v-if="!casoActivo" class="wa-panel-empty">
        <i class="pi pi-whatsapp" />
        <h2>Soporte IA — GPS Ubicación</h2>
        <p>Selecciona una conversación de la izquierda para ver el detalle y darle seguimiento.</p>
      </div>

      <template v-else>
        <header class="wa-panel-header">
          <button v-if="isMobile" class="wa-back-btn" @click="casoActivo = null"><i class="pi pi-arrow-left" /></button>
          <span class="wa-avatar wa-avatar-lg" :style="{ '--serie-color': estadoColor(casoActivo.estado) }">
            <img :src="getAvatarDataUri(casoActivo.telefono)" alt="" />
          </span>
          <div class="wa-panel-identidad" @click="isMobile && (infoMobileAbierta = !infoMobileAbierta)">
            <span class="wa-panel-nombre">{{ casoActivo.nombre_contacto || casoActivo.telefono }}</span>
            <span class="wa-panel-telefono">{{ casoActivo.telefono }}</span>
          </div>
          <span v-if="!isMobile" :class="'badge-estado badge-' + casoActivo.estado">{{ estadoLabel(casoActivo.estado) }}</span>
          <button v-if="isMobile" class="wa-info-btn" @click="infoMobileAbierta = !infoMobileAbierta">
            <i :class="['pi', infoMobileAbierta ? 'pi-chevron-up' : 'pi-info-circle']" />
          </button>
        </header>

        <div v-if="esUrgenteSinAsignar(casoActivo)" class="wa-panel-alerta">
          <i class="pi pi-exclamation-triangle" /> Este caso fue escalado y todavía no tiene a nadie asignado.
        </div>

        <div v-if="casoActivo.diagnostico" class="wa-diagnostico">
          <div class="wa-diagnostico-titulo"><i class="pi pi-clipboard" /> Diagnóstico del bot</div>
          <pre class="wa-diagnostico-texto">{{ casoActivo.diagnostico }}</pre>
        </div>

        <div v-if="casoActivo.intervencion_humana" class="wa-intervencion-banner">
          <span><i class="pi pi-user-edit" /> Estás respondiendo tú — la IA está en pausa para este caso.</span>
          <Button label="Reactivar IA" icon="pi pi-android" class="p-button-sm p-button-outlined" @click="reactivarIaCaso" />
        </div>

        <div v-if="!isMobile || infoMobileAbierta" class="wa-panel-controles">
          <div class="wa-control-field wa-control-field-contacto">
            <label>Nombre del contacto</label>
            <div class="wa-asignado-row">
              <InputText v-model="nombreContactoInput" class="w-full" placeholder="Nombre para identificar este número" />
              <Button icon="pi pi-save" class="p-button-sm" @click="guardarNombreContacto" />
            </div>
          </div>
          <div class="wa-control-field wa-control-field-numero">
            <label>Número</label>
            <InputText :model-value="casoActivo.telefono" class="w-full" disabled />
          </div>
          <div class="wa-control-field">
            <label>Estado</label>
            <Dropdown v-model="casoActivo.estado" :options="ESTADOS" optionLabel="label" optionValue="value" class="w-full" @change="guardarEstado" />
          </div>
          <div class="wa-control-field">
            <label>Categoría</label>
            <Dropdown v-model="casoActivo.categoria" :options="CATEGORIAS" optionLabel="label" optionValue="value" class="w-full" @change="guardarCategoria" />
          </div>
          <div class="wa-control-field wa-control-field-asignado">
            <label>Atendido por</label>
            <div class="wa-asignado-row">
              <InputText v-model="atendidoPorInput" class="w-full" placeholder="Nombre de quien da seguimiento" />
              <Button icon="pi pi-save" class="p-button-sm" @click="guardarAsignado" />
            </div>
          </div>
        </div>

        <div class="wa-panel-messages">
          <div v-if="loadingDetalle" class="wa-list-loading"><i class="pi pi-spin pi-spinner" /></div>
          <div v-else-if="!casoActivo.mensajes || !casoActivo.mensajes.length" class="wa-list-empty">
            Sin mensajes registrados para este caso.
          </div>
          <template v-else>
            <div v-for="m in casoActivo.mensajes" :key="m.id" :class="['mensaje-bubble', m.direccion === 'out' ? 'out' : 'in']">
              <div v-if="m.autor === 'humano'" class="mensaje-autor">Tú</div>
              <a v-if="m.media_url" :href="m.media_url" target="_blank" rel="noopener noreferrer" class="mensaje-imagen-link">
                <img :src="m.media_url" alt="Imagen enviada" class="mensaje-imagen" />
              </a>
              <div v-if="m.texto" class="mensaje-texto">{{ m.texto }}</div>
              <div class="mensaje-fecha">{{ formatFechaHora(m.fecha) }}</div>
            </div>
          </template>
        </div>

        <div class="wa-compose">
          <InputText
            v-model="mensajeManualInput"
            class="w-full"
            placeholder="Escribe una respuesta como tú, no como el bot..."
            @keyup.enter="enviarMensajeManual"
          />
          <Button icon="pi pi-send" :loading="enviandoManual" :disabled="!mensajeManualInput.trim()" @click="enviarMensajeManual" />
        </div>
      </template>
    </section>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onBeforeUnmount } from 'vue';
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
  renombrarContacto,
  responderComoHumano,
  reactivarIA,
} from '@/services/whatsappCasosService';
import { getAvatarDataUri } from '@/services/avatarService';

const toast = useToast();

const CATEGORIAS = [
  { value: 'tramite',            label: 'Trámite (reporte/nota/factura)', short: 'Trámite',    color: '#2a78d6' },
  { value: 'soporte_equipo_app', label: 'Soporte — Equipo y app',        short: 'Equipo/App', color: '#1baf7a' },
  { value: 'soporte_dudas',      label: 'Soporte — Dudas',                short: 'Dudas',      color: '#eda100' },
  { value: 'soporte_accesos',    label: 'Soporte — Accesos',              short: 'Accesos',    color: '#4a3aa7' },
  { value: 'otro',               label: 'Otro',                           short: 'Otro',       color: '#898781' },
];

const REFERENCIA_LABELS = { reporte: 'Reporte', nota: 'Nota', factura: 'Factura' };

const ESTADOS = [
  { value: 'abierto',            label: 'Abierto',           short: 'Abierto',   color: '#2a78d6' },
  { value: 'en_progreso',        label: 'En progreso',       short: 'Progreso',  color: '#fab219' },
  { value: 'esperando_cliente',  label: 'Esperando cliente', short: 'Esperando', color: '#eb6834' },
  { value: 'escalado',           label: 'Escalado',          short: 'Escalado',  color: '#d03b3b' },
  { value: 'resuelto',           label: 'Resuelto',          short: 'Resuelto',  color: '#0ca30c' },
  { value: 'cerrado',            label: 'Cerrado',           short: 'Cerrado',   color: '#898781' },
];

const loading = ref(true);
const loadingDetalle = ref(false);
const casos = ref([]);
const filtroCategoria = ref('');
const filtroEstado = ref('');
const filtroTexto = ref('');
const casoActivo = ref(null);
const atendidoPorInput = ref('');
const nombreContactoInput = ref('');
const mensajeManualInput = ref('');
const enviandoManual = ref(false);
const isMobile = ref(false);
const infoMobileAbierta = ref(false);

function setViewportMode() {
  isMobile.value = window.innerWidth <= 860;
}

const casosFiltrados = computed(() => {
  const texto = filtroTexto.value.trim().toLowerCase();
  return casos.value.filter(c => {
    if (filtroCategoria.value && c.categoria !== filtroCategoria.value) return false;
    if (filtroEstado.value && c.estado !== filtroEstado.value) return false;
    if (texto) {
      const enNombre = (c.nombre_contacto || '').toLowerCase().includes(texto);
      const enTelefono = (c.telefono || '').toLowerCase().includes(texto);
      if (!enNombre && !enTelefono) return false;
    }
    return true;
  });
});

// Agrupa por teléfono (un "contacto" = un hilo). El caso vigente es el más
// reciente que no esté cerrado; si todos están cerrados, el más reciente a secas.
const contactos = computed(() => {
  const grupos = new Map();
  for (const c of casosFiltrados.value) {
    if (!grupos.has(c.telefono)) grupos.set(c.telefono, []);
    grupos.get(c.telefono).push(c);
  }
  const lista = [];
  for (const [telefono, casosDelNumero] of grupos) {
    const ordenados = [...casosDelNumero].sort((a, b) => new Date(b.ultima_actividad) - new Date(a.ultima_actividad));
    const vigente = ordenados.find(c => c.estado !== 'cerrado') || ordenados[0];
    const historial = ordenados.filter(c => c.id !== vigente.id);
    lista.push({ telefono, nombre_contacto: vigente.nombre_contacto, vigente, historial });
  }
  return lista.sort((a, b) => new Date(b.vigente.ultima_actividad) - new Date(a.vigente.ultima_actividad));
});

const expandidos = ref(new Set());
function toggleHistorial(telefono) {
  const nuevo = new Set(expandidos.value);
  if (nuevo.has(telefono)) nuevo.delete(telefono);
  else nuevo.add(telefono);
  expandidos.value = nuevo;
}

function categoriaColor(valor) {
  return CATEGORIAS.find(c => c.value === valor)?.color || '#898781';
}
function estadoColor(valor) {
  return ESTADOS.find(e => e.value === valor)?.color || '#898781';
}
function esUrgenteSinAsignar(caso) {
  return caso.estado === 'escalado' && !caso.atendido_por;
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
  if (min < 1) return 'ahora';
  if (min < 60) return `${min} min`;
  const horas = Math.floor(min / 60);
  if (horas < 24) return `${horas} h`;
  const dias = Math.floor(horas / 24);
  return `${dias} d`;
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
  loadingDetalle.value = true;
  infoMobileAbierta.value = false;
  casoActivo.value = { ...caso, mensajes: [] };
  atendidoPorInput.value = caso.atendido_por || '';
  nombreContactoInput.value = caso.nombre_contacto || '';
  try {
    casoActivo.value = await getCasoDetalle(caso.id);
    atendidoPorInput.value = casoActivo.value.atendido_por || '';
    nombreContactoInput.value = casoActivo.value.nombre_contacto || '';
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

async function guardarNombreContacto() {
  if (!casoActivo.value) return;
  try {
    await renombrarContacto(casoActivo.value.id, nombreContactoInput.value);
    casoActivo.value.nombre_contacto = nombreContactoInput.value;
    for (const c of casos.value) {
      if (c.telefono === casoActivo.value.telefono) c.nombre_contacto = nombreContactoInput.value;
    }
    toast.add({ severity: 'success', summary: 'Guardado', detail: 'Contacto guardado.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo guardar el nombre del contacto.', life: 4000 });
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

async function enviarMensajeManual() {
  const texto = mensajeManualInput.value.trim();
  if (!texto || !casoActivo.value) return;
  enviandoManual.value = true;
  try {
    await responderComoHumano(casoActivo.value.id, texto);
    casoActivo.value.mensajes = casoActivo.value.mensajes || [];
    casoActivo.value.mensajes.push({
      id: `local-${Date.now()}`,
      direccion: 'out',
      autor: 'humano',
      texto,
      fecha: new Date().toISOString(),
    });
    casoActivo.value.intervencion_humana = true;
    const local = casos.value.find(c => c.id === casoActivo.value.id);
    if (local) local.intervencion_humana = true;
    mensajeManualInput.value = '';
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo enviar el mensaje.', life: 4500 });
  }
  enviandoManual.value = false;
}

async function reactivarIaCaso() {
  if (!casoActivo.value) return;
  try {
    await reactivarIA(casoActivo.value.id);
    casoActivo.value.intervencion_humana = false;
    const local = casos.value.find(c => c.id === casoActivo.value.id);
    if (local) local.intervencion_humana = false;
    toast.add({ severity: 'success', summary: 'Listo', detail: 'La IA vuelve a responder este caso.', life: 2500 });
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo reactivar la IA.', life: 4000 });
  }
}

onMounted(() => {
  setViewportMode();
  window.addEventListener('resize', setViewportMode);
  cargar();
});

onBeforeUnmount(() => {
  window.removeEventListener('resize', setViewportMode);
});
</script>

<style scoped>
.wa-shell {
  /* ── Paleta real de WhatsApp (light) ── */
  --wa-accent:        #00a884;
  --wa-accent-strong: #008069;
  --wa-bg-panel:      #ffffff;
  --wa-bg-header:     #f0f2f5;
  --wa-bg-hover:      #f5f6f6;
  --wa-bg-selected:   #e9edef;
  --wa-border:        #e9edef;
  --wa-text-primary:  #111b21;
  --wa-text-secondary:#667781;
  --wa-bubble-out:    #d9fdd3;
  --wa-bubble-in:     #ffffff;
  --wa-chat-bg:       #efeae2;

  font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Helvetica Neue", Helvetica, Arial, sans-serif;
  display: flex;
  height: calc(100vh - 90px);
  min-height: 560px;
  border: 1px solid var(--wa-border);
  border-radius: 12px;
  overflow: hidden;
  background: var(--wa-bg-panel);
  margin: 1rem;
}
@media (prefers-color-scheme: dark) {
  .wa-shell {
    --wa-bg-panel:      #111b21;
    --wa-bg-header:     #202c33;
    --wa-bg-hover:      #202c33;
    --wa-bg-selected:   #2a3942;
    --wa-border:        #222d34;
    --wa-text-primary:  #e9edef;
    --wa-text-secondary:#8696a0;
    --wa-bubble-out:    #005c4b;
    --wa-bubble-in:     #202c33;
    --wa-chat-bg:       #0b141a;
  }
}
/* Por si más adelante agregan un toggle manual de tema */
:root[data-theme="dark"] .wa-shell {
  --wa-bg-panel:      #111b21;
  --wa-bg-header:     #202c33;
  --wa-bg-hover:      #202c33;
  --wa-bg-selected:   #2a3942;
  --wa-border:        #222d34;
  --wa-text-primary:  #e9edef;
  --wa-text-secondary:#8696a0;
  --wa-bubble-out:    #005c4b;
  --wa-bubble-in:     #202c33;
  --wa-chat-bg:       #0b141a;
}

/* ── Rail de iconos ── */
.wa-icon-rail {
  width: 60px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.5rem;
  padding: 1rem 0;
  background: var(--wa-bg-header);
  border-right: 1px solid var(--wa-border);
}
.wa-rail-spacer { flex: 1; }
.wa-rail-icon {
  width: 2.4rem;
  height: 2.4rem;
  border-radius: 8px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 1.15rem;
  color: var(--wa-text-secondary);
}
.wa-rail-icon.activo {
  background: color-mix(in srgb, var(--wa-accent) 16%, transparent);
  color: var(--wa-accent-strong);
}

/* ── Sidebar ── */
.wa-sidebar {
  width: 380px;
  flex-shrink: 0;
  display: flex;
  flex-direction: column;
  border-right: 1px solid var(--wa-border);
  background: var(--wa-bg-panel);
  min-width: 0;
}
.wa-sidebar-oculto { display: none; }
.wa-sidebar-header {
  padding: 1.1rem 1.25rem;
  background: var(--wa-bg-header);
  border-bottom: 1px solid var(--wa-border);
}
.wa-wordmark {
  margin: 0;
  font-size: 1.55rem;
  font-weight: 600;
  color: var(--wa-accent-strong);
}
.wa-sidebar-count {
  font-size: 0.78rem;
  color: var(--wa-text-secondary);
}

.wa-search {
  display: flex;
  align-items: center;
  gap: 0.6rem;
  margin: 0.75rem 1rem;
  padding: 0.55rem 0.9rem;
  border-radius: 8px;
  background: var(--wa-bg-header);
  border: none;
}
.wa-search i { color: var(--wa-text-secondary); }
.wa-search input {
  border: none;
  outline: none;
  background: transparent;
  color: var(--wa-text-primary);
  font-size: 0.88rem;
  width: 100%;
}
.wa-search input::placeholder { color: var(--wa-text-secondary); }

.wa-filter-row {
  display: flex;
  flex-wrap: wrap;
  gap: 0.4rem;
  padding: 0 1rem 0.55rem;
}
.wa-filter-row-estado { padding-bottom: 0.8rem; }
.wa-filter-chip {
  display: flex;
  align-items: center;
  gap: 0.3rem;
  padding: 0.3rem 0.65rem;
  border-radius: 999px;
  border: 1px solid var(--wa-border);
  background: var(--wa-bg-panel);
  color: var(--wa-text-secondary);
  font-size: 0.74rem;
  font-weight: 500;
  cursor: pointer;
  white-space: nowrap;
  line-height: 1.3;
}
.wa-filter-chip-sm { font-size: 0.71rem; padding: 0.24rem 0.6rem; opacity: 0.85; }
.wa-filter-chip.activo {
  background: var(--chip-color, var(--wa-accent));
  border-color: var(--chip-color, var(--wa-accent));
  color: #fff;
}
.wa-filter-dot {
  width: 7px;
  height: 7px;
  border-radius: 50%;
  background: var(--chip-color, currentColor);
}
.wa-filter-chip.activo .wa-filter-dot { background: #fff; }
.wa-filter-count {
  opacity: 0.65;
  font-weight: 700;
}

.wa-list-loading, .wa-list-empty {
  text-align: center;
  padding: 2.5rem 1rem;
  color: var(--wa-text-secondary);
}

.wa-chat-list {
  list-style: none;
  margin: 0;
  padding: 0;
  overflow-y: auto;
  flex: 1;
}
.wa-chat-item {
  display: flex;
  gap: 0.75rem;
  padding: 0.85rem 1.1rem;
  border-bottom: 1px solid var(--wa-border);
  cursor: pointer;
  transition: background 0.12s;
}
.wa-chat-item:hover { background: var(--wa-bg-hover); }
.wa-chat-item.activo { background: var(--wa-bg-selected); }
.wa-chat-item.urgente { background: color-mix(in srgb, #d03b3b 8%, transparent); }
.wa-chat-item.urgente.activo { background: color-mix(in srgb, #d03b3b 16%, transparent); }

.wa-avatar {
  position: relative;
  flex-shrink: 0;
  width: 2.75rem;
  height: 2.75rem;
  border-radius: 50%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
  background: color-mix(in srgb, var(--serie-color) 20%, transparent);
  box-shadow: 0 0 0 2px var(--serie-color);
  color: var(--serie-color);
  font-size: 1.2rem;
}
.wa-avatar img {
  width: 100%;
  height: 100%;
  object-fit: cover;
}
.wa-avatar-lg { width: 3rem; height: 3rem; }
.wa-avatar-alert {
  position: absolute;
  bottom: -2px;
  right: -2px;
  width: 1.15rem;
  height: 1.15rem;
  border-radius: 50%;
  background: #d03b3b;
  color: #fff;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 0.6rem;
  border: 2px solid var(--wa-bg-panel);
}

.wa-chat-info {
  min-width: 0;
  flex: 1;
  display: flex;
  flex-direction: column;
  gap: 0.2rem;
}
.wa-chat-row1 {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  gap: 0.5rem;
}
.wa-chat-nombre {
  font-weight: 600;
  color: var(--wa-text-primary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.wa-chat-tiempo {
  flex-shrink: 0;
  font-size: 0.72rem;
  color: var(--wa-text-secondary);
}
.wa-chat-row2 {
  display: flex;
  align-items: center;
  gap: 0.4rem;
}
.wa-chat-preview {
  flex: 1;
  min-width: 0;
  font-size: 0.83rem;
  color: var(--wa-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
.wa-chat-dot {
  flex-shrink: 0;
  width: 8px;
  height: 8px;
  border-radius: 50%;
  background: var(--cat-color);
}
.wa-chat-row3 {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  flex-wrap: wrap;
}
.wa-chat-categoria {
  font-size: 0.7rem;
  color: var(--wa-text-secondary);
  text-transform: uppercase;
  letter-spacing: 0.02em;
}

.wa-contacto {
  border-bottom: 1px solid var(--wa-border);
}
.wa-contacto .wa-chat-item { border-bottom: none; }
.wa-historial-toggle {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  width: 100%;
  padding: 0.5rem 1.1rem 0.6rem 4.5rem;
  border: none;
  background: none;
  color: var(--wa-accent-strong);
  font-size: 0.78rem;
  font-weight: 600;
  cursor: pointer;
  text-align: left;
}
.wa-historial-list {
  list-style: none;
  margin: 0;
  padding: 0 1rem 0.6rem 4.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.4rem;
}
.wa-historial-item {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.4rem 0.6rem;
  border-radius: 8px;
  cursor: pointer;
  background: var(--wa-bg-header);
  border: 1px solid var(--wa-border);
}
.wa-historial-item:hover { border-color: var(--wa-accent); }
.wa-historial-item.activo { box-shadow: 0 0 0 2px color-mix(in srgb, var(--wa-accent) 30%, transparent); }
.wa-historial-fecha {
  font-size: 0.7rem;
  color: var(--wa-text-secondary);
  flex-shrink: 0;
}
.wa-historial-preview {
  font-size: 0.78rem;
  color: var(--wa-text-secondary);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
  min-width: 0;
}

/* ── Panel ── */
.wa-panel {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.wa-panel-oculto { display: none; }
.wa-panel {
  background: var(--wa-chat-bg);
}
.wa-panel-empty {
  flex: 1;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  text-align: center;
  gap: 0.5rem;
  padding: 2rem;
  color: var(--wa-text-secondary);
  background: var(--wa-bg-header);
}
.wa-panel-empty i {
  font-size: 3rem;
  color: var(--wa-accent);
  opacity: 0.6;
  margin-bottom: 0.5rem;
}
.wa-panel-empty h2 {
  margin: 0;
  color: var(--wa-text-primary);
  font-weight: 400;
}

.wa-panel-header {
  display: flex;
  align-items: center;
  gap: 0.85rem;
  padding: 0.85rem 1.5rem;
  border-bottom: 1px solid var(--wa-border);
  background: var(--wa-bg-header);
}
.wa-back-btn {
  border: none;
  background: none;
  font-size: 1.1rem;
  color: var(--wa-text-primary);
  cursor: pointer;
  padding: 0.3rem;
}
.wa-info-btn {
  border: none;
  background: none;
  font-size: 1.2rem;
  color: var(--wa-text-secondary);
  cursor: pointer;
  padding: 0.3rem 0.5rem;
  flex-shrink: 0;
}
.wa-panel-identidad {
  flex: 1;
  display: flex;
  flex-direction: column;
  min-width: 0;
}
.wa-panel-nombre {
  font-weight: 600;
  color: var(--wa-text-primary);
}
.wa-panel-telefono {
  font-size: 0.78rem;
  color: var(--wa-text-secondary);
}

.wa-panel-alerta {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  padding: 0.65rem 1.5rem;
  background: color-mix(in srgb, #d03b3b 15%, transparent);
  color: #d03b3b;
  font-weight: 600;
  font-size: 0.85rem;
}

.wa-intervencion-banner {
  display: flex;
  align-items: center;
  justify-content: space-between;
  gap: 0.75rem;
  padding: 0.6rem 1.5rem;
  background: color-mix(in srgb, var(--wa-accent) 16%, transparent);
  color: var(--wa-accent-strong);
  font-weight: 600;
  font-size: 0.85rem;
  flex-wrap: wrap;
}

.wa-compose {
  display: flex;
  gap: 0.6rem;
  align-items: center;
  padding: 0.85rem 1.5rem;
  background: var(--wa-bg-header);
  border-top: 1px solid var(--wa-border);
}

.wa-diagnostico {
  margin: 0.85rem 1.5rem 0;
  padding: 0.9rem 1.1rem;
  border-radius: 10px;
  background: color-mix(in srgb, var(--wa-accent) 10%, var(--wa-bg-panel));
  border: 1px solid color-mix(in srgb, var(--wa-accent) 30%, transparent);
}
.wa-diagnostico-titulo {
  display: flex;
  align-items: center;
  gap: 0.4rem;
  font-weight: 700;
  font-size: 0.82rem;
  color: var(--wa-accent-strong);
  margin-bottom: 0.4rem;
}
.wa-diagnostico-texto {
  margin: 0;
  font-family: inherit;
  white-space: pre-wrap;
  word-break: break-word;
  font-size: 0.85rem;
  color: var(--wa-text-primary);
}

.wa-panel-controles {
  display: flex;
  gap: 1rem;
  flex-wrap: wrap;
  padding: 1rem 1.5rem;
  background: var(--wa-bg-panel);
  border-bottom: 1px solid var(--wa-border);
}
.wa-control-field {
  flex: 1;
  min-width: 180px;
}
.wa-control-field-asignado { flex: 1.3; }
.wa-control-field-contacto { flex: 1.3; }
.wa-control-field-numero { flex: 0.8; min-width: 140px; }
.wa-control-field label {
  display: block;
  font-weight: 600;
  margin-bottom: 0.3rem;
  font-size: 0.82rem;
  color: var(--wa-text-secondary);
}
.wa-asignado-row {
  display: flex;
  gap: 0.5rem;
}

.wa-panel-messages {
  flex: 1;
  overflow-y: auto;
  padding: 1.25rem 1.5rem;
  display: flex;
  flex-direction: column;
  gap: 0.65rem;
  background: var(--wa-chat-bg);
}

.badge-estado {
  padding: 0.3rem 0.75rem;
  border-radius: 999px;
  font-size: 0.76rem;
  font-weight: 700;
  white-space: nowrap;
  flex-shrink: 0;
}
.badge-abierto { background: color-mix(in srgb, var(--wa-accent-strong) 18%, transparent); color: var(--wa-accent-strong); }
.badge-en_progreso { background: color-mix(in srgb, #fab219 25%, transparent); color: #b07500; }
.badge-esperando_cliente { background: color-mix(in srgb, #eb6834 22%, transparent); color: #eb6834; }
.badge-escalado { background: color-mix(in srgb, #d03b3b 22%, transparent); color: #d03b3b; }
.badge-resuelto { background: color-mix(in srgb, var(--wa-accent) 22%, transparent); color: var(--wa-accent-strong); }
.badge-cerrado { background: color-mix(in srgb, var(--wa-text-secondary) 25%, transparent); color: var(--wa-text-secondary); }

.referencia-tag {
  padding: 0.1rem 0.55rem;
  border-radius: 999px;
  background: var(--wa-bg-header);
  border: 1px solid var(--wa-border);
  color: var(--wa-text-secondary);
  font-size: 0.7rem;
  font-weight: 700;
}

.mensaje-bubble {
  max-width: 70%;
  padding: 0.5rem 0.7rem;
  border-radius: 8px;
  font-size: 0.9rem;
  box-shadow: 0 1px 0.5px rgba(0,0,0,0.13);
}
.mensaje-bubble.in {
  align-self: flex-start;
  background: var(--wa-bubble-in);
  border-top-left-radius: 0;
}
.mensaje-bubble.out {
  align-self: flex-end;
  background: var(--wa-bubble-out);
  border-top-right-radius: 0;
}
.mensaje-autor {
  font-size: 0.68rem;
  font-weight: 700;
  text-transform: uppercase;
  letter-spacing: 0.04em;
  color: var(--wa-accent-strong);
  margin-bottom: 0.15rem;
}
.mensaje-texto {
  white-space: pre-wrap;
  word-break: break-word;
  color: var(--wa-text-primary);
}
.mensaje-imagen-link {
  display: block;
  margin-bottom: 0.35rem;
}
.mensaje-imagen {
  display: block;
  max-width: 100%;
  max-height: 260px;
  border-radius: 6px;
  object-fit: cover;
}
.mensaje-fecha {
  margin-top: 0.2rem;
  font-size: 0.68rem;
  color: var(--wa-text-secondary);
  text-align: right;
}
.w-full { width: 100%; }

@media (max-width: 860px) {
  .wa-shell { margin: 0; border-radius: 0; height: calc(100vh - 70px); border: none; }
  .wa-sidebar { width: 100%; }

  /* Header de lista más como app nativa */
  .wa-sidebar-header { padding: 0.9rem 1rem; }
  .wa-wordmark { font-size: 1.3rem; }

  /* Chat list con más aire, tipo app */
  .wa-chat-item { padding: 0.75rem 1rem; gap: 0.65rem; }
  .wa-avatar { width: 3rem; height: 3rem; }
  .wa-chat-nombre { font-size: 1rem; }
  .wa-chat-preview { font-size: 0.87rem; }

  /* Header de conversación: nombre tappeable abre info, como WhatsApp real */
  .wa-panel-header { padding: 0.6rem 0.85rem; gap: 0.65rem; }
  .wa-panel-identidad { cursor: pointer; }
  .wa-panel-nombre { font-size: 1.05rem; }

  .wa-panel-controles { flex-direction: column; background: var(--wa-bg-panel); }

  /* Compose bar idéntica a WhatsApp: pill + botón circular verde */
  .wa-compose {
    padding: 0.5rem 0.6rem;
    background: var(--wa-bg-header);
  }
  .wa-compose :deep(.p-inputtext) {
    border-radius: 999px;
    background: var(--wa-bg-panel);
    border: none;
    padding: 0.65rem 1.1rem;
  }
  .wa-compose :deep(.p-button) {
    width: 2.6rem;
    height: 2.6rem;
    border-radius: 50%;
    background: var(--wa-accent);
    border-color: var(--wa-accent);
    flex-shrink: 0;
    padding: 0;
    display: flex;
    align-items: center;
    justify-content: center;
  }

  .mensaje-bubble { max-width: 82%; }
}
</style>
