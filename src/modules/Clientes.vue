<template>
  <div class="clientes-container">
    <h2 class="clientes-title">Clientes</h2>
    <div class="clientes-filtros">
      <InputText
        v-model="filtroNombre"
        placeholder="Buscar por nombre..."
        class="filtro-input"
        clearable
      />
      <AutoComplete
        v-model="filtroUsuario"
        :suggestions="usuariosFiltrados"
        @complete="buscarUsuario"
        optionLabel="label"
        placeholder="Filtrar por usuario"
        class="filtro-autocomplete"
        :dropdown="true"
        forceSelection
        @item-select="e => filtroUsuario = e.value.label"
      />
      <AutoComplete
        v-model="filtroTelefono"
        :suggestions="telefonosFiltrados"
        @complete="buscarTelefono"
        optionLabel="label"
        placeholder="Filtrar por teléfono"
        class="filtro-autocomplete"
        :dropdown="true"
        forceSelection
        @item-select="e => filtroTelefono = e.value.label"
      />
      <Button label="Limpiar" icon="pi pi-times" class="p-button-secondary" @click="limpiarFiltros" />
      <Button label="Agregar Cliente" icon="pi pi-plus" @click="openModal" class="p-button-success" />
    </div>
    <div class="clientes-card">
      <DataTable :value="clientesFiltrados" stripedRows responsiveLayout="scroll" class="clientes-table">
        <Column field="nombre" header="Nombre" />
        <Column field="telefono" header="Teléfonos">
          <template #body="slotProps">
            <ul class="list-inline">
              <li v-for="(tel, idx) in slotProps.data.telefonos" :key="idx">
                <span class="chip chip-telefono">{{ tel }}</span>
              </li>
            </ul>
          </template>
        </Column>
        <Column field="correo" header="Correo" />
        <Column field="direccion" header="Ciudad" />
        <Column header="Usuarios">
          <template #body="slotProps">
            <ul class="list-inline">
              <li v-for="(u, idx) in slotProps.data.usuarios" :key="idx">
                <span class="chip chip-usuario">{{ u }}</span>
              </li>
            </ul>
          </template>
        </Column>
        <Column header="Plataformas">
          <template #body="slotProps">
            <ul class="list-inline">
              <li v-for="(p, idx) in slotProps.data.plataformas" :key="idx">
                <span class="chip chip-plataforma">{{ p }}</span>
              </li>
            </ul>
          </template>
        </Column>
        <Column header="Acciones" body-class="acciones-col">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" class="p-button-rounded p-button-text p-button-info" @click="editCliente(slotProps.data)" />
            <Button icon="pi pi-trash" class="p-button-rounded p-button-text p-button-danger" @click="handleDeleteCliente(slotProps.data.id)" />
          </template>
        </Column>
      </DataTable>
    </div>
    <!-- Modal para agregar/editar cliente -->
    <Dialog v-model:visible="showModal" :header="form.id ? 'Editar Cliente' : 'Nuevo Cliente'" :modal="true" :closable="true" class="clientes-dialog">
      <div class="form-group">
        <label for="nombre">Nombre:</label>
        <InputText id="nombre" v-model="form.nombre" class="w-full" />
      </div>
      <div class="form-group">
        <label>Teléfonos:</label>
        <div v-for="(tel, idx) in form.telefonos" :key="idx" class="input-row">
          <InputText v-model="form.telefonos[idx]" class="w-full" />
          <Button icon="pi pi-minus" class="p-button-text p-button-danger" @click="removeTelefono(idx)" v-if="form.telefonos.length > 1" />
        </div>
        <Button icon="pi pi-plus" class="p-button-text" @click="addTelefono" />
      </div>
      <div class="form-group">
        <label for="correo">Correo:</label>
        <InputText id="correo" v-model="form.correo" class="w-full" />
      </div>
      <div class="form-group">
        <label for="direccion">Ciudad:</label>
        <InputText id="direccion" v-model="form.direccion" class="w-full" />
      </div>
      <div class="form-group">
        <label>Usuarios:</label>
        <div v-for="(u, idx) in form.usuarios" :key="idx" class="input-row">
          <InputText v-model="form.usuarios[idx]" class="w-full" />
          <Button icon="pi pi-minus" class="p-button-text p-button-danger" @click="removeUsuario(idx)" v-if="form.usuarios.length > 1" />
        </div>
        <Button icon="pi pi-plus" class="p-button-text" @click="addUsuario" />
      </div>
      <div class="form-group">
        <label>Plataformas:</label>
        <div v-for="(p, idx) in form.plataformas" :key="idx" class="input-row">
          <InputText v-model="form.plataformas[idx]" class="w-full" />
          <Button icon="pi pi-minus" class="p-button-text p-button-danger" @click="removePlataforma(idx)" v-if="form.plataformas.length > 1" />
        </div>
        <Button icon="pi pi-plus" class="p-button-text" @click="addPlataforma" />
      </div>
      <div class="modal-actions">
        <Button label="Guardar" icon="pi pi-save" @click="saveCliente" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="closeModal" />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, computed, onMounted, watch } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import AutoComplete from 'primevue/autocomplete';
