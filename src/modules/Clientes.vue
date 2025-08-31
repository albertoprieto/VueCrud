<template>
  <div class="clientes-page">
    <div class="clientes-header-card">
      <h2 class="clientes-title">
        <i class="pi pi-users" style="color:#ff4081; font-size:1.5em; margin-right:0.5em;"></i>
        Clientes
      </h2>
      <div class="clientes-filtros">
        <InputText
          v-model="filtroNombre"
          placeholder="Buscar por nombre..."
          class="filtro-input"
          clearable
        >
          <template #prepend>
            <i class="pi pi-search" style="color:#ff4081"></i>
          </template>
        </InputText>
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
        >
          <template #prepend>
            <i class="pi pi-user" style="color:#ff4081"></i>
          </template>
        </AutoComplete>
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
        >
          <template #prepend>
            <i class="pi pi-phone" style="color:#ff4081"></i>
          </template>
        </AutoComplete>
        <Button label="Limpiar" icon="pi pi-times" class="clientes-btn" @click="limpiarFiltros" />
        <Button label="Agregar Cliente" icon="pi pi-plus" @click="openModal" class="clientes-btn" />
      </div>
    </div>
    <div class="clientes-table-card">
      <DataTable :value="clientesFiltrados" stripedRows responsiveLayout="scroll" class="clientes-table">
        <Column field="nombre" header="Nombre" />
        <Column field="telefono" header="Teléfonos">
          <template #body="slotProps">
            <div class="chip-list">
              <span v-for="(tel, idx) in slotProps.data.telefonos" :key="idx" class="chip chip-telefono">
                <i class="pi pi-phone" style="margin-right:0.2em;color:#4a148c"></i>{{ tel }}
              </span>
            </div>
          </template>
        </Column>
        <Column field="correo" header="Correo" />
        <Column field="direccion" header="Ciudad" />
        <Column header="Usuarios">
          <template #body="slotProps">
            <div class="chip-list">
              <span v-for="(u, idx) in slotProps.data.usuarios" :key="idx" class="chip chip-usuario">
                <i class="pi pi-user" style="margin-right:0.2em;color:#00695c"></i>{{ u }}
              </span>
            </div>
          </template>
        </Column>
        <Column header="Plataformas">
          <template #body="slotProps">
            <div class="chip-list">
              <span v-for="(p, idx) in slotProps.data.plataformas" :key="idx" class="chip chip-plataforma">
                <i class="pi pi-globe" style="margin-right:0.2em;color:#795548"></i>{{ p }}
              </span>
            </div>
          </template>
        </Column>
        <Column header="Acciones" body-class="acciones-col">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" class="clientes-btn" @click="editCliente(slotProps.data)" />
            <Button icon="pi pi-trash" class="clientes-btn" @click="handleDeleteCliente(slotProps.data.id)" />
          </template>
        </Column>
      </DataTable>
    </div>
    <Dialog v-model:visible="showModal" :header="form.id ? 'Editar Cliente' : 'Nuevo Cliente'" :modal="true" :closable="true" class="clientes-dialog">
      <div class="clientes-dialog-content compact-form">
        <div class="formgrid grid grid-responsive">
          <div class="field col-12 md:col-6">
            <label for="nombre"><i class="pi pi-user" style="margin-right:0.3em;color:#ff4081"></i>Nombre:</label>
            <InputText id="nombre" v-model="form.nombre" class="w-full" placeholder="Nombre del cliente" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-phone" style="margin-right:0.3em;color:#ff4081"></i>Teléfonos:</label>
            <div v-for="(tel, idx) in form.telefonos" :key="idx" class="input-row">
              <InputText v-model="form.telefonos[idx]" class="w-full" placeholder="Teléfono" />
              <Button icon="pi pi-minus" class="clientes-btn" @click="removeTelefono(idx)" v-if="form.telefonos.length > 1" />
            </div>
            <Button icon="pi pi-plus" class="clientes-btn" @click="addTelefono" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="correo"><i class="pi pi-envelope" style="margin-right:0.3em;color:#ff4081"></i>Correo:</label>
            <InputText id="correo" v-model="form.correo" class="w-full" placeholder="Correo electrónico" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="direccion"><i class="pi pi-map-marker" style="margin-right:0.3em;color:#ff4081"></i>Ciudad:</label>
            <InputText id="direccion" v-model="form.direccion" class="w-full" placeholder="Ciudad" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-user" style="margin-right:0.3em;color:#ff4081"></i>Usuarios:</label>
            <div v-for="(u, idx) in form.usuarios" :key="idx" class="input-row">
              <InputText v-model="form.usuarios[idx]" class="w-full" placeholder="Usuario" />
              <Button icon="pi pi-minus" class="clientes-btn" @click="removeUsuario(idx)" v-if="form.usuarios.length > 1" />
            </div>
            <Button icon="pi pi-plus" class="clientes-btn" @click="addUsuario" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-globe" style="margin-right:0.3em;color:#ff4081"></i>Plataformas:</label>
            <div v-for="(p, idx) in form.plataformas" :key="idx" class="input-row">
              <InputText v-model="form.plataformas[idx]" class="w-full" placeholder="Plataforma" />
              <Button icon="pi pi-minus" class="clientes-btn" @click="removePlataforma(idx)" v-if="form.plataformas.length > 1" />
            </div>
            <Button icon="pi pi-plus" class="clientes-btn" @click="addPlataforma" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-user-edit" style="margin-right:0.3em;color:#ff4081"></i>Atendido por:</label>
            <div class="atendido-row">
              <InputText :value="atendidoPor" class="w-full" disabled />
            </div>
          </div>
          <div class="field col-12 md:col-6">
            <div class="factura-row">
              <label><i class="pi pi-file-edit" style="margin-right:0.3em;color:#ff4081"></i>Requiere factura:</label>
              <InputSwitch v-model="requiereFactura" class="factura-switch" />
            </div>
            <div v-if="requiereFactura">
              <label for="rfc" style="margin-top:0.5em;"><i class="pi pi-id-card" style="margin-right:0.3em;color:#ff4081"></i>RFC:</label>
              <InputText id="rfc" v-model="rfc.value" class="w-full" placeholder="RFC del cliente" />
            </div>
            <label for="constanciaFiscal" style="margin-top:0.5em;"><i class="pi pi-paperclip" style="margin-right:0.3em;color:#ff4081"></i>Constancia fiscal:</label>
            <input id="constanciaFiscal" type="file" @change="handleFileChange" class="w-full" />
          </div>
        </div>
        <div class="modal-actions">
          <Button label="Guardar" icon="pi pi-save" class="clientes-btn" @click="saveCliente" type="button" />
          <Button label="Cancelar" icon="pi pi-times" class="clientes-btn" @click="closeModal" />
        </div>
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
import InputSwitch from 'primevue/inputswitch';
import { useToast } from 'primevue/usetoast';
import { getClientes, addCliente, updateCliente, deleteCliente } from '@/services/clientesService';
import { useLoginStore } from '@/stores/loginStore';

