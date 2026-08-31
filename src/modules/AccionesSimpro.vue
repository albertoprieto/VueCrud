<template>
  <section class="acc-page">
    <Button icon="pi pi-arrow-left" label="Volver a SIM ESPAÑOL" class="p-button-text" @click="router.push('/utilidades-imei')" />

    <div v-if="loading" class="acc-loading"><i class="pi pi-spin pi-spinner" style="font-size:2rem;" /></div>

    <div v-else-if="!row" class="acc-loading">No se encontró el registro.</div>

    <div v-else class="acc-wrap">
      <h1>Acciones SIMPRO</h1>

      <div class="acc-card acc-info">
        <div><strong>Tipo:</strong> {{ row.tipo }}</div>
        <div><strong>IMEI:</strong> {{ row.imei || '—' }}</div>
        <div><strong>ICCID:</strong> {{ row.iccid || '—' }}</div>
        <div><strong>SIM ESPAÑOL:</strong> {{ row.deviceMobile || '—' }}</div>
        <div><strong>Usuario:</strong> {{ row.deaccount || '—' }}</div>
        <div><strong>Cliente:</strong> {{ row.accountName || '—' }}</div>
        <div><strong>Plataforma:</strong> {{ row.plataforma || '—' }}</div>
        <div>
          <strong>Salud:</strong>
          <Tag :value="saludTag(row.salud).value" :severity="saludTag(row.salud).severity" />
          <span class="acc-hint" style="margin-left:.4rem">({{ row.sim_customer_status || '—' }})</span>
        </div>
        <div><strong>Vigencia:</strong> {{ row.vigencia_sim || '—' }}</div>
        <div>
          <strong>Bloqueo por equipo:</strong>
          <template v-if="row.imei_lock === 1"><span class="acc-warn">BLOQUEADO (cambio de IMEI)</span></template>
          <template v-else-if="row.imei_lock === 0">Sin bloqueo</template>
          <template v-else>Desconocido — pulsa "Verificar estado"</template>
        </div>
        <div v-if="row.network_imei"><strong>IMEI visto en red:</strong> {{ row.network_imei }}</div>
        <div v-if="imeiMismatch(row.network_imei, row.imei)" class="acc-warn">
          ⚠ El IMEI del registro ({{ row.imei }}) no coincide con el que SIMPRO ve en la red ({{ row.network_imei }}).
        </div>
        <div v-if="row.last_seen"><strong>Última señal:</strong> {{ fechaCorta(row.last_seen) }}</div>
        <div v-if="row.sim_state === 'suspendido_temporal'" class="acc-warn">
          Suspendido temporal desde {{ fechaCorta(row.suspendido_desde) }}
        </div>
        <div v-if="row.sim_state === 'bloqueado_imei'" class="acc-warn">
          ⚠ SIM BLOQUEADO por cambio de equipo (locked_due_to_imei_change). No pasa tráfico.
          Si el cambio fue a propósito: pulsa "Desbloquear" — SIMPRO lo procesa en unos minutos;
          cuando figure "active", "Preparar" + "Bloquear" para re-armar en el equipo correcto.
          Si no fue a propósito, monta el SIM de vuelta en el equipo original.
        </div>
        <div><strong>Consumo del mes:</strong>
          {{ row.data_usage_mb != null ? row.data_usage_mb + ' MB' : '—' }}
          <span v-if="row.sin_trafico" class="acc-warn">· sin tráfico</span>
        </div>
      </div>

      <div class="acc-grid">
        <div class="acc-card">
          <h3>Consulta</h3>
          <Button label="Verificar estado" icon="pi pi-sync" outlined :loading="busy==='estado'" @click="accion('estado')" />
          <Button label="Verificar consumo" icon="pi pi-chart-bar" outlined :loading="busy==='consumo'" @click="accion('consumo')" />
          <Button label="Refrescar red" icon="pi pi-wifi" outlined :loading="busy==='refrescar-red'" @click="accion('refrescar-red')" />
        </div>

        <div class="acc-card">
          <h3>Bloqueo por equipo (IMEI lock)</h3>
          <p class="acc-hint">
            Arma el bloqueo. Si después alguien mueve el SIM a otro equipo (IMEI distinto),
            SIMPRO lo bloquea solo y deja de pasar tráfico. SIMPRO procesa en segundo plano
            (unos minutos). Usa "Preparar" para que el equipo objetivo reporte antes de armar.
          </p>
          <label class="acc-hint">IMEI objetivo (equipo donde va el SIM)</label>
          <InputText v-model="lockTarget" placeholder="IMEI del equipo objetivo" />
          <Button label="1. Preparar (esperar señal del equipo)" icon="pi pi-sync" outlined
            :loading="busy==='preparar'" @click="accion('preparar')" />
          <p v-if="prepText" :class="['acc-hint', prepMatch ? 'acc-ok' : 'acc-warn']">{{ prepText }}</p>
          <Button label="2. Bloquear a este equipo" icon="pi pi-lock" outlined
            :loading="busy==='lock-on'" @click="accion('lock-on')" />
          <Button v-if="row.sim_state === 'bloqueado_imei'"
            label="Desbloquear (se bloqueó por cambio de equipo)" icon="pi pi-unlock" severity="help" outlined
            :loading="busy==='recasar'" @click="accion('recasar')" />
          <Button label="Ver JSON de SIMPRO" icon="pi pi-code" text size="small"
            :loading="busy==='raw'" @click="accion('raw')" />
          <pre v-if="rawText" class="acc-raw">{{ rawText }}</pre>
        </div>

        <div class="acc-card">
          <h3>Cambiar tarjeta física</h3>
          <p class="acc-hint">Conserva número, plan y vigencia. Para SIM dañado.</p>
          <InputText v-model="nuevoIccid" placeholder="ICCID de la tarjeta nueva" />
          <Button label="Cambiar tarjeta" icon="pi pi-sim" outlined
            :disabled="!nuevoIccid" :loading="busy==='swap'" @click="accion('swap')" />
        </div>

        <div class="acc-card">
          <h3>Historial de consumo</h3>
          <Button label="Ver últimos 6 meses" icon="pi pi-calendar" outlined :loading="busy==='historial'" @click="accion('historial')" />
          <ul v-if="historial.length" class="acc-list">
            <li v-for="h in historial" :key="h.mes">{{ h.mes }}: {{ h.resumen }}</li>
          </ul>
        </div>

        <div class="acc-card">
          <h3>Suspensión temporal</h3>
          <template v-if="row.sim_state === 'suspendido_temporal'">
            <Button label="Reactivar SIM" icon="pi pi-play" severity="success" :loading="busy==='reactivar'" @click="accion('reactivar')" />
          </template>
          <template v-else>
            <label class="acc-check">
              <input type="checkbox" v-model="pausaFactura" />
              También pausar facturación (tariff holiday hasta fin de mes)
            </label>
            <Button label="Suspender temporal" icon="pi pi-pause" severity="warning" :loading="busy==='suspender'" @click="accion('suspender')" />
          </template>
        </div>

        <div class="acc-card">
          <h3>Cancelación</h3>
          <template v-if="row.sim_state === 'cancelacion_programada'">
            <Button label="Detener cancelación" icon="pi pi-undo" outlined :loading="busy==='detener'" @click="accion('detener')" />
          </template>
          <template v-else>
            <label>Fecha de cancelación (opcional, dd/mm/aaaa)</label>
            <InputText v-model="cancelarFecha" placeholder="hoy si se deja vacío" />
            <Button label="Cancelar en SIMPRO" icon="pi pi-times-circle" severity="danger" :loading="busy==='cancelar'" @click="accion('cancelar')" />
          </template>
        </div>

        <div class="acc-card">
          <h3>Historial de acciones</h3>
          <Button label="Ver bitácora" icon="pi pi-history" outlined :loading="busy==='eventos'" @click="accion('eventos')" />
          <ul v-if="eventos.length" class="acc-list">
            <li v-for="e in eventos" :key="e.id">
              <span :class="e.ok ? '' : 'acc-warn'">{{ fechaCorta(e.creado_en) }} · {{ e.accion }}</span>
              <template v-if="e.detalle"> — {{ e.detalle }}</template>
              <template v-if="e.usuario"> ({{ e.usuario }})</template>
            </li>
          </ul>
          <p v-else-if="eventosCargados" class="acc-hint">Sin acciones registradas.</p>
        </div>
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import Tag from 'primevue/tag';
import { useToast } from 'primevue/usetoast';
import {
  getConsultaSim,
  verificarEstadoSim,
  verificarConsumoSim,
  suspenderSim,
  reactivarSim,
  cancelarSim,
  detenerCancelacionSim,
  imeiLockSim,
  prepararLockSim,
  recasarSim,
  getSimproRaw,
  getEventosSim,
  refrescarRedSim,
  historialConsumoSim,
  swapIccidSim
} from '@/services/utilidadesImeiService';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const id = route.params.id;
const loading = ref(true);
const raw = ref(null);
const row = ref(null);
const busy = ref('');