import { useToast } from 'primevue/usetoast';
import { getClientes, addCliente, updateCliente, deleteCliente } from '@/services/clientesService';

const toast = useToast();

const clientes = ref([]);
const showModal = ref(false);
const form = ref({
  id: null,
  nombre: '',
  telefonos: [''],
  correo: '',
  direccion: '',
  usuarios: [''],
  plataformas: ['']
});

const filtroNombre = ref('');
const filtroUsuario = ref(null);
const filtroPlataforma = ref(null);
const filtroTelefono = ref(null);

const limpiarFiltros = () => {
  filtroNombre.value = '';
  filtroUsuario.value = null;
  filtroTelefono.value = null;
};

const clientesFiltrados = computed(() => {
  return clientes.value.filter(c => {
    const nombreOk = !filtroNombre.value || c.nombre.toLowerCase().includes(filtroNombre.value.toLowerCase());
    const usuarioOk = !filtroUsuario.value || (c.usuarios && c.usuarios.includes(filtroUsuario.value));
    const telefonoOk = !filtroTelefono.value ||
      (c.telefonos && c.telefonos.some(tel => tel.includes(filtroTelefono.value)));
    return nombreOk && usuarioOk && telefonoOk;
  });
});

const usuariosUnicos = computed(() => {
  const set = new Set();
  clientes.value.forEach(c => (c.usuarios || []).forEach(u => set.add(u)));
  return Array.from(set).map(u => ({ label: u, value: u }));
});
const plataformasUnicas = computed(() => {
  const set = new Set();
  clientes.value.forEach(c => (c.plataformas || []).forEach(p => set.add(p)));
  return Array.from(set).map(p => ({ label: p, value: p }));
});
const telefonosUnicos = computed(() => {
  const set = new Set();
  clientes.value.forEach(c => (c.telefonos || []).forEach(t => set.add(t)));
  return Array.from(set).map(t => ({ label: t, value: t }));
});

// Para autocompletar usuarios/plataformas
const usuariosFiltrados = ref([]);
const plataformasFiltradas = ref([]);
const telefonosFiltrados = ref([]);

const buscarUsuario = (event) => {
  const query = event.query?.toLowerCase() || '';
  usuariosFiltrados.value = usuariosUnicos.value.filter(u => u.label.toLowerCase().includes(query));
};
const buscarPlataforma = (event) => {
  const query = event.query?.toLowerCase() || '';
  plataformasFiltradas.value = plataformasUnicas.value.filter(p => p.label.toLowerCase().includes(query));
};
const buscarTelefono = (event) => {
  const query = event.query?.toLowerCase() || '';
  telefonosFiltrados.value = telefonosUnicos.value.filter(t => t.label.toLowerCase().includes(query));
};

const loadClientes = async () => {
  clientes.value = await getClientes();
};

onMounted(loadClientes);

const openModal = () => {
  form.value = {
    id: null,
    nombre: '',
    telefonos: [''],
    correo: '',
    direccion: '',
    usuarios: [''],
    plataformas: ['']
  };
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const saveCliente = async () => {
  if (!form.value.nombre) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'El nombre es obligatorio.', life: 4000 });
    return;
  }
  form.value.telefonos = form.value.telefonos.filter(t => t);
  form.value.usuarios = form.value.usuarios.filter(u => u);
  form.value.plataformas = form.value.plataformas.filter(p => p);
  try {
    if (form.value.id) {
      await updateCliente(form.value.id, form.value);
      toast.add({ severity: 'success', summary: 'Cliente actualizado', detail: 'El cliente se actualizó correctamente.', life: 3000 });
    } else {
      await addCliente(form.value);
      toast.add({ severity: 'success', summary: 'Cliente agregado', detail: 'El cliente se agregó correctamente.', life: 3000 });
    }
    showModal.value = false;
    await loadClientes();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al guardar el cliente.', life: 4000 });
  }
};

