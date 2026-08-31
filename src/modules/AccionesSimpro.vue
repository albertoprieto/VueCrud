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
        <div><strong>Vigencia:</strong> {{ row.vigencia_sim || '—' }}</div>

        <div v-if="row.network_imei"><strong>IMEI visto en red:</strong> {{ row.network_imei }}</div>
        <div v-if="row.last_seen"><strong>Última señal:</strong> {{ fechaCorta(row.last_seen) }}</div>
        <div v-if="row.sim_state === 'suspendido_temporal'" class="acc-warn">
          Suspendido temporal desde {{ fechaCorta(row.suspendido_desde) }}
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
            Limita el uso del SIM al IMEI que lo porta.
          </p>
          <label class="acc-hint">IMEI objetivo (equipo donde va el SIM)</label>
          <InputText v-model="lockTarget" placeholder="IMEI del equipo objetivo" />
          <Button label="1. Preparar (esperar señal del equipo)" icon="pi pi-sync" outlined
            :loading="busy==='preparar'" @click="accion('preparar')" />
          <p v-if="prepText" :class="['acc-hint', prepMatch ? 'acc-ok' : 'acc-warn']">{{ prepText }}</p>
          <Button label="2. Bloquear a este equipo" icon="pi pi-lock" outlined
            :loading="busy==='lock-on'" @click="accion('lock-on')" />
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

        <!-- Cancelación: oculto del front por ahora.
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
        -->

<!--         <div class="acc-card">
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
        </div> -->
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute, useRouter } from 'vue-router';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
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
  getEventosSim,
  refrescarRedSim,
  historialConsumoSim
} from '@/services/utilidadesImeiService';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const id = route.params.id;
const loading = ref(true);
const raw = ref(null);
const row = ref(null);
const busy = ref('');

const historial = ref([]);
const pausaFactura = ref(false);
const cancelarFecha = ref(''); // usado por la tarjeta de Cancelación (oculta)
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
}
.acc-loading {
  text-align: center;
  padding: 3rem;
  color: var(--color-text);
}
.acc-wrap h1 {
  margin: 0.75rem 0 1.25rem;
  color: var(--color-title);
}
.acc-card {
  background: var(--color-card);
  border: 1px solid var(--color-border);
  border-radius: 12px;
  padding: 1rem;
  display: flex;
  flex-direction: column;
  gap: 0.6rem;
}
.acc-card h3 {
  margin: 0 0 0.25rem;
  font-size: 0.8rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-title);
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 0.4rem;
}
.acc-card :deep(.p-button) { width: 100%; justify-content: center; }
.acc-card :deep(.p-inputtext) { width: 100%; }
.acc-info {
  display: grid;
  grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 0.55rem 1rem;
  margin-bottom: 1.25rem;
}
.acc-info > div { font-size: 0.85rem; color: var(--color-text); }
.acc-info strong { color: var(--color-title); font-weight: 600; }
.acc-grid {
  display: grid;
  grid-template-columns: repeat(2, 1fr);
  gap: 1rem;
  align-items: start;
}
@media (max-width: 760px) {
  .acc-grid { grid-template-columns: 1fr; }
}
.acc-warn { color: var(--color-error); font-weight: 600; }
.acc-ok { color: var(--color-success); font-weight: 600; }
.acc-hint { margin: 0; font-size: 0.8rem; color: var(--color-text); opacity: 0.7; }
.acc-check { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; color: var(--color-text); }
.acc-list { margin: 0.25rem 0 0; padding-left: 1.1rem; font-size: 0.82rem; color: var(--color-text); }
</style>