const nuevoIccid = ref('');
const historial = ref([]);
const pausaFactura = ref(false);
const cancelarFecha = ref('');
const rawText = ref('');
const eventos = ref([]);
const eventosCargados = ref(false);
const lockTarget = ref('');
const prepText = ref('');
const prepMatch = ref(false);

function mapRow(r) {
  return {
    id: r.id,
    tipo: r.tipo || '',
    imei: r.imei || '',
    iccid: r.iccid || '',
    deviceMobile: r.device_mobile || '',
    deaccount: r.deaccount || '',
    accountName: r.account_name || '',
    plataforma: r.plataforma || '',
    vigencia_sim: r.vigencia_sim || '',
    sim_state: r.sim_state || '',
    sim_customer_status: r.sim_customer_status || '',
    suspendido_desde: r.suspendido_desde || '',
    data_usage_mb: r.data_usage_mb ?? null,
    sin_trafico: !!r.sin_trafico,
    imei_lock: r.imei_lock == null ? null : Number(r.imei_lock),
    imei_lock_imei: r.imei_lock_imei || '',
    network_imei: r.network_imei || '',
    last_seen: r.last_seen || '',
    in_session: r.in_session == null ? null : Number(r.in_session),
    salud: r.salud || 'desconocido'
  };
}

function fechaCorta(v) {
  return v ? String(v).slice(0, 10) : '';
}

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