const editCliente = (cliente) => {
  form.value = {
    id: cliente.id,
    nombre: cliente.nombre,
    telefonos: cliente.telefonos?.length ? [...cliente.telefonos] : [''],
    correo: cliente.correo,
    direccion: cliente.direccion,
    usuarios: cliente.usuarios?.length ? [...cliente.usuarios] : [''],
    plataformas: cliente.plataformas?.length ? [...cliente.plataformas] : ['']
  };
  showModal.value = true;
};

const handleDeleteCliente = async (id) => {
  try {
    await deleteCliente(id);
    await loadClientes();
    toast.add({ severity: 'success', summary: 'Cliente eliminado', detail: 'El cliente se eliminó correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al eliminar el cliente.', life: 4000 });
  }
};

const addTelefono = () => form.value.telefonos.push('');
const removeTelefono = (idx) => form.value.telefonos.splice(idx, 1);
const addUsuario = () => form.value.usuarios.push('');
const removeUsuario = (idx) => form.value.usuarios.splice(idx, 1);
const addPlataforma = () => form.value.plataformas.push('');
const removePlataforma = (idx) => form.value.plataformas.splice(idx, 1);

watch(filtroUsuario, (val) => {
  if (typeof val === 'object' && val !== null) filtroUsuario.value = val.label;
});
watch(filtroPlataforma, (val) => {
  if (typeof val === 'object' && val !== null) filtroPlataforma.value = val.label;
});
</script>

<style scoped>
.clientes-container {
  max-width: 1100px;
  margin: 2rem auto;
  padding: 2rem;
  background: var(--color-bg);
  color: var(--color-text);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
}
.clientes-title {
  margin-bottom: 2rem;
  color: var(--color-title, #ff4081);
  text-align: center;
  font-size: 2rem;
  font-weight: bold;
  letter-spacing: 1px;
}
.clientes-filtros {
  display: flex;
  flex-wrap: wrap;
  gap: 1rem;
  margin-bottom: 1.5rem;
  align-items: center;
}
.filtro-input {
  min-width: 220px;
  flex: 1;
}
.filtro-dropdown {
  min-width: 200px;
}
.filtro-autocomplete {
  min-width: 220px;
}
.clientes-card {
  background: var(--color-card);
  border-radius: 12px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.clientes-table {
  border-radius: 8px;
  overflow: hidden;
}
.list-inline {
  list-style: none;
  padding: 0;
  margin: 0;
  display: flex;
  flex-wrap: wrap;
  gap: 0.3rem;
}
.chip {
  display: inline-block;
  padding: 0.2em 0.7em;
  border-radius: 12px;
  font-size: 0.95em;
  font-weight: 500;
  background: var(--color-card);
  color: var(--color-text);
}
.chip-usuario {
  background: #b2ebf2;
  color: #00695c;
}
.chip-plataforma {
  background: #ffe082;
  color: #795548;
}
.chip-telefono {
  background: #e1bee7;
  color: #4a148c;
  font-weight: 500;
  border-radius: 12px;
  padding: 0.2em 0.7em;
  margin-right: 0.2em;
  display: inline-block;
}
.acciones-col {
  min-width: 120px;
  display: flex;
  gap: 0.5rem;
  justify-content: center;
}
.input-row {
  display: flex;
  gap: 0.5rem;
  align-items: center;
  margin-bottom: 0.3rem;
}
.form-group {
  margin-bottom: 1rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1rem;
}
.clientes-dialog :deep(.p-dialog-content) {
  background: var(--color-card, #292d36);
  padding: 1.5rem 1rem;
  border-radius: 12px;
}
.clientes-dialog :deep(.p-dialog-header) {
  background: var(--color-bg, #23272f);
  color: var(--color-title, #ff4081);
  border-bottom: 1px solid #e0e0e0;
  border-radius: 12px 12px 0 0;
  font-size: 1.2rem;
  font-weight: bold;
  padding: 1rem 1.5rem;
}
@media (max-width: 700px) {
  .clientes-container {
    padding: 1rem 0.2rem;
  }
  .clientes-card {
    padding: 0.5rem;
  }
  .clientes-filtros {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
}
</style>