<script setup>
import { ref, computed, onMounted } from 'vue';
import { getArticulos, getTodosArticulos, addArticulo, updateArticulo, deleteArticulo as deleteArticuloService } from '@/services/articulosService';
import { getIMEIs } from '@/services/imeiService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import * as XLSX from 'xlsx';

import { useToast } from 'primevue/usetoast';

const toast = useToast();

const articulos = ref([]);
const imeis = ref([]);
const loadingArticulos = ref(true);
const showModal = ref(false);
const form = ref({
  id: null,
  codigo: '',
  nombre: '',
  sku: '',
  tipo: '',
  precioVenta: '',
  precioCompra: '',
  codigoSat: '',
  codigoUnidadSat: '',
  unidadSat: '',
});
const tipoOptions = [
  { label: 'Bien', value: 'Bien' },
  { label: 'Servicio', value: 'Servicio' }
];
const search = ref('');
const sortField = ref('nombre');
const sortOrder = ref(1);

const showErrorDialog = ref(false);
const errorMessage = ref('');
const showConfirmDelete = ref(false);
const articuloToDelete = ref(null);

const loadArticulos = async () => {
  loadingArticulos.value = true;
  try {
    articulos.value = await getTodosArticulos();
    imeis.value = await getIMEIs();
  } finally {
    loadingArticulos.value = false;
  }
};
onMounted(loadArticulos);

// Agrupa los imeis por artículo y calcula vendidos y total vendido
const resumenArticulos = computed(() => {
  const grupos = {};
  imeis.value.forEach(i => {
    if (!grupos[i.articulo_nombre]) grupos[i.articulo_nombre] = [];
    grupos[i.articulo_nombre].push(i);
  });
  return articulos.value.map(art => {
    const imeisArr = grupos[art.nombre] || [];
    const existencias = imeisArr.filter(i => i.status === 'Disponible').length;
    const precio = Number(art.precioVenta) || 0;
    return {
      ...art,
      existencias,
      // Elimina vendidos y totalVendido
    };
  });
});

// Formato moneda MXN
const formatoMoneda = (valor) => {
  return new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' }).format(Number(valor) || 0);
};

const filteredArticulos = computed(() => {
  if (!search.value) return resumenArticulos.value;
  return resumenArticulos.value.filter(a =>
    a.nombre?.toLowerCase().includes(search.value.toLowerCase()) ||
    a.sku?.toLowerCase().includes(search.value.toLowerCase())
    // Quita la búsqueda por descripción
  );
});

const openModal = () => {
  form.value = {
    id: null,
    codigo: '',
    nombre: '',
    sku: '',
    tipo: '',
    precioVenta: '',
    precioCompra: '',
    codigoSat: '',
    codigoUnidadSat: '',
    unidadSat: '',
  };
  showModal.value = true;
};

const editArticulo = (data) => {
  form.value = {
    id: data.id,
    codigo: data.codigo || '',
    nombre: data.nombre || '',
    sku: data.sku || '',
    tipo: data.tipo || '',
    precioVenta: data.precioVenta || '',
    precioCompra: data.precioCompra || '',
    codigoSat: data.codigoSat || '',
    codigoUnidadSat: data.codigoUnidadSat || '',
    unidadSat: data.unidadSat || '',
  };
  showModal.value = true;
};

// Refuerza el click de editar para nunca asignar booleanos
function handleEditArticulo(data) {
  if (typeof form.value !== 'object' || form.value === null) {
    form.value = { id: null, sku: '', nombre: '', tipo: '', precioVenta: '', precioCompra: '', codigoSat: '', codigoUnidadSat: '' };
  }
  Object.assign(form.value, data);
  // Refuerzo: si no hay id, no permitas editar
  if (!form.value.id) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'El artículo no tiene ID válido para editar.', life: 4000 });
    showModal.value = false;
    return;
  }
  showModal.value = true;
}

const closeModal = () => {
  showModal.value = false;
  // Nunca reasignes form.value a false ni a booleanos
};

