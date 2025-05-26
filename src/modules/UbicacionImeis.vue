<template>
  <div>
    <h2>IMEIs en la bodega: {{ ubicacion?.nombre }}</h2>
    <Button label="Volver" icon="pi pi-arrow-left" @click="$router.back()" class="mb-3" />
    <DataTable :value="imeis" :loading="loading">
      <Column field="imei" header="IMEI" />
      <Column field="articulo_nombre" header="Artículo" />
      <Column field="status" header="Estado">
        <template #body="slotProps">
          <span
            :class="{
              'status-disponible': slotProps.data.status === 'Disponible',
              'status-vendido': slotProps.data.status === 'Vendido',
              'status-otro': slotProps.data.status !== 'Disponible' && slotProps.data.status !== 'Vendido'
            }"
          >
            {{ slotProps.data.status }}
          </span>
        </template>
      </Column>
      <Column field="date" header="Fecha registro" />
      <Column field="registeredBy" header="Registró" />
      <Column field="technician" header="Técnico" />
    </DataTable>
    <h3>Asignar IMEIs a esta bodega</h3>
    <DataTable
      :value="imeisDisponibles"
      selectionMode="multiple"
      v-model:selection="seleccionados"
      dataKey="imei"
    >
      <Column field="imei" header="IMEI" />
      <Column field="articulo_nombre" header="Artículo" />
      <template #empty>
        <span>No hay IMEIs disponibles para asignar.</span>
      </template>
    </DataTable>
    <Button label="Asignar seleccionados" @click="asignarSeleccionados" :disabled="seleccionados.length === 0" />
    <h3>Transferir IMEIs a otra bodega</h3>
    <Dropdown v-model="bodegaDestino" :options="otrasUbicaciones" optionLabel="nombre" placeholder="Selecciona bodega destino" class="mb-2" />
    <DataTable
      :value="imeis"
      selectionMode="multiple"
      v-model:selection="imeisSeleccionados"
      dataKey="imei"
    >
      <Column field="imei" header="IMEI" />
      <Column field="articulo_nombre" header="Artículo" />
    </DataTable>
    <Button label="Transferir seleccionados" @click="transferirSeleccionados" :disabled="!bodegaDestino || imeisSeleccionados.length === 0" />
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getUbicaciones, getImeisPorUbicacion, asignarImeisUbicacion } from '@/services/ubicacionesService';
import { getIMEIs } from '@/services/imeiService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dropdown from 'primevue/dropdown';

const route = useRoute();
const ubicacion = ref(null);
const imeis = ref([]);
const imeisDisponibles = ref([]);
const seleccionados = ref([]);
const imeisSeleccionados = ref([]);
const bodegaDestino = ref(null);
const otrasUbicaciones = ref([]);
const loading = ref(true);

const cargarDatos = async () => {
  loading.value = true;
  const ubicaciones = await getUbicaciones();
  ubicacion.value = ubicaciones.find(u => u.id == route.params.id);
  imeis.value = await getImeisPorUbicacion(route.params.id);
  const todosImeis = await getIMEIs();
  // Solo mostrar IMEIs no asignados a ninguna bodega
  imeisDisponibles.value = todosImeis.filter(i => i.ubicacion_id === null);
  otrasUbicaciones.value = ubicaciones.filter(u => u.id != route.params.id);
  loading.value = false;
};

const asignarSeleccionados = async () => {
  await asignarImeisUbicacion(route.params.id, seleccionados.value.map(i => i.imei));
  seleccionados.value = [];
  await cargarDatos();
};

const transferirSeleccionados = async () => {
  await asignarImeisUbicacion(bodegaDestino.value.id, imeisSeleccionados.value.map(i => i.imei));
  imeisSeleccionados.value = [];
  bodegaDestino.value = null;
  await cargarDatos();
};

onMounted(cargarDatos);
</script>

<style>
.status-disponible {
  background: #e0f7fa;
  color: #00695c;
  font-weight: bold;
  border-radius: 6px;
  padding: 0.2em 0.7em;
  display: inline-block;
}

.status-vendido {
  background: #ffdde1;
  color: #b71c1c;
  font-weight: bold;
  border-radius: 6px;
  padding: 0.2em 0.7em;
  display: inline-block;
}

.status-otro {
  background: #ffe082;
  color: #795548;
  font-weight: bold;
  border-radius: 6px;
  padding: 0.2em 0.7em;
  display: inline-block;
}
</style>