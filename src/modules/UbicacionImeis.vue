<template>
  <div>
    <h2>IMEIs en la bodega: {{ ubicacion?.nombre }}</h2>
    <Button label="Volver" icon="pi pi-arrow-left" @click="$router.back()" class="mb-3" />

    <div class="mb-2 filtro-chips">
      <Chip
        v-for="option in statusOptions"
        :key="option.value"
        :label="option.label"
        :class="[
          'chip-filtro',
          { 'chip-activo': filtroStatus === option.value },
          option.value === 'Disponible' ? 'chip-disponible' : option.value === 'Vendido' ? 'chip-vendido' : 'chip-todos'
        ]"
        @click="filtroStatus = option.value"
      />
    </div>

    <div class="mb-2 filtros-adicionales" style="display: flex; gap: 1rem;">
      <InputText v-model="filtroImei" placeholder="Filtrar por IMEI o últimos 5 dígitos" class="p-inputtext-sm" />
      <InputText v-model="filtroArticulo" placeholder="Filtrar por artículo" class="p-inputtext-sm" />
      <InputText v-model="filtroSku" placeholder="Filtrar por SKU" class="p-inputtext-sm" />
      <Button label="Limpiar" icon="pi pi-times" class="p-button-secondary" @click="limpiarFiltros" />
    </div>

    <DataTable :value="imeisFiltrados" :loading="loading">
      <template #loading>
        <DataTableLoader text="Cargando IMEIs..." />
      </template>
      <Column field="imei" header="IMEI" />
      <!-- <Column field="articulo_nombre" header="Artículo" /> -->
      <Column field="sku" header="SKU" />
      <Column field="status" header="Estado">
        <template #body="slotProps">
          <Chip
            :label="slotProps.data.status"
            :class="[
              slotProps.data.status === 'Vendido' ? 'chip-vendido' :
              slotProps.data.status === 'Devuelto' ? 'chip-devuelto' : 'chip-otro'
            ]"
          />
        </template>
      </Column>
      <Column field="date" header="Fecha registro" />
      <!-- <Column field="registeredBy" header="Registró" /> -->
    </DataTable>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getUbicaciones, getImeisPorUbicacion } from '@/services/ubicacionesService';
import { devolverIMEI } from '@/services/imeiService';
import DataTable from 'primevue/datatable';
import DataTableLoader from '@/components/DataTableLoader.vue';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import InputText from 'primevue/inputtext';

const route = useRoute();
const ubicacion = ref(null);
const imeis = ref([]);
const loading = ref(true);

const filtroStatus = ref(null);
const filtroImei = ref('');
const filtroArticulo = ref('');
const filtroSku = ref('');

const statusOptions = [
  { label: 'Todos', value: null },
  { label: 'Disponibles', value: 'Disponible' },
  { label: 'Vendidos', value: 'Vendido' },
  { label: 'Devueltos', value: 'Devuelto' }
];

const cargarDatos = async () => {
  loading.value = true;
  const ubicaciones = await getUbicaciones();
  ubicacion.value = ubicaciones.find(u => u.id == route.params.id);
  imeis.value = await getImeisPorUbicacion(route.params.id);
  loading.value = false;
};

const limpiarFiltros = () => {
  filtroImei.value = '';
  filtroArticulo.value = '';
  filtroSku.value = '';
};

const imeisFiltrados = computed(() => {
  return imeis.value.filter(i => {
    // Status
    const statusOk = !filtroStatus.value || i.status === filtroStatus.value;
    // IMEI o últimos 5 dígitos
    const imeiOk = !filtroImei.value ||
      i.imei?.toLowerCase().includes(filtroImei.value.toLowerCase()) ||
      i.imei?.slice(-5).includes(filtroImei.value);
    // Artículo
    const articuloOk = !filtroArticulo.value ||
      i.articulo_nombre?.toLowerCase().includes(filtroArticulo.value.toLowerCase());
    // SKU
    const skuOk = !filtroSku.value ||
      i.sku?.toLowerCase().includes(filtroSku.value.toLowerCase());
    return statusOk && imeiOk && articuloOk && skuOk;
  });
});

const marcarDevuelto = async (imei) => {
  await devolverIMEI(imei);
  await cargarDatos();
};

onMounted(cargarDatos);
</script>

<style scoped>
.filtro-chips {
  display: flex;
  gap: 0.5rem;
  margin-bottom: 1rem;
}
.chip-filtro {
  cursor: pointer;
  font-weight: bold;
  opacity: 0.7;
  transition: opacity 0.2s, box-shadow 0.2s;
  border-radius: 16px;
  font-size: 1em;
}
.chip-activo {
  opacity: 1;
  box-shadow: 0 2px 8px rgba(0,0,0,0.10);
}
.chip-disponible {
  background: linear-gradient(90deg, #e0f7fa 0%, #b2ebf2 100%);
  color: #00695c;
}
.chip-vendido {
  background: linear-gradient(90deg, #ffdde1 0%, #ee9ca7 100%);
  color: #b71c1c;
}
.chip-todos {
  background: #ececec;
  color: #444;
}
.chip-otro {
  background: #ffe082;
  color: #795548;
}
.chip-devuelto {
  background: #ffe082;
  color: #795548;
}
</style>