const saveArticulo = async () => {
  if (!form.value.nombre || !form.value.sku) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Por favor, complete los campos obligatorios.', life: 4000 });
    errorMessage.value = 'Por favor, complete los campos obligatorios.';
    showErrorDialog.value = true;
    return;
  }
  try {
    const articuloPayload = {
      id: form.value.id ?? null, // requerido por el backend
      codigo: form.value.codigo || '',
      nombre: form.value.nombre || '',
      sku: form.value.sku || '',
      tipo: form.value.tipo || '',
      precioVenta: Number(form.value.precioVenta) || 0,
      precioCompra: Number(form.value.precioCompra) || 0,
      codigoSat: form.value.codigoSat || '',
      codigoUnidadSat: form.value.codigoUnidadSat || '',
      unidadSat: form.value.unidadSat || '',
      stock: 0, // requerido por el backend
      ubicacion_id: null, // requerido por el backend, null si no hay valor
      pagina: '',
      unidad: '',
      impuesto: '',
      descripcion: '',
    };
    
    console.log('Form ID antes de enviar:', form.value.id);
    console.log('Payload a enviar:', articuloPayload);
    
    if (form.value.id) {
      await updateArticulo(form.value.id, articuloPayload);
      toast.add({ severity: 'success', summary: 'Artículo actualizado', life: 3000 });
    } else {
      await addArticulo(articuloPayload);
      toast.add({ severity: 'success', summary: 'Artículo agregado', life: 3000 });
    }
    closeModal();
    loadArticulos();
  } catch (error) {
    let backendMsg = '';
    if (error.response && error.response.data) {
      backendMsg = typeof error.response.data === 'string' ? error.response.data : JSON.stringify(error.response.data);
    } else if (error.message) {
      backendMsg = error.message;
    } else {
      backendMsg = 'Error desconocido';
    }
    console.error('Error completo:', error);
    toast.add({ severity: 'error', summary: 'Error al guardar artículo', detail: backendMsg, life: 8000 });
    errorMessage.value = backendMsg;
    showErrorDialog.value = true;
  }
};

// Nueva función para manejar el click de eliminar
const handleDeleteClick = (data) => {
  if (data) {
    articuloToDelete.value = data;
    showConfirmDelete.value = true;
  }
};

const deleteArticulo = async () => {
  if (!articuloToDelete.value || !articuloToDelete.value.id) return;
  try {
    await deleteArticuloService(articuloToDelete.value.id);
    toast.add({ severity: 'success', summary: 'Artículo eliminado', life: 3000 });
    loadArticulos();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error al eliminar artículo', detail: error.message, life: 5000 });
  } finally {
    showConfirmDelete.value = false;
    articuloToDelete.value = null;
  }
};

// Exportar a Excel
const exportToExcel = () => {
  const ws = XLSX.utils.json_to_sheet(resumenArticulos.value);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Articulos');
  const fileName = `reporte_articulos_${new Date().toISOString().slice(0, 10)}.xlsx`;
  XLSX.writeFile(wb, fileName);
};

// Elimina todo lo relacionado con ubicaciones
// const ubicaciones = ref([]);
// const loadUbicaciones = async () => { ... };
// onMounted(() => { loadArticulos(); loadUbicaciones(); });

</script>

