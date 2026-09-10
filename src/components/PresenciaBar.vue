<template>
  <div v-if="usuarios.length" class="presencia-bar">
    <div class="presencia-inner">
      <button
        class="presencia-toggle"
        :title="colapsada ? 'Mostrar conectados' : 'Ocultar'"
        @click="toggle"
      >
        <span class="pi" :class="colapsada ? 'pi-users' : 'pi-chevron-up'"></span>
      </button>
      <span class="presencia-head">
        <span class="dot dot-on"></span>
        {{ conectados.length }} conectado{{ conectados.length === 1 ? '' : 's' }}
      </span>
      <div v-if="!colapsada" class="presencia-list">
        <span
          v-for="u in ordenados"
          :key="u.id"
          class="chip"
          :class="`chip-${criticidad(u)}`"
          :title="tooltip(u)"
        >
          <span class="dot" :class="`dot-${criticidad(u)}`"></span>
          <span class="nombre">{{ u.username }}</span>
          <span class="tiempo">{{ esOnline(u) ? 'ahora' : rel(ultimoVisto(u)) }}</span>
        </span>
      </div>
    </div>

    <button
      class="tema-btn"
      :title="tema === 'dark' ? 'Cambiar a tema claro' : 'Cambiar a tema oscuro'"
      @click="toggleTheme"
    >
      <span class="pi" :class="tema === 'dark' ? 'pi-sun' : 'pi-moon'"></span>
    </button>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, onUnmounted } from 'vue';
import { getUsuarios } from '@/services/usuariosService';
import { useLoginStore } from '@/stores/loginStore';
import { useTheme } from '@/composables/useTheme';
import { USUARIOS_VIGILADOS } from '@/config/vigilados';

const loginStore = useLoginStore();
const { tema, toggleTheme } = useTheme();
const ONLINE_MS = 3 * 60 * 1000;
const usuarios = ref([]);
let timer = null;

const colapsada = ref((() => {
  try { return localStorage.getItem('presenciaBarColapsada') === '1'; } catch { return false; }
})());
function toggle() {
  colapsada.value = !colapsada.value;
  try { localStorage.setItem('presenciaBarColapsada', colapsada.value ? '1' : '0'); } catch { /* ignore */ }
}

const toMs = (f) => (f ? new Date(f.endsWith('Z') ? f : f + 'Z').getTime() : 0);
const ultimoVisto = (u) => (toMs(u.ultimo_ping) > toMs(u.ultima_sesion) ? u.ultimo_ping : u.ultima_sesion);
const esOnline = (u) => Date.now() - toMs(u.ultimo_ping) < ONLINE_MS;

// Semáforo por antigüedad de la última actividad.
function criticidad(u) {
  if (esOnline(u)) return 'ok';
  const min = (Date.now() - toMs(ultimoVisto(u))) / 60000;
  if (min < 4 * 60) return 'medio';   // últimas horas
  if (min < 24 * 60) return 'alto';   // mismo día
  return 'critico';                   // más de 1 día
}

const conectados = computed(() => usuarios.value.filter(esOnline));
const ordenados = computed(() =>
  [...usuarios.value].sort((a, b) => {
    const oa = esOnline(a), ob = esOnline(b);
    if (oa !== ob) return ob - oa;
    return toMs(ultimoVisto(b)) - toMs(ultimoVisto(a));
  })
);

function rel(fecha) {
  if (!fecha) return 'sin registro';
  const m = Math.floor((Date.now() - toMs(fecha)) / 60000);
  if (m < 1) return 'hace un momento';
  if (m < 60) return `hace ${m} min`;
  const h = Math.floor(m / 60);
  if (h < 24) return `hace ${h} h`;
  const d = Math.floor(h / 24);
  if (d === 1) return 'ayer';
  if (d < 30) return `hace ${d} d`;
  const mo = Math.floor(d / 30);
  return `hace ${mo} mes${mo > 1 ? 'es' : ''}`;
}

function tooltip(u) {
  const fmt = (f) => (f
    ? new Date(f.endsWith('Z') ? f : f + 'Z').toLocaleString('es-MX', { dateStyle: 'short', timeStyle: 'short' })
    : '—');
  const estado = esOnline(u) ? 'Conectado ahora' : `Última señal: ${fmt(u.ultimo_ping)}`;
  return `${u.username}\n${estado}\nÚltimo ingreso (contraseña): ${fmt(u.ultima_sesion)}`;
}

