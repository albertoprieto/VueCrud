<template>
  <div class="articulos-con-imeis">
    <h2>Stock por Artículo</h2>
    <div class="table-actions" style="margin-bottom:1rem; display:flex; justify-content:flex-end;">
      <InputText v-model="filtroNombre" placeholder="Filtrar por artículo..." class="p-inputtext-sm" style="max-width:250px;" />
    </div>
    <DataTable
      :value="articulosFiltrados"
      :sortField="sortField"
      :sortOrder="sortOrder"
      responsiveLayout="scroll"
      @sort="onSort"
    >
      <Column field="articulo_nombre" header="Artículo" sortable />
      <Column field="cantidad" header="Cantidad IMEIs" sortable />
      <Column header="Ver IMEIs">
        <template #body="slotProps">
          <Button label="Ver IMEIs" @click="verImeis(slotProps.data.articulo_nombre)" />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showImeisDialog" header="IMEIs Asociados" :modal="true" :closable="true">
      <DataTable :value="imeisSeleccionados" responsiveLayout="scroll">
        <Column field="imei" header="IMEI" />
        <Column field="status" header="Estado" />
        <Column field="registeredBy" header="Registró" />
        <Column field="date" header="Fecha" />
      </DataTable>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import { getIMEIs } from '@/services/imeiService';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';

const imeis = ref([]);
const showImeisDialog = ref(false);
const imeisSeleccionados = ref([]);
const filtroNombre = ref('');
const sortField = ref('articulo_nombre');
const sortOrder = ref(1);

const articulosAgrupados = computed(() => {
  const grupos = {};
  imeis.value.forEach(i => {
    if (!grupos[i.articulo_nombre]) {
      grupos[i.articulo_nombre] = [];
    }
    grupos[i.articulo_nombre].push(i);
  });
  return Object.entries(grupos).map(([articulo_nombre, imeisArr]) => ({
    articulo_nombre,
    cantidad: imeisArr.length,
    imeis: imeisArr
  }));
});

const articulosFiltrados = computed(() => {
  if (!filtroNombre.value) return articulosAgrupados.value;
  return articulosAgrupados.value.filter(a =>
    a.articulo_nombre?.toLowerCase().includes(filtroNombre.value.toLowerCase())
  );
});

const verImeis = (articulo_nombre) => {
  const grupo = articulosAgrupados.value.find(a => a.articulo_nombre === articulo_nombre);
  imeisSeleccionados.value = grupo ? grupo.imeis : [];
  showImeisDialog.value = true;
};

const onSort = (event) => {
  sortField.value = event.sortField;
  sortOrder.value = event.sortOrder;
};

const loadIMEIs = async () => {
  imeis.value = await getIMEIs();
};

onMounted(loadIMEIs);
</script>

<style scoped>
.articulos-con-imeis {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}
.table-actions {
  margin-bottom: 1rem;
}
</style>