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

    <div v-if="exito" style="color:var(--green-500, #27ae60); margin-bottom:1em;">
      {{ exito }}
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import { buscarDispositivosPlataforma } from '@/services/plataformasService';

const emit = defineEmits(['seleccionar', 'busqueda-resultado']);

const plataformaOpciones = [
  { label: 'IOP GPS', value: 'iop' },
  { label: 'Tracksolid', value: 'tracksolid' },
];

const plataformaSeleccionada = ref(null);
const queryBusqueda = ref('');
const buscando = ref(false);
const error = ref('');
const exito = ref('');

const aplanarResultadoIOP = (item) => {
  const flat = {};
  if (item.deviceStatus) Object.entries(item.deviceStatus).forEach(([k, v]) => flat[k] = v);
  if (item.deviceBrief) Object.entries(item.deviceBrief).forEach(([k, v]) => { if (!(k in flat)) flat[k] = v; });
  if (item.account) {
    flat._account = item.account.accountName || '';
    flat._userName = item.account.userName || '';
    flat._contactTel = item.account.contactTel || '';
    flat._email = item.account.email || '';
  }
  if (item.deviceBrief?.name && !flat.deviceName) flat.deviceName = item.deviceBrief.name;
  return flat;
};

const aplanarResultadoTracksolid = (item) => {
  // Mapear campos de Tracksolid al formato que esperan los componentes padres
  return {
    ...item,
    _userName: item.driverName || item._accountName || '',
    _contactTel: item.driverPhone || '',
    _email: '',
    address: '',
  };
};

const buscar = async () => {
  if (!plataformaSeleccionada.value || queryBusqueda.value.length < 2) return;
  buscando.value = true;
  error.value = '';
  exito.value = '';
  try {
    const data = await buscarDispositivosPlataforma(queryBusqueda.value, plataformaSeleccionada.value);
    let items = data.resultados || [];
    if (plataformaSeleccionada.value === 'iop') {
      items = items.map(aplanarResultadoIOP);
    } else if (plataformaSeleccionada.value === 'tracksolid') {
      items = items.map(aplanarResultadoTracksolid);
    }
    if (!items.length) {
      error.value = 'No se encontraron dispositivos con ese criterio.';
    } else {
      const primer = items[0];
      const nombre = primer.deviceName || primer.device_name || primer.imei || '';
      exito.value = `Dispositivo encontrado: ${primer.imei || ''} — ${nombre}`;
      emit('busqueda-resultado', {
        plataforma: plataformaSeleccionada.value,
        resultados: items,
      });
      emit('seleccionar', {
        plataforma: plataformaSeleccionada.value,
        dispositivo: primer,
      });
    }
  } catch (e) {
    error.value = e?.response?.data?.detail || e.message || 'Error al buscar';
  } finally {
    buscando.value = false;
  }
};
</script>

<style scoped>
.buscador-plataforma {
  border-radius: 8px;
  padding: 1rem;
  margin-bottom: 1.5rem;
}
</style>