async function cargar() {
  try {
    const todos = await getUsuarios();
    // Cada cliente filtra su propia respuesta: los usuarios vigilados + el
    // propio usuario firmado (señal de que el heartbeat funciona). Al resto
    // el usuario firmado no le aparece si no está en la lista.
    const yo = loginStore.user?.id;
    usuarios.value = todos.filter(
      (u) => USUARIOS_VIGILADOS.includes((u.username || '').toLowerCase()) || u.id === yo
    );
  } catch {
    /* silencioso: la barra no debe romper la pantalla */
  }
}

onMounted(() => {
  cargar();
  timer = setInterval(cargar, 60000);
});
onUnmounted(() => clearInterval(timer));
</script>

<style scoped>
.presencia-bar {
  position: relative;
  width: 100%;
  padding: 0.4rem 2.4rem;
  background: var(--color-card, #f7f7fa);
  color: var(--color-text, #222);
  border-bottom: 1px solid var(--color-border, #e0e0e0);
  font-size: 0.8rem;
  box-sizing: border-box;
}
.presencia-inner {
  display: flex;
  align-items: center;
  justify-content: center;
  gap: 0.75rem;
  max-width: 100%;
}
.tema-btn {
  position: absolute;
  right: 0.5rem;
  top: 50%;
  transform: translateY(-50%);
  border: none;
  background: transparent;
  color: var(--color-text, #222);
  opacity: 0.45;
  font-size: 1rem;
  line-height: 1;
  padding: 0.3rem;
  cursor: pointer;
  transition: opacity 0.15s ease, transform 0.15s ease;
}
.tema-btn:hover {
  opacity: 1;
  transform: translateY(-50%) scale(1.15);
}
.presencia-toggle {
  display: flex;
  align-items: center;
  justify-content: center;
  width: 1.4rem;
  height: 1.4rem;
  padding: 0;
  border: 1px solid var(--color-border, #e0e0e0);
  border-radius: 50%;
  background: var(--color-bg, #fff);
  color: var(--color-text, #222);
  font-size: 0.7rem;
  cursor: pointer;
  flex-shrink: 0;
}
.presencia-toggle:hover {
  background: var(--color-card, #f0f0f0);
}
.presencia-head {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  font-weight: 600;
  color: var(--color-text, #222);
  white-space: nowrap;
  flex-shrink: 0;
}
.presencia-list {
  display: flex;
  gap: 0.4rem;
  overflow-x: auto;
  padding-bottom: 2px;
  min-width: 0;
}
.presencia-list::-webkit-scrollbar {
  height: 4px;
}
.presencia-list::-webkit-scrollbar-thumb {
  background: var(--color-border, #ccc);
  border-radius: 2px;
}
.chip {
  display: flex;
  align-items: center;
  gap: 0.35rem;
  padding: 0.15rem 0.55rem 0.15rem 0.4rem;
  border-radius: 1rem;
  background: var(--color-bg, #fff);
  border: 1px solid var(--color-border, #e0e0e0);
  white-space: nowrap;
}
.dot {
  width: 0.5rem;
  height: 0.5rem;
  border-radius: 50%;
  flex-shrink: 0;
}
.chip-ok { border-color: var(--color-success); }
.dot-ok { background: var(--color-success); }
.chip-medio { border-color: var(--color-warning); opacity: 0.9; }
.dot-medio { background: var(--color-warning); }
.chip-alto { border-color: color-mix(in srgb, var(--color-warning) 55%, var(--color-error)); opacity: 0.75; }
.dot-alto { background: color-mix(in srgb, var(--color-warning) 55%, var(--color-error)); }
.chip-critico { border-color: var(--color-error); opacity: 0.6; }
.dot-critico { background: var(--color-error); }
.nombre {
  max-width: 9rem;
  overflow: hidden;
  text-overflow: ellipsis;
  color: var(--color-text, #222);
}
.tiempo {
  opacity: 0.7;
  font-variant-numeric: tabular-nums;
}
@media (max-width: 768px) {
  .presencia-bar {
    font-size: 0.75rem;
  }
  .nombre {
    max-width: 6rem;
  }
}
</style>