// La red reporta IMEISV (16 díg); el registro suele traer IMEI de 15.
// Comparar por el núcleo de 14 (TAC + serie).
function imeiCore(v) {
  return String(v || '').replace(/\D+/g, '').slice(0, 14);
}
function imeiMismatch(redImei, regImei) {
  const a = imeiCore(redImei);
  const b = imeiCore(regImei);
  return !!a && !!b && a !== b;
}

function resumenConsumoMes(datos) {
  try {
    const first = Array.isArray(datos) ? datos[0] : (datos?.sims?.[0] || datos);
    const up = Number(first?.month_to_date_bytes_up || first?.bytes_up || 0);
    const down = Number(first?.month_to_date_bytes_down || first?.bytes_down || 0);
    if (up || down) return `${((up + down) / (1024 * 1024)).toFixed(2)} MB`;
    return JSON.stringify(datos).slice(0, 120);
  } catch {
    return '—';
  }
}

async function cargar() {
  loading.value = true;
  try {
    raw.value = await getConsultaSim(id);
    row.value = mapRow(raw.value);
    if (!lockTarget.value) {
      lockTarget.value = row.value?.imei || row.value?.imei_lock_imei || row.value?.network_imei || '';
    }
  } catch {
    row.value = null;
  }
  loading.value = false;
}

function ok(detail) {
  toast.add({ severity: 'success', summary: 'SIMPRO', detail, life: 3500 });
}
function err(e) {
  toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || e?.message || 'La acción falló.', life: 5000 });
}