const toast = useToast();
const loginStore = useLoginStore();
const usuarioSesion = ref(loginStore.user?.username || '');
const atendidoPor = ref(loginStore.user?.username || '');
const requiereFactura = ref(false);
const rfc = ref('XAXX010101000');
const constanciaFiscal = ref(null);
const rfcVisible = ref(false);

watch(requiereFactura, (val) => {
  console.log('watch requiereFactura:', val);
  
  rfcVisible.value = !!val.value;
  if (!val.value) {
    rfc.value = 'XAXX010101000';
  } else {
    rfc.value = '';
  }
});

const clientes = ref([]);
const showModal = ref(false);
const form = ref({
  id: null,
  nombre: '',
  telefonos: [''],
  correo: '',
  direccion: '',
  usuarios: [''],
  plataformas: [''],
  atendidoPor: '',
  usuarioSesion: '',
  requiereFactura: false,
  rfc: 'XAXX010101000',
  constanciaFiscal: null
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
    plataformas: [''],
    atendidoPor: atendidoPor.value,
    usuarioSesion: usuarioSesion.value,
    requiereFactura: requiereFactura.value,
    rfc: rfc.value,
    constanciaFiscal: null
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
  form.value.atendidoPor = atendidoPor.value;
  form.value.usuarioSesion = usuarioSesion.value;
  form.value.requiereFactura = requiereFactura.value;
  form.value.rfc = rfc.value;
  form.value.constanciaFiscal = constanciaFiscal.value;
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
    plataformas: cliente.plataformas?.length ? [...cliente.plataformas] : [''],
    atendidoPor: cliente.atendidoPor || atendidoPor.value,
    usuarioSesion: cliente.usuarioSesion || usuarioSesion.value,
    requiereFactura: cliente.requiereFactura ?? false,
    rfc: cliente.rfc || 'XAXX010101000',
    constanciaFiscal: null // No se precarga archivo
  };
  requiereFactura.value = form.value.requiereFactura;
  rfc.value = form.value.rfc;
  usuarioSesion.value = form.value.usuarioSesion;
  atendidoPor.value = form.value.atendidoPor;
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

const handleFacturaChange = () => {
  if (!requiereFactura.value) {
    rfc.value = 'XAXX010101000';
  } else {
    rfc.value = '';
  }
};

const handleFileChange = (event) => {
  constanciaFiscal.value = event.target.files[0];
};
</script>

<style scoped>
.clientes-page {
  background: linear-gradient(135deg,#fff 80%,#ffe6f0 100%);
  min-height: 100vh;
  padding: 2rem 0.5rem;
}
.clientes-header-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(255,64,129,0.10);
  padding: 1.2rem 2rem 1rem 2rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.clientes-title {
  font-size: 2em;
  font-weight: 700;
  color: #ff4081;
  display: flex;
  align-items: center;
  margin-bottom: 0.5em;
}
.clientes-filtros {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 0.5em;
  flex-wrap: wrap;
}
.clientes-btn {
  border-radius: 8px;
  font-weight: 500;
  box-shadow: 0 2px 8px rgba(255,64,129,0.08);
  background: linear-gradient(90deg,#fff 60%,#fff 100%);
  color: #bd3838;
}
.clientes-table-card {
  background: #fff;
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(255,64,129,0.10);
  padding: 1.2rem 1rem 1rem 1rem;
}
.clientes-table {
  font-size: 1em;
  border-radius: 12px;
  background: transparent;
}
.chip {
  display: inline-flex;
  align-items: center;
  padding: 0.18em 0.55em;
  border-radius: 7px;
  font-size: 0.97em;
  font-weight: 500;
  background: #f7f7fa;
  color: #444;
  /* border: 1px solid #e0e0e0; */ /* Eliminado el borde */
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
  font-family: 'Montserrat', 'Roboto', Arial, sans-serif;
  margin-right: 0.18em;
  margin-bottom: 0.12em;
  transition: box-shadow 0.2s;
}
.chip i {
  font-size: 1em;
  margin-right: 0.32em;
  color: #888;
  opacity: 0.7;
}
.chip-usuario {
  background: #f7f7fa;
  color: #00695c;
  /* border-color: #b2ebf2; */ /* Eliminado el borde */
}
.chip-plataforma {
  background: #f7f7fa;
  color: #795548;
  /* border-color: #ffe082; */ /* Eliminado el borde */
}
.chip-telefono {
  background: #f7f7fa;
  color: #4a148c;
  /* border-color: #e1bee7; */ /* Eliminado el borde */
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
.clientes-dialog-content {
  padding: 1rem 0.7rem 0.5rem 0.7rem;
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
  .clientes-header-card {
    min-width: 98vw;
    max-width: 99vw;
  }
  .grid-responsive > .field {
    min-width: 100%;
    flex: 1 1 100%;
  }
}
@media (max-width: 700px) {
  .clientes-page {
    padding: 1rem 0.2rem;
  }
  .clientes-header-card {
    padding: 0.5rem;
  }
  .clientes-table-card {
    padding: 0.5rem;
  }
  .clientes-filtros {
    flex-direction: column;
    gap: 0.5rem;
    align-items: stretch;
  }
}
.chip-list {
  display: flex;
  flex-wrap: wrap;
  gap: 0.1em;
  align-items: center;
  margin: 0;
  padding: 0;
}
.compact-form .formgrid {
  gap: 0.5rem 0.7rem;
}
.compact-form .field {
  margin-bottom: 0.1em;
  padding-bottom: 0.1em;
}
.atendido-row {
  margin-bottom: 0.2em;
}
.factura-row {
  display: flex;
  align-items: center;
  gap: 0.5em;
  margin-bottom: 0.2em;
}
.factura-switch {
  margin-left: 0.5em;
  vertical-align: middle;
}
</style>