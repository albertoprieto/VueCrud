<template>
  <div class="articulos">
    <h2>Artículos</h2>
    <div class="actions">
      <Button label="Agregar Artículo" icon="pi pi-plus" @click="openModal" />
      <InputText v-model="search" placeholder="Buscar..." class="ml-2" />
    </div>
    <DataTable :value="filteredArticulos" :sortField="sortField" :sortOrder="sortOrder" responsiveLayout="scroll">
      <Column field="codigo" header="Código" sortable />
      <Column field="nombre" header="Nombre" sortable />
      <Column field="pagina" header="Página de Captura" sortable />
      <Column header="Acciones">
        <template #body="slotProps">
          <Button icon="pi pi-pencil" class="p-button-text" @click="editArticulo(slotProps.data)" />
          <Button icon="pi pi-trash" class="p-button-text p-button-danger" @click="deleteArticulo(slotProps.data.id)" />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showModal" header="Agregar/Editar Artículo" :modal="true" :closable="true">
      <div class="modal-content">
        <h3>{{ form.id ? 'Editar Artículo' : 'Nuevo Artículo' }}</h3>
        <div class="form-grid">
          <div class="form-col">
            <div class="form-group">
              <label for="tipo">Tipo:</label>
              <Dropdown id="tipo" v-model="form.tipo" :options="['Bienes', 'Servicio']" placeholder="Selecciona tipo" />
            </div>
            <div class="form-group">
              <label for="nombre">Nombre:</label>
              <InputText id="nombre" v-model="form.nombre" placeholder="Nombre del artículo" />
              <small v-if="!form.nombre" class="error-text">Este campo es obligatorio.</small>
            </div>
            <div class="form-group">
              <label for="sku">SKU:</label>
              <InputText id="sku" v-model="form.sku" placeholder="SKU o código interno" />
              <small v-if="!form.sku" class="error-text">Este campo es obligatorio.</small>
            </div>
            <div class="form-group">
              <label for="unidad">Unidad:</label>
              <Dropdown id="unidad" v-model="form.unidad" :options="['pieza', 'servicio', 'kg', 'litro']" placeholder="Selecciona unidad" />
            </div>
          </div>
          <div class="form-col">
            <div class="form-group">
              <label for="precioVenta">Precio de venta (MXN):</label>
              <InputText id="precioVenta" v-model="form.precioVenta" placeholder="Precio de venta" />
            </div>
            <div class="form-group">
              <label for="impuesto">Impuesto:</label>
              <Dropdown id="impuesto" v-model="form.impuesto" :options="['IVA 16%', 'IVA 0%', 'Exento']" placeholder="Selecciona impuesto" />
            </div>
            <div class="form-group">
              <label for="descripcion">Descripción:</label>
              <InputText id="descripcion" v-model="form.descripcion" placeholder="Descripción (opcional)" />
            </div>
          </div>
        </div>
        <div class="modal-actions">
          <Button label="Guardar" icon="pi pi-save" @click="saveArticulo" />
          <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="closeModal" />
        </div>
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import { getArticulos, addArticulo, updateArticulo, deleteArticulo as deleteArticuloService } from '@/services/articulosService';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Checkbox from 'primevue/checkbox';

const articulos = ref([]);
const showModal = ref(false);
const form = ref({ id: null, codigo: '', nombre: '', pagina: '' });
const search = ref('');
const sortField = ref('nombre');
const sortOrder = ref(1);

const loadArticulos = async () => {
  articulos.value = await getArticulos();
};

onMounted(loadArticulos);

const openModal = () => {
  form.value = { id: null, codigo: '', nombre: '', pagina: '' };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveArticulo = async () => {
  if (!form.value.codigo || !form.value.nombre || !form.value.pagina) {
    alert('Todos los campos son obligatorios');
    return;
  }
  if (form.value.id) {
    await updateArticulo({ ...form.value });
  } else {
    await addArticulo({ ...form.value });
  }
  showModal.value = false;
  await loadArticulos();
};

const editArticulo = (articulo) => {
  form.value = { ...articulo };
  showModal.value = true;
};

const deleteArticulo = async (id) => {
  if (confirm('¿Eliminar este artículo?')) {
    await deleteArticuloService(id);
    await loadArticulos();
  }
};

const filteredArticulos = computed(() => {
  if (!search.value) return articulos.value;
  return articulos.value.filter(a =>
    a.nombre.toLowerCase().includes(search.value.toLowerCase()) ||
    a.codigo.toLowerCase().includes(search.value.toLowerCase()) ||
    a.pagina.toLowerCase().includes(search.value.toLowerCase())
  );
});
</script>

<style scoped>
.articulos {
  max-width: 900px;
  margin: 0 auto;
  text-align: center;
}
.actions {
  display: flex;
  justify-content: flex-start;
  align-items: center;
  margin-bottom: 1rem;
  gap: 1rem;
}
:deep(.p-dialog) {
  width: 80vw !important;
  max-width: 80vw !important;
}
.modal-content {
  padding: 1rem 0.5rem;
  text-align: left;
}
.form-grid {
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
  color: red;
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