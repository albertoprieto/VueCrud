<script setup>
import { ref, computed, onMounted } from 'vue';
import { getArticulos, getTodosArticulos, addArticulo, updateArticulo, deleteArticulo as deleteArticuloService } from '@/services/articulosService';
import { getIMEIs } from '@/services/imeiService';
import DataTable from 'primevue/datatable';
import DataTableLoader from '@/components/DataTableLoader.vue';
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
  codigo: '', // Opcional
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
    codigo: '', // Opcional
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
    
  //
  //
    
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
  <div class="articulos-page">
    <div class="articulos-header-card">
      <h2 class="mb-4 articulos-title">
        <i class="pi pi-database icon-accent"></i>
        Artículos
      </h2>
      <div class="articulos-actions">
        <Button label="Agregar Artículo" icon="pi pi-plus" @click="openModal" class="mb-3 articulos-btn" />
        <Button label="Exportar a Excel" icon="pi pi-file-excel" @click="exportToExcel" class="mb-3 articulos-btn" />
      </div>
    </div>
    <div class="articulos-table-card">
      <DataTable :value="filteredArticulos" :loading="loadingArticulos" paginator rows="10" :sortField="sortField" :sortOrder="sortOrder" class="datatable-responsive articulos-table">
        <template #loading>
          <DataTableLoader text="Cargando artículos..." />
        </template>
        <Column field="sku" header="SKU" :sortable="true" />
        <Column field="tipo" header="Tipo" :sortable="true" />
        <Column field="precioVenta" header="Precio Venta" :sortable="true" :body="formatoMoneda" />
        <Column field="precioCompra" header="Precio Compra" :sortable="true" :body="formatoMoneda" />
        <Column field="codigoSat" header="Código SAT" :sortable="true" />
        <Column field="codigoUnidadSat" header="Código Unidad SAT" :sortable="true" />
        <Column header="Acciones">
          <template #body="{ data }">
            <Button icon="pi pi-pencil" class="mr-2 articulos-btn" @click="() => handleEditArticulo(data)" />
            <Button icon="pi pi-trash" class="articulos-btn" @click="() => handleDeleteClick(data)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog header="Artículo" v-model:visible="showModal" :modal="true" :closeOnEscape="true" :dismissableMask="true" class="dialog-articulo dialog-articulo-amplio">
      <div class="dialog-articulo-content">
        <div class="dialog-articulo-header">
          <span class="dialog-articulo-title">
            <i class="pi pi-box icon-accent"></i>
            {{ form.id ? 'Editar artículo' : 'Nuevo artículo' }}
          </span>
        </div>
        <div class="dialog-articulo-sections">
          <div class="dialog-articulo-card">
            <div class="formgrid grid grid-responsive">
              <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="nombre"><i class="pi pi-tag icon-inline"></i>Nombre:</label>
                <InputText id="nombre" v-model="form.nombre" class="w-full" placeholder="Nombre del artículo" />
              </div>
              <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="sku"><i class="pi pi-barcode icon-inline"></i>SKU:</label>
                <InputText id="sku" v-model="form.sku" class="w-full" placeholder="SKU único" />
              </div>
              <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="tipo"><i class="pi pi-cog icon-inline"></i>Tipo:</label>
                <Dropdown id="tipo" v-model="form.tipo" :options="tipoOptions" optionLabel="label" optionValue="value" placeholder="Selecciona tipo" class="w-full" />
              </div>
              <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="precioVenta"><i class="pi pi-dollar icon-inline"></i>Precio Venta:</label>
                <InputText id="precioVenta" v-model.number="form.precioVenta" type="number" class="w-full" placeholder="Precio de venta" />
              </div>
              <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="precioCompra"><i class="pi pi-money-bill icon-inline"></i>Precio Compra:</label>
                <InputText id="precioCompra" v-model.number="form.precioCompra" type="number" class="w-full" placeholder="Precio de compra" />
              </div>
            </div>
          </div>
          <div class="dialog-articulo-card">
            <div class="formgrid grid grid-responsive">
              <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="codigoSat"><i class="pi pi-key icon-inline"></i>Código de artículo del SAT:</label>
                <InputText id="codigoSat" v-model="form.codigoSat" class="w-full" placeholder="Código de artículo del SAT" />
              </div>
              <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="unidadSat"><i class="pi pi-hashtag icon-inline"></i>Código de unidad del SAT:</label>
                <InputText id="unidadSat" v-model="form.codigoUnidadSat" class="w-full" placeholder="Código de unidad del SAT" />
              </div>
              <!-- <div class="field col-12 md:col-6 lg:col-6 xl:col-6">
                <label for="codigoUnidadSat"><i class="pi pi-hashtag" style="margin-right:0.3em;color:#ff4081"></i>Código Unidad SAT:</label>
                <InputText id="codigoUnidadSat" v-model="form.codigoUnidadSat" class="w-full" placeholder="Código Unidad SAT" />
              </div> -->
            </div>
          </div>
        </div>
      </div>
      <template #footer>
        <Button label="Cancelar" icon="pi pi-times" @click="closeModal" class="p-button-text" />
        <Button label="Guardar" icon="pi pi-check" @click="saveArticulo" class="p-button-success" />
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
.articulos-page {
  background: linear-gradient(135deg, var(--color-bg) 80%, color-mix(in oklab, var(--color-primary) 12%, var(--color-bg)) 100%);
  min-height: 100vh;
  padding: 2rem 0.5rem;
}
.articulos-header-card {
  background: var(--color-card);
  border-radius: 16px;
  box-shadow: var(--shadow-2);
  padding: 1.2rem 2rem 1rem 2rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.articulos-title {
  font-size: 2em;
  font-weight: 700;
  color: var(--color-primary, var(--color-title));
  display: flex;
  align-items: center;
  margin-bottom: 0.5em;
}
.articulos-actions {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 0.5em;
}
.articulos-btn {
  border-radius: 8px;
  font-weight: 500;
  box-shadow: var(--shadow-1);
  background: linear-gradient(90deg, var(--color-card) 60%, var(--color-card) 100%);
  color: var(--color-title);
}
.articulos-table-card {
  background: var(--color-card);
  border-radius: 16px;
  box-shadow: var(--shadow-2);
  padding: 1.2rem 1rem 1rem 1rem;
}
.articulos-table {
  font-size: 1em;
  border-radius: 12px;
  background: transparent;
}
.datatable-responsive {
  font-size: 0.95rem;
}

.dialog-articulo {
  min-width: 420px;
  max-width: 600px;
  border-radius: 16px;
  box-shadow: var(--shadow-3);
  background: linear-gradient(135deg, var(--color-card) 80%, color-mix(in oklab, var(--color-primary) 10%, var(--color-card)) 100%);
}
.dialog-articulo-content {
  padding: .1rem 0.7rem 0.5rem 0.7rem;
}
.dialog-articulo-header {
  text-align: left;
  margin-bottom: 1.2rem;
}
.dialog-articulo-title {
  font-size: 1.35em;
  font-weight: 600;
  color: var(--color-primary, var(--color-title));
  display: flex;
  align-items: center;
}
.dialog-articulo-sections {
  display: flex;
  flex-direction: column;
  gap: 0.7rem;
}
.dialog-articulo-card {
  background: var(--color-card);
  border-radius: 12px;
  box-shadow: var(--shadow-1);
  padding: 0.7rem 0.7rem 0.3rem 0.7rem;
  margin-bottom: 0.2rem;
}
.dialog-articulo-card label {
  font-weight: 500;
  color: var(--color-title);
  margin-bottom: 0.3em;
  display: block;
}
.icon-accent { color: var(--color-primary); font-size: 1.5em; margin-right: 0.5em; }
.icon-inline { color: var(--color-primary); margin-right: 0.3em; }
.dialog-articulo-card .pi {
  vertical-align: middle;
}
.dialog-articulo-card .w-full {
  margin-bottom: 0.3em;
}
@media (max-width: 700px) {
  .dialog-articulo {
    min-width: 90vw;
    max-width: 98vw;
    padding: 0.5rem;
  }
  .dialog-articulo-content {
    padding: 0.5rem 0.2rem;
  }
}

.dialog-articulo.dialog-articulo-amplio {
  min-width: 600px;
  max-width: 900px;
}
.grid-responsive {
  display: flex;
  flex-wrap: wrap;
  gap: 0.7rem 1.2rem;
}
.grid-responsive > .field {
  min-width: 220px;
  flex: 1 1 45%;
  margin-bottom: 0.2em;
}
@media (max-width: 900px) {
  .dialog-articulo.dialog-articulo-amplio {
    min-width: 98vw;
    max-width: 99vw;
  }
  .grid-responsive > .field {
    min-width: 100%;
    flex: 1 1 100%;
  }
}
</style>