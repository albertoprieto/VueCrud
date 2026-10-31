<template>
  <div>
    <h2 class="page-title">IMEIs en la bodega: {{ ubicacion?.nombre }}</h2>
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

    <div class="mb-2 filtros-adicionales" style="display: flex; gap: 1rem; align-items: center;">
      <InputText v-model="filtroImei" placeholder="Filtrar por IMEI o últimos 5 dígitos" class="p-inputtext-sm" />
      <Dropdown v-model="filtroSkuDropdown" :options="skuOptions" optionLabel="label" optionValue="value" placeholder="Filtrar por Artículo" class="p-inputtext-sm" showClear />
      <span v-if="filtroSkuDropdown" style="font-weight:bold; color:var(--color-primary);">Total: {{ totalSkuFiltrado }}</span>
      <Button label="Limpiar" icon="pi pi-times" class="p-button-secondary" @click="limpiarFiltros" />
    </div>

    <div v-if="seleccionados.length" class="mb-2 barra-transferir">
      <span>{{ seleccionados.length }} seleccionado{{ seleccionados.length === 1 ? '' : 's' }}</span>
      <Button label="Transferir" icon="pi pi-share-alt" @click="abrirTransferir" />
      <Button label="Quitar selección" class="p-button-text" @click="seleccionados = []" />
    </div>

    <DataTable v-model:selection="seleccionados" :value="imeisFiltrados" :loading="loading" dataKey="imei">
      <template #loading>
        <DataTableLoader text="Cargando IMEIs..." />
      </template>
      <Column selectionMode="multiple" style="width:3rem" />
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

    <Dialog v-model:visible="showTransferir" header="Transferir IMEIs" :modal="true" :style="{ width: '420px', maxWidth: '95vw' }" :draggable="false">
      <p style="margin-top:0;">{{ seleccionados.length }} IMEI{{ seleccionados.length === 1 ? '' : 's' }} de {{ ubicacion?.nombre }}</p>
      <Dropdown
        v-model="destino"
        :options="ubicacionesDestino"
        optionLabel="nombre"
        placeholder="Selecciona ubicación destino"
        filter
        autoFilterFocus
        filterPlaceholder="Escribe para buscar"
        emptyFilterMessage="Sin resultados"
        style="width:100%;"
      />
      <template #footer>
        <Button label="Cancelar" class="p-button-secondary" @click="showTransferir = false" />
        <Button label="Transferir" icon="pi pi-share-alt" :disabled="!destino" :loading="transfiriendo" @click="confirmarTransferir" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { useRoute } from 'vue-router';
import { getUbicaciones, getImeisPorUbicacion, transferirImeis } from '@/services/ubicacionesService';
import { devolverIMEI } from '@/services/imeiService';
import DataTable from 'primevue/datatable';
import DataTableLoader from '@/components/DataTableLoader.vue';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Chip from 'primevue/chip';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Dialog from 'primevue/dialog';
import { useToast } from 'primevue/usetoast';

const route = useRoute();
const toast = useToast();
const ubicaciones = ref([]);
const ubicacion = ref(null);
const imeis = ref([]);
const loading = ref(true);

const filtroStatus = ref(null);
const filtroImei = ref('');
const filtroArticulo = ref('');
const filtroSku = ref('');
const filtroSkuDropdown = ref(null);

const statusOptions = [
  { label: 'Todos', value: null },
  { label: 'Disponibles', value: 'Disponible' },
  { label: 'Vendidos', value: 'Vendido' },
  { label: 'Devueltos', value: 'Devuelto' }
];

const skuOptions = computed(() => {
  const skus = imeis.value.map(i => i.sku).filter(s => !!s);
  return Array.from(new Set(skus)).map(sku => ({ label: sku, value: sku }));
});

const cargarDatos = async () => {
  loading.value = true;
  ubicaciones.value = await getUbicaciones();
  ubicacion.value = ubicaciones.value.find(u => u.id == route.params.id);
  imeis.value = await getImeisPorUbicacion(route.params.id);
  loading.value = false;
};

const seleccionados = ref([]);
const showTransferir = ref(false);
const destino = ref(null);
const transfiriendo = ref(false);
const ubicacionesDestino = computed(() => ubicaciones.value.filter(u => u.id != route.params.id));

const abrirTransferir = () => {
  destino.value = null;
  showTransferir.value = true;
};

const confirmarTransferir = async () => {
  transfiriendo.value = true;
  try {
    const total = seleccionados.value.length;
    await transferirImeis(seleccionados.value.map(i => i.imei), destino.value.id);
    toast.add({ severity: 'success', summary: 'Transferidos', detail: `${total} IMEI(s) transferidos a "${destino.value.nombre}".`, life: 4000 });
    seleccionados.value = [];
    showTransferir.value = false;
    await cargarDatos();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudieron transferir los IMEIs.', life: 4500 });
  }
  transfiriendo.value = false;
};

const limpiarFiltros = () => {
  filtroImei.value = '';
  filtroArticulo.value = '';
  filtroSku.value = '';
  filtroSkuDropdown.value = null;
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
    // SKU Dropdown
    const skuDropdownOk = !filtroSkuDropdown.value || i.sku === filtroSkuDropdown.value;
    // SKU texto
    const skuOk = !filtroSku.value ||
      i.sku?.toLowerCase().includes(filtroSku.value.toLowerCase());
    return statusOk && imeiOk && articuloOk && skuDropdownOk && skuOk;
  });
});

const totalSkuFiltrado = computed(() => imeisFiltrados.value.length);

const marcarDevuelto = async (imei) => {
  await devolverIMEI(imei);
  await cargarDatos();
};

onMounted(cargarDatos);
</script>

<style scoped>
.barra-transferir {
  display: flex;
  gap: 1rem;
  align-items: center;
}
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
  color: var(--color-text);
}
.chip-devuelto {
  background: #ffe082;
  color: var(--color-text);
}
</style>