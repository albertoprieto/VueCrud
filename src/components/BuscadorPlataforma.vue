<template>
  <div class="buscador-plataforma">
    <h4 style="font-size:1.1em; font-weight:bold; margin-bottom:0.8em;">
      Buscar en plataforma (opcional)
    </h4>
    <div style="display:flex; gap:1em; align-items:flex-end; flex-wrap:wrap; margin-bottom:1em;">
      <div style="flex:0 0 160px; display:flex; flex-direction:column;">
        <label>Plataforma</label>
        <Dropdown v-model="plataformaSeleccionada" :options="plataformaOpciones"
          optionLabel="label" optionValue="value" placeholder="Selecciona" class="w-full" />
      </div>
      <div style="flex:1; min-width:200px; display:flex; flex-direction:column;">
        <label>Buscar (IMEI, nombre o cuenta)</label>
        <InputText v-model="queryBusqueda" class="w-full" placeholder="Ej: 352484093054353"
          @keyup.enter="buscar" />
      </div>
      <Button label="Buscar" icon="pi pi-search" class="p-button-outlined"
        @click="buscar" :loading="buscando" :disabled="!plataformaSeleccionada || queryBusqueda.length < 2" />
    </div>

    <div v-if="error" style="color:var(--red-500, #e74c3c); margin-bottom:1em;">
      {{ error }}
    </div>

    <div v-if="resultados.length" style="margin-bottom:1em;">
      <label style="font-weight:500;">Resultados ({{ resultados.length }})</label>
      <Dropdown v-model="dispositivoSeleccionado" :options="resultados"
        :optionLabel="formatLabel" placeholder="Selecciona un dispositivo" class="w-full"
        filter :filterPlaceholder="'Filtrar resultados...'" @change="onSeleccionar" />
    </div>

    <!-- Mostrar response raw del dispositivo seleccionado para mapeo manual -->
    <div v-if="dispositivoSeleccionado" class="device-detail-card">
      <div style="display:flex; justify-content:space-between; align-items:center; margin-bottom:0.5em;">
        <strong>Datos del dispositivo seleccionado</strong>
        <Button label="Usar estos datos" icon="pi pi-check" class="p-button-sm p-button-success"
          @click="aplicarDatos" />
      </div>
      <div class="device-fields-grid">
        <div v-for="(valor, llave) in camposMostrar" :key="llave" class="device-field-item">
          <span class="device-field-key">{{ llave }}</span>
          <span class="device-field-value">{{ valor ?? '—' }}</span>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref, computed } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { buscarDispositivosPlataforma } from '@/services/plataformasService';

const emit = defineEmits(['seleccionar']);

const plataformaOpciones = [
  { label: 'IOP GPS', value: 'iop' },
  { label: 'Tracksolid', value: 'tracksolid' },
];

const plataformaSeleccionada = ref(null);
const queryBusqueda = ref('');
const resultados = ref([]);
const dispositivoSeleccionado = ref(null);
const buscando = ref(false);
const error = ref('');

const formatLabel = (item) => {
  const imei = item.imei || item.IMEI || 'Sin IMEI';
  const name = item.deviceName || item.device_name || 'Sin nombre';
  const acc = item._account || item._userName || item._accountName || '';
  return `${imei} — ${name}${acc ? ` (${acc})` : ''}`;
};

const camposMostrar = computed(() => {
  if (!dispositivoSeleccionado.value) return {};
  const dev = { ...dispositivoSeleccionado.value };
  // Excluir campos internos muy largos o no útiles visualmente
  const excluir = ['__ob__', '_rawData'];
  const resultado = {};
  for (const [k, v] of Object.entries(dev)) {
    if (excluir.includes(k)) continue;
    if (typeof v === 'object' && v !== null) {
      resultado[k] = JSON.stringify(v);
    } else {
      resultado[k] = v;
    }
  }
  return resultado;
});

const aplanarResultadoIOP = (item) => {
  // IOP devuelve { deviceStatus: {...}, deviceBrief: {...}, account: {...} }
  // Aplanamos todo a un solo objeto para que formatLabel y camposMostrar funcionen
  const flat = {};
  if (item.deviceStatus) Object.entries(item.deviceStatus).forEach(([k, v]) => flat[k] = v);
  if (item.deviceBrief) Object.entries(item.deviceBrief).forEach(([k, v]) => { if (!(k in flat)) flat[k] = v; });
  if (item.account) {
    flat._account = item.account.accountName || '';
    flat._userName = item.account.userName || '';
    flat._contactTel = item.account.contactTel || '';
    flat._email = item.account.email || '';
  }
  // Renombrar 'name' de deviceBrief a 'deviceName' para que formatLabel lo encuentre
  if (item.deviceBrief?.name && !flat.deviceName) flat.deviceName = item.deviceBrief.name;
  return flat;
};

const buscar = async () => {
  if (!plataformaSeleccionada.value || queryBusqueda.value.length < 2) return;
  buscando.value = true;
  error.value = '';
  resultados.value = [];
  dispositivoSeleccionado.value = null;
  try {
    const data = await buscarDispositivosPlataforma(queryBusqueda.value, plataformaSeleccionada.value);
    let items = data.resultados || [];
    if (plataformaSeleccionada.value === 'iop') {
      items = items.map(aplanarResultadoIOP);
    }
    resultados.value = items;
    if (!resultados.value.length) {
      error.value = 'No se encontraron dispositivos con ese criterio.';
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Error al buscar';
  } finally {
    buscando.value = false;
  }
};

const onSeleccionar = () => {
  // El usuario puede ver los datos primero antes de aplicar
};

const aplicarDatos = () => {
  if (!dispositivoSeleccionado.value) return;
  emit('seleccionar', {
    plataforma: plataformaSeleccionada.value,
    dispositivo: dispositivoSeleccionado.value,
  });
};
</script>

<style scoped>
.buscador-plataforma {

  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;

}

.device-detail-card {

  border-radius: 6px;
  padding: 0.8rem;

  margin-top: 0.5em;
}

.device-fields-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 0.4rem 1.5rem;
  max-height: 300px;
  overflow-y: auto;
}

.device-field-item {
  display: flex;
  flex-direction: column;
  padding: 0.2rem 0;
}

.device-field-key {
  font-size: 0.78em;
  font-weight: 600;
}

.device-field-value {
  font-size: 0.92em;
  word-break: break-all;
}
</style>