async function accion(a) {
  busy.value = a;
  try {
    let res;
    if (a === 'estado') {
      res = await verificarEstadoSim(id);
      ok('Estado + conectividad actualizados. Salud: ' + (res.salud || '?'));
    } else if (a === 'consumo') {
      res = await verificarConsumoSim(id);
      ok('Consumo + señal actualizados. Salud: ' + (res.salud || '?'));
    } else if (a === 'refrescar-red') {
      await refrescarRedSim(id);
      ok('Refresh de red enviado.');
    } else if (a === 'preparar') {
      const data = await prepararLockSim(id, lockTarget.value.trim());
      prepMatch.value = !!data.match;
      prepText.value = `${data.mensaje} Red ve: ${data.network_imei || '—'}`
        + (data.minutos_desde_ultima_senal != null ? ` (hace ${Math.round(data.minutos_desde_ultima_senal)} min)` : '');
      (prepMatch.value ? ok : (m => err({ message: m })))(prepText.value);
    } else if (a === 'lock-on') {
      const objetivo = lockTarget.value.trim();
      try {
        res = await imeiLockSim(id, true, false, objetivo);
      } catch (e) {
        // 409 = guardia previa (equipo objetivo no reporta / IMEI no coincide).
        if (e?.response?.status === 409) {
          const detalle = e.response.data?.detail || 'No se pudo verificar el equipo.';
          if (window.confirm(detalle + '\n\n¿Bloquear de todos modos (force)?')) {
            res = await imeiLockSim(id, true, true, objetivo);
          } else {
            busy.value = ''; return;
          }
        } else {
          throw e;
        }
      }
      ok(res?.message || 'SIM bloqueado a este equipo.');
    } else if (a === 'recasar') {
      if (!window.confirm('Quita el bloqueo por equipo del SIM. SIMPRO lo procesa en segundo plano. ¿Continuar?')) { busy.value = ''; return; }
      res = await recasarSim(id);
      if (res.desbloqueado) ok(res.message || 'SIM desbloqueado.');
      else err({ message: res.message || 'Desbloqueo encolado.' });
    } else if (a === 'raw') {
      const data = await getSimproRaw(id);
      rawText.value = JSON.stringify(data, null, 2);
      ok('JSON de SIMPRO cargado.');
    } else if (a === 'eventos') {
      const data = await getEventosSim(id);
      eventos.value = data.eventos || [];
      eventosCargados.value = true;
      ok('Bitácora cargada.');
    } else if (a === 'swap') {
      if (!window.confirm('Esto cambia la tarjeta física en SIMPRO. ¿Continuar?')) { busy.value = ''; return; }
      res = await swapIccidSim(id, nuevoIccid.value.trim());
      ok('Tarjeta cambiada. El registro apunta al ICCID nuevo.'
        + (res.avisos?.length ? ' ' + res.avisos.join(' ') : ''));
    } else if (a === 'historial') {
      const data = await historialConsumoSim(id, 6);
      historial.value = (data.historial || []).map(h => ({
        mes: h.mes,
        resumen: h.error ? `error: ${h.error}` : resumenConsumoMes(h.datos)
      }));
      ok('Historial cargado.');
    } else if (a === 'suspender') {
      if (!window.confirm('Se cortará TODO el tráfico del SIM: el equipo dejará de reportar hasta reactivarlo. ¿Continuar?')) { busy.value = ''; return; }
      res = await suspenderSim(id, { pausarFacturacion: pausaFactura.value });
      if (res.avisos?.length) res.avisos.forEach(m => err({ message: m }));
      else ok(pausaFactura.value ? 'SIM suspendido y facturación pausada.' : 'SIM suspendido (tráfico bloqueado).');
    } else if (a === 'reactivar') {
      res = await reactivarSim(id);
      if (res.avisos?.length) res.avisos.forEach(m => err({ message: m }));
      else ok('SIM reactivado.');
    } else if (a === 'cancelar') {
      if (!window.confirm('Esto cancela el SIM en SIMPRO. ¿Continuar?')) { busy.value = ''; return; }
      res = await cancelarSim(id, { cancellationDate: cancelarFecha.value.trim() || undefined });
      ok(`Cancelación registrada (${res.cancellation_date}).`);
    } else if (a === 'detener') {
      res = await detenerCancelacionSim(id);
      ok('Cancelación detenida.');
    }
    if (res && res.item) row.value = mapRow(res.item);
  } catch (e) {
    err(e);
  } finally {
    busy.value = '';
  }
}

onMounted(cargar);
</script>

<style scoped>
.acc-page {
  padding: 1.25rem;
  max-width: 1100px;
  margin: 0 auto;
}
.acc-loading {
  text-align: center;
  padding: 3rem;
  color: var(--color-text);
}
.acc-wrap h1 {
  margin: 0.5rem 0 1rem;
  color: var(--color-title);
}
.acc-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.5rem;
}
.acc-card h3 {
  margin: 0 0 0.25rem;
  font-size: 0.95rem;
  color: var(--color-title);
}
.acc-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(220px, 1fr));
  gap: 0.4rem 1rem;
  margin-bottom: 1.25rem;
}
.acc-grid {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
  gap: 1rem;
  align-items: start;
}
.acc-warn { color: #d1242f; font-weight: 600; }
.acc-ok { color: #238636; font-weight: 600; }
.acc-hint { margin: 0; font-size: 0.8rem; opacity: 0.7; }
.acc-raw {
  background: var(--color-bg-light, #f5f5f5);
  border-radius: 8px;
  padding: 0.6rem;
  font-size: 0.72rem;
  max-height: 260px;
  overflow: auto;
  white-space: pre-wrap;
  word-break: break-word;
}
.acc-check { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; }
.acc-list { margin: 0.25rem 0 0; padding-left: 1.1rem; font-size: 0.82rem; }
.w-full { width: 100%; }
</style>
