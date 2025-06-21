<script setup>
import { ref, computed, onMounted } from 'vue';
import { getTodosArticulos, addArticulo, updateArticulo, deleteArticulo as deleteArticuloService } from '@/services/articulosService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const articulos = ref([]);
const loadingArticulos = ref(true);
const showModal = ref(false);
const form = ref({
  id: null,
  sku: '',
  nombre: '',
  tipo: '',
  precioVenta: '',
  precioCompra: '',
  codigoSat: '',
  codigoUnidadSat: '',
  impuesto: '16%',
});
const search = ref('');
const showConfirmDelete = ref(false);
const articuloToDelete = ref(null);

const tipoOptions = [
  { label: 'Bien', value: 'Bien' },
  { label: 'Servicio', value: 'Servicio' }
];

const loadArticulos = async () => {
  loadingArticulos.value = true;
  try {
    articulos.value = await getTodosArticulos();
  } finally {
    loadingArticulos.value = false;
  }
};
onMounted(loadArticulos);

const filteredArticulos = computed(() => {
  if (!search.value) return articulos.value;
  return articulos.value.filter(a =>
    a.nombre?.toLowerCase().includes(search.value.toLowerCase()) ||
    a.sku?.toLowerCase().includes(search.value.toLowerCase()) ||
    a.descripcion?.toLowerCase().includes(search.value.toLowerCase())
  );
});

const openModal = (articulo = null) => {
  if (articulo) {
    form.value = {
      id: articulo.id,
      sku: articulo.sku,
      nombre: articulo.nombre,
      tipo: articulo.tipo,
      precioVenta: articulo.precioVenta,
      precioCompra: articulo.precioCompra,
      codigoSat: articulo.codigoSat,
      codigoUnidadSat: articulo.codigoUnidadSat,
      impuesto: articulo.impuesto || '16%',
    };
  } else {
    form.value = {
      id: null,
      sku: '',
      nombre: '',
      tipo: '',
      precioVenta: '',
      precioCompra: '',
      codigoSat: '',
      codigoUnidadSat: '',
      impuesto: '16%',
    };
  }
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveArticulo = async () => {
  if (!form.value.nombre || !form.value.sku) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Por favor, complete los campos obligatorios.', life: 4000 });
    return;
  }
  try {
    const articuloPayload = {
      sku: form.value.sku,
      nombre: form.value.nombre,
      tipo: form.value.tipo,
      precioVenta: Number(form.value.precioVenta) || 0,
      precioCompra: Number(form.value.precioCompra) || 0,
      codigoSat: form.value.codigoSat,
      codigoUnidadSat: form.value.codigoUnidadSat,
      impuesto: form.value.impuesto || '16%',
    };
    if (form.value.id) {
      await updateArticulo({
        id: form.value.id,
        ...articuloPayload
      });
      toast.add({ severity: 'success', summary: 'Artículo actualizado', life: 3000 });
    } else {
      await addArticulo(articuloPayload);
      toast.add({ severity: 'success', summary: 'Artículo agregado', life: 3000 });
    }
    closeModal();
    await loadArticulos();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error al guardar artículo', detail: error.message, life: 5000 });
  }
};

const confirmDelete = (articulo) => {
  articuloToDelete.value = articulo;
  showConfirmDelete.value = true;
};

const deleteArticulo = async () => {
  if (!articuloToDelete.value || !articuloToDelete.value.id) return;
  try {
    await deleteArticuloService(articuloToDelete.value.id);
    toast.add({ severity: 'success', summary: 'Artículo eliminado', life: 3000 });
    await loadArticulos();
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error al eliminar artículo', detail: error.message, life: 5000 });
  } finally {
    showConfirmDelete.value = false;
  }
};
</script>

<template>
  <div>
    <Button label="Agregar Artículo" icon="pi pi-plus" @click="() => openModal()" class="mb-3" />
    <InputText v-model="search" placeholder="Buscar artículo..." class="mb-3" />
    <DataTable :value="filteredArticulos" :loading="loadingArticulos" paginator rows="10" class="datatable-responsive">
      <Column field="sku" header="SKU" :sortable="true" />
      <Column field="nombre" header="Nombre" :sortable="true" />
      <Column field="tipo" header="Tipo" :sortable="true" />
      <Column field="precioVenta" header="Precio Venta" :sortable="true" />
      <Column field="precioCompra" header="Precio Compra" :sortable="true" />
      <Column field="codigoSat" header="Código SAT" :sortable="true" />
      <Column field="codigoUnidadSat" header="Código Unidad SAT" :sortable="true" />
      <Column header="Acciones">
        <template #body="{ data }">
          <Button icon="pi pi-pencil" class="mr-2" @click="() => openModal(data)" />
          <Button icon="pi pi-trash" @click="() => confirmDelete(data)" />
        </template>
      </Column>
    </DataTable>

    <Dialog header="Artículo" v-model:visible="showModal" :modal="true">
      <div class="p-fluid">
        <div class="formgrid grid">
          <div class="field col-12 md:col-6">
            <label for="sku">SKU:</label>
            <InputText id="sku" v-model="form.sku" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="nombre">Nombre:</label>
            <InputText id="nombre" v-model="form.nombre" class="w-full" />
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
            <label for="codigoUnidadSat">Código Unidad SAT:</label>
            <InputText id="codigoUnidadSat" v-model="form.codigoUnidadSat" class="w-full" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="impuesto">IVA:</label>
            <InputText id="impuesto" v-model="form.impuesto" class="w-full" disabled />
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" icon="pi pi-times" @click="closeModal" class="p-button-text" />
        <Button label="Guardar" icon="pi pi-check" @click="saveArticulo" />
      </template>
    </Dialog>

    <Dialog header="Confirmar eliminación" v-model:visible="showConfirmDelete" :modal="true">
      <div>
        <p>¿Estás seguro de que deseas eliminar este artículo?</p>
      </div>
      <template #footer>
        <Button label="Cancelar" icon="pi pi-times" @click="() => showConfirmDelete = false" class="p-button-text" />
        <Button label="Eliminar" icon="pi pi-check" @click="deleteArticulo" />
      </template>
    </Dialog>
  </div>
</template>

<style scoped>
.datatable-responsive {
  font-size: 0.875rem;
}
</style>