<template>
  <div>
    
    <h2 class="mb-4">Artículos</h2>
    <Button label="Agregar Artículo" icon="pi pi-plus" @click="openModal" class="mb-3" />
    <Button label="Exportar a Excel" icon="pi pi-file-excel" @click="exportToExcel" class="mb-3" />
    <DataTable :value="filteredArticulos" :loading="loadingArticulos" paginator rows="10" :sortField="sortField" :sortOrder="sortOrder" class="datatable-responsive">
      <Column field="codigo" header="Código" :sortable="true" />
      <!-- <Column field="nombre" header="Nombre" :sortable="true" /> -->
      <Column field="sku" header="SKU" :sortable="true" />
      <Column field="tipo" header="Tipo" :sortable="true" />
      <Column field="precioVenta" header="Precio Venta" :sortable="true" :body="formatoMoneda" />
      <Column field="precioCompra" header="Precio Compra" :sortable="true" :body="formatoMoneda" />
      <Column field="codigoSat" header="Código SAT" :sortable="true" />
      <Column field="codigoUnidadSat" header="Código Unidad SAT" :sortable="true" />
      <Column header="Acciones">
        <template #body="{ data }">
          <Button icon="pi pi-pencil" class="mr-2" @click="() => handleEditArticulo(data)" />
          <Button icon="pi pi-trash" @click="() => { articuloToDelete.value = data; showConfirmDelete.value = true; }" />
        </template>
      </Column>
    </DataTable>

    <Dialog header="Artículo" v-model:visible="showModal" :modal="true" :closeOnEscape="true" :dismissableMask="true">
      <div class="p-fluid">
        <div class="formgrid grid">
          <div class="field col-12 md:col-6">
            <label for="codigo">Código:</label>
            <InputText id="codigo" v-model="form.codigo" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="nombre">Nombre:</label>
            <InputText id="nombre" v-model="form.nombre" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="sku">SKU:</label>
            <InputText id="sku" v-model="form.sku" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="tipo">Tipo:</label>
            <Dropdown id="tipo" v-model="form.tipo" :options="tipoOptions" optionLabel="label" optionValue="value" placeholder="Selecciona tipo" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="precioVenta">Precio Venta:</label>
            <InputText id="precioVenta" v-model.number="form.precioVenta" type="number" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="precioCompra">Precio Compra:</label>
            <InputText id="precioCompra" v-model.number="form.precioCompra" type="number" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="codigoSat">Código SAT:</label>
            <InputText id="codigoSat" v-model="form.codigoSat" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="unidadSat">Unidad SAT:</label>
            <InputText id="unidadSat" v-model="form.unidadSat" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="codigoUnidadSat">Código Unidad SAT:</label>
            <InputText id="codigoUnidadSat" v-model="form.codigoUnidadSat" class="w-full" />
          </div>
        </div>
        <!-- Ubicación eliminada -->
        <!--
        <div class="form-group">
          <label for="ubicacion_id">Ubicación:</label>
          <Dropdown id="ubicacion_id" v-model="form.ubicacion_id" :options="ubicaciones" optionLabel="nombre" optionValue="id" placeholder="Selecciona ubicación" class="w-full" />
        </div>
        -->
      </div>
      <template #footer>
        <Button label="Cancelar" icon="pi pi-times" @click="closeModal" class="p-button-text" />
        <Button label="Guardar" icon="pi pi-check" @click="saveArticulo" />
      </template>
    </Dialog>

    <Dialog header="Confirmar eliminación" v-model:visible="showConfirmDelete" :modal="true" :closeOnEscape="true" :dismissableMask="true">
      <div>
        <p>¿Estás seguro de que deseas eliminar este artículo?</p>
      </div>
      <template #footer>
        <Button label="Cancelar" icon="pi pi-times" @click="() => showConfirmDelete.value = false" class="p-button-text" />
        <Button label="Eliminar" icon="pi pi-check" @click="deleteArticulo" />
      </template>
    </Dialog>

    <Dialog header="Error" v-model:visible="showErrorDialog" :modal="true" :closeOnEscape="true" :dismissableMask="true">
      <div>
        <p>{{ errorMessage }}</p>
      </div>
      <template #footer>
        <Button label="Cerrar" icon="pi pi-times" @click="() => showErrorDialog.value = false" class="p-button-text" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.datatable-responsive {
  font-size: 0.875rem;
}

.form-group {
  padding-bottom: 1rem;
}

.form-row,
.form-section {
  padding: 0.5rem 0;
}

.p-dialog .p-dialog-content,
.p-dialog .p-dialog-footer {
  padding: 1.5rem !important;
}

.reporte-servicio-container,
.articulos-imeis-card,
.clientes-card,
.ventas-card {
  padding: 2rem 1.5rem;
}
</style>