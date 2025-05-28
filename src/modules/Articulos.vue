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
import { saveAs } from 'file-saver';

const articulos = ref([]);
const imeis = ref([]);
const loadingArticulos = ref(true);
const showModal = ref(false);
const form = ref({
  id: null,
  sku: '',
  nombre: '',
  descripcion: '',
  tipo: '',
  precioVenta: '',
  unidad: '',
  impuesto: '',
  precioCompra: '',
  codigoSat: '',
  unidadSat: '',
  codigoUnidadSat: ''
});
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
    articulos.value = await getTodosArticulos(); // <-- Cambia aquí
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
    a.sku?.toLowerCase().includes(search.value.toLowerCase()) ||
    a.descripcion?.toLowerCase().includes(search.value.toLowerCase())
  );
});

const openModal = () => {
  form.value = { id: null, sku: '', nombre: '', descripcion: '', tipo: '', precioVenta: '', unidad: '', impuesto: '' };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveArticulo = async () => {
  if (!form.value.nombre || !form.value.sku) {
    errorMessage.value = 'Por favor, complete los campos obligatorios.';
    showErrorDialog.value = true;
    return;
  }
  try {
    const articuloPayload = {
      ...form.value,
      codigo: form.value.codigo ?? '',
      pagina: form.value.pagina ?? ''
    };
    if (form.value.id) {
      await updateArticulo(articuloPayload);
    } else {
      await addArticulo(articuloPayload);
    }
    showModal.value = false;
    await loadArticulos();
  } catch (e) {
    errorMessage.value = 'Error al guardar el artículo.';
    showErrorDialog.value = true;
  }
};

const editArticulo = (articulo) => {
  form.value = { ...articulo };
  showModal.value = true;
};

const confirmDeleteArticulo = (id) => {
  articuloToDelete.value = id;
  showConfirmDelete.value = true;
};

const deleteArticulo = async (id) => {
  try {
    await deleteArticuloService(id);
    await loadArticulos();
    showConfirmDelete.value = false;
  } catch (e) {
    errorMessage.value = 'Error al eliminar el artículo.';
    showErrorDialog.value = true;
  }
};

const exportarArticulos = () => {
  const mxn = new Intl.NumberFormat('es-MX', { style: 'currency', currency: 'MXN' });
  const data = resumenArticulos.value.map(art => ({
    'Artículo': art.nombre,
    'SKU': art.sku,
    'Tipo': art.tipo,
    'Unidad': art.unidad,
    'Precio de venta': mxn.format(art.precioVenta),
    'Existencias en mano': art.existencias,
    'Vendidos': art.vendidos,
    'Total inventario': mxn.format(art.precioVenta * art.existencias),
    'Total vendidos (MXN)': mxn.format(art.totalVendido),
    'Descripción': art.descripcion,
    'Impuesto': art.impuesto,
  }));
  const ws = XLSX.utils.json_to_sheet(data);
  const wb = XLSX.utils.book_new();
  XLSX.utils.book_append_sheet(wb, ws, 'Artículos');
  const excelBuffer = XLSX.write(wb, { bookType: 'xlsx', type: 'array' });
  saveAs(new Blob([excelBuffer], { type: 'application/octet-stream' }), 'articulos.xlsx');
};
</script>

<template>
  <div class="articulos">
    <h2>Artículos</h2>
    <div class="actions">
      <Button label="Agregar Artículo" icon="pi pi-plus" @click="openModal" />
      <InputText v-model="search" placeholder="Buscar..." class="ml-2" />
    </div>
    <div class="articulos-card">
      <DataTable
        :value="filteredArticulos"
        :sortField="sortField"
        :sortOrder="sortOrder"
        responsiveLayout="scroll"
        :loading="loadingArticulos"
      >
        <Column field="sku" header="SKU" sortable />
        <Column field="nombre" header="Nombre" sortable />
        <Column field="tipo" header="Tipo" sortable />
        <Column field="precioVenta" header="Precio de venta">
          <template #body="slotProps">
            {{ formatoMoneda(slotProps.data.precioVenta) }}
          </template>
        </Column>
        <Column header="Existencias en mano">
          <template #body="slotProps">
            <span v-if="slotProps.data.tipo && slotProps.data.tipo.toLowerCase() === 'servicio'">NA</span>
            <span v-else>{{ slotProps.data.existencias }}</span>
          </template>
        </Column>
        <Column field="precioCompra" header="Precio de compra">
          <template #body="slotProps">
            {{ formatoMoneda(slotProps.data.precioCompra) }}
          </template>
        </Column>
        <Column field="codigoSat" header="Código SAT" sortable />
        <Column field="unidadSat" header="Unidad SAT" sortable />
        <Column field="codigoUnidadSat" header="Código unidad SAT" sortable />
        <Column header="Acciones">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" class="p-button-text" @click="editArticulo(slotProps.data)" />
            <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="confirmDeleteArticulo(slotProps.data.id)" />
          </template>
        </Column>
      </DataTable>
    </div>

    <Dialog v-model:visible="showModal" :header="form.id ? 'Editar Artículo' : 'Nuevo Artículo'" :modal="true" :closable="true" class="custom-modal">
      <div class="modal-content">
        <h3 class="modal-title">{{ form.id ? 'Editar Artículo' : 'Nuevo Artículo' }}</h3>
        <div class="form-grid">
          <div class="form-row">
            <div class="form-col">
              <div class="form-group">
                <label for="tipo">Tipo:</label>
                <Dropdown id="tipo" v-model="form.tipo" :options="['Bienes', 'Servicio']" placeholder="Selecciona tipo" class="w-full" />
              </div>
              <div class="form-group">
                <label for="nombre">Nombre:</label>
                <InputText id="nombre" v-model="form.nombre" placeholder="Nombre del artículo" class="w-full" />
                <small v-if="!form.nombre" class="error-text">Obligatorio.</small>
              </div>
              <div class="form-group">
                <label for="sku">SKU:</label>
                <InputText id="sku" v-model="form.sku" placeholder="SKU o código interno" class="w-full" />
                <small v-if="!form.sku" class="error-text">Obligatorio.</small>
              </div>
              <div class="form-group">
                <label for="unidad">Unidad:</label>
                <Dropdown id="unidad" v-model="form.unidad" :options="['pieza', 'servicio', 'kg', 'litro']" placeholder="Selecciona unidad" class="w-full" />
              </div>
              <div class="form-group">
                <label for="precioVenta">Precio de venta (MXN):</label>
                <InputText id="precioVenta" v-model="form.precioVenta" placeholder="Precio de venta" class="w-full" />
              </div>
            </div>
            <div class="form-col">
              <div class="form-group">
                <label for="impuesto">Impuesto:</label>
                <Dropdown id="impuesto" v-model="form.impuesto" :options="['IVA 16%', 'IVA 0%', 'Exento']" placeholder="Selecciona impuesto" class="w-full" />
              </div>
              <div class="form-group">
                <label for="descripcion">Descripción:</label>
                <InputText id="descripcion" v-model="form.descripcion" placeholder="Descripción (opcional)" class="w-full" />
              </div>
              <div class="form-group">
                <label for="precioCompra">Precio de compra (MXN):</label>
                <InputText id="precioCompra" v-model="form.precioCompra" placeholder="Precio de compra" class="w-full" />
              </div>
              <div class="form-group">
                <label for="codigoSat">Código artículo SAT:</label>
                <InputText id="codigoSat" v-model="form.codigoSat" placeholder="Código SAT" class="w-full" />
              </div>
              <div class="form-group">
                <label for="unidadSat">Unidad SAT:</label>
                <InputText id="unidadSat" v-model="form.unidadSat" placeholder="Unidad SAT" class="w-full" />
              </div>
              <div class="form-group">
                <label for="codigoUnidadSat">Código unidad SAT:</label>
                <InputText id="codigoUnidadSat" v-model="form.codigoUnidadSat" placeholder="Código unidad SAT" class="w-full" />
              </div>
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <Button label="Guardar" icon="pi pi-save" @click="saveArticulo" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="closeModal" />
        </div>
      </div>
    </Dialog>

    <Dialog v-model:visible="showErrorDialog" header="Error" :modal="true" :closable="false">
      <div class="dialog-content">
        <p>{{ errorMessage }}</p>
        <div class="modal-actions">
          <Button label="Aceptar" icon="pi pi-check" @click="showErrorDialog = false" />
        </div>
      </div>
    </Dialog>

    <Dialog v-model:visible="showConfirmDelete" header="Confirmar Eliminación" :modal="true" :closable="false">
      <div class="dialog-content">
        <p>¿Eliminar este artículo?</p>
        <div class="modal-actions">
          <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" @click="deleteArticulo(articuloToDelete)" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="showConfirmDelete = false" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<style scoped>
.articulos {
  /* max-width: 900px; */
  padding: 2rem;
  margin: 0 auto;
  text-align: center;
  background: var(--color-bg);
  color: var(--color-text);
}
.actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}
.articulos-card {
  background: var(--color-card);
  color: var(--color-text);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
  border: 1px solid var(--color-border);
}
:deep(.p-dialog.custom-modal .p-dialog-header) {
  background: var(--color-bg);
  border-bottom: 2px solid #1976d2;
}
:deep(.p-dialog.custom-modal .p-dialog-content) {
  background: var(--color-card);
}
.modal-content {
  padding: 1rem 0.5rem;
  text-align: left;
}
.modal-title {
  color: var(--color-title);
  text-align: center;
  margin-bottom: 1.5rem;
  font-weight: bold;
  font-size: 1.3rem;
  letter-spacing: 1px;
}
.form-grid {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}
.form-row {
  display: flex;
  gap: 2rem;
  flex-wrap: wrap;
}
.form-col {
  flex: 1 1 0;
  min-width: 250px;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
.error-text {
  color: #d32f2f;
  font-size: 0.85rem;
  margin-top: 0.25rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
@media (max-width: 700px) {
  .form-grid {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>