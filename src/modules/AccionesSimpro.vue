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
        <div><strong>Estado SIMPRO:</strong> {{ row.sim_customer_status || '—' }}</div>
        <div><strong>Vigencia:</strong> {{ row.vigencia_sim || '—' }}</div>
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
          <Button label="Bloquear a este equipo" icon="pi pi-lock" outlined :loading="busy==='lock-on'" @click="accion('lock-on')" />
          <Button label="Quitar bloqueo" icon="pi pi-lock-open" outlined :loading="busy==='lock-off'" @click="accion('lock-off')" />
        </div>

        <div class="acc-card">
          <h3>Pasar este SIM a otro equipo</h3>
          <p class="acc-hint">El SIM y su vigencia se quedan igual. Cambia solo el equipo (IMEI) al que está asignado. El registro queda como "Reutilizado".</p>
          <InputText v-model="reasignar.nuevoImei" placeholder="IMEI del equipo nuevo" />
          <Button label="Pasar a este equipo" icon="pi pi-arrow-right-arrow-left" severity="help"
            :disabled="!reasignar.nuevoImei" :loading="busy==='reasignar'" @click="accion('reasignar')" />
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
      </div>
    </div>
  </section>
</template>

<script setup>
import { ref, reactive, onMounted } from 'vue';
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
  refrescarRedSim,
  historialConsumoSim,
  swapIccidSim,
  reasignarSim
} from '@/services/utilidadesImeiService';

const route = useRoute();
const router = useRouter();
const toast = useToast();

const id = route.params.id;
const loading = ref(true);
const raw = ref(null);
const row = ref(null);
const busy = ref('');

const reasignar = reactive({ nuevoImei: '' });
const nuevoIccid = ref('');
const historial = ref([]);
const pausaFactura = ref(false);
const cancelarFecha = ref('');

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
    sin_trafico: !!r.sin_trafico
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
      ok(res.es_baja_en_simpro ? 'Estado actualizado. Figura dado de baja en SIMPRO.' : 'Estado actualizado.');
    } else if (a === 'consumo') {
      res = await verificarConsumoSim(id);
      ok('Consumo actualizado.');
    } else if (a === 'refrescar-red') {
      await refrescarRedSim(id);
      ok('Refresh de red enviado.');
    } else if (a === 'lock-on' || a === 'lock-off') {
      await imeiLockSim(id, a === 'lock-on');
      ok(a === 'lock-on' ? 'SIM bloqueado a este equipo.' : 'Bloqueo quitado.');
    } else if (a === 'swap') {
      if (!window.confirm('Esto cambia la tarjeta física en SIMPRO. ¿Continuar?')) { busy.value = ''; return; }
      res = await swapIccidSim(id, nuevoIccid.value.trim());
      ok('Tarjeta cambiada. El registro apunta al ICCID nuevo.');
    } else if (a === 'reasignar') {
      res = await reasignarSim(id, { nuevoImei: reasignar.nuevoImei.trim() });
      ok('SIM pasado al equipo nuevo (Reutilizado).' + (res.avisos?.length ? ' ' + res.avisos.join(' ') : ''));
    } else if (a === 'historial') {
      const data = await historialConsumoSim(id, 6);
      historial.value = (data.historial || []).map(h => ({
        mes: h.mes,
        resumen: h.error ? `error: ${h.error}` : resumenConsumoMes(h.datos)
      }));
      ok('Historial cargado.');
    } else if (a === 'suspender') {
      res = await suspenderSim(id, { pausarFacturacion: pausaFactura.value });
      ok(pausaFactura.value ? 'SIM suspendido y facturación pausada.' : 'SIM suspendido (tráfico bloqueado).');
    } else if (a === 'reactivar') {
      res = await reactivarSim(id);
      ok('SIM reactivado.');
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
.acc-hint { margin: 0; font-size: 0.8rem; opacity: 0.7; }
.acc-check { display: flex; align-items: center; gap: 0.4rem; font-size: 0.85rem; }
.acc-list { margin: 0.25rem 0 0; padding-left: 1.1rem; font-size: 0.82rem; }
.w-full { width: 100%; }
</style>
