<template>
  <div class="clientes-page">
    <div class="clientes-header-card">
      <div class="clientes-title-row">
        <h2 class="clientes-title">
          <i class="pi pi-users icon-accent"></i>
          Clientes
        </h2>
        <span class="clientes-subtitle">{{ clientes.length }} registrado{{ clientes.length === 1 ? '' : 's' }}</span>
      </div>
      <div class="clientes-filtros">
        <span class="p-input-icon-left filtro-input">
          <i class="pi pi-search"></i>
          <InputText v-model="filtroNombre" placeholder="Buscar por nombre..." class="w-full" />
        </span>
        <span class="p-input-icon-left filtro-autocomplete">
          <i class="pi pi-user"></i>
          <AutoComplete
            v-model="filtroUsuario"
            :suggestions="usuariosFiltrados"
            @complete="buscarUsuario"
            optionLabel="label"
            placeholder="Filtrar por usuario"
            class="w-full"
            :dropdown="true"
            forceSelection
            @item-select="e => filtroUsuario = e.value.label"
          />
        </span>
        <span class="p-input-icon-left filtro-autocomplete">
          <i class="pi pi-phone"></i>
          <AutoComplete
            v-model="filtroTelefono"
            :suggestions="telefonosFiltrados"
            @complete="buscarTelefono"
            optionLabel="label"
            placeholder="Filtrar por teléfono"
            class="w-full"
            :dropdown="true"
            forceSelection
            @item-select="e => filtroTelefono = e.value.label"
          />
        </span>
        <Button label="Limpiar" icon="pi pi-times" class="p-button-sm p-button-outlined" @click="limpiarFiltros" />
        <Button label="Agregar Cliente" icon="pi pi-plus" class="p-button-sm" @click="openModal" />
      </div>
    </div>
    <div class="clientes-table-card">
      <DataTable
        :value="clientesFiltrados"
        :loading="loading"
        stripedRows
        class="clientes-table"
        :paginator="clientesFiltrados.length > 10"
        :rows="50"
        size="small"
        :rowsPerPageOptions="[50, 100, 150, 200]"
        paginatorTemplate="FirstPageLink PrevPageLink PageLinks NextPageLink LastPageLink CurrentPageReport RowsPerPageDropdown"
        currentPageReportTemplate="Mostrando {first} a {last} de {totalRecords}"
      >
        <template #loading>
          <DataTableLoader text="Cargando clientes..." />
        </template>
        <template #empty>
          <div class="clientes-empty">
            <i class="pi pi-users"></i>
            <span>{{ filtroNombre || filtroUsuario || filtroTelefono ? 'Sin resultados para estos filtros.' : 'Aún no hay clientes registrados.' }}</span>
          </div>
        </template>
        <Column header="Nombre" :pt="{ bodyCell: { 'data-label': 'Nombre' } }">
          <template #body="slotProps">
            <div class="cliente-nombre-cell">
              <span class="cliente-avatar">{{ inicialesDe(slotProps.data.nombre) }}</span>
              <span>{{ slotProps.data.nombre }}</span>
              <i
                v-if="slotProps.data.facturapi_validado"
                class="pi pi-verified facturapi-badge facturapi-badge-validado"
                title="Datos fiscales validados ante el SAT"
              ></i>
              <i
                v-else-if="slotProps.data.facturapi_customer_id"
                class="pi pi-sync facturapi-badge facturapi-badge-sincronizado"
                title="Sincronizado con Facturapi, datos fiscales sin validar"
              ></i>
              <i
                v-else-if="datosFiscalesCapturados(slotProps.data)"
                class="pi pi-check-circle facturapi-badge facturapi-badge-capturado"
                title="Datos fiscales capturados, pendientes de sincronizar con Facturapi"
              ></i>
              <i
                v-else
                class="pi pi-user facturapi-badge facturapi-badge-generico"
                title="Sin RFC propio capturado — se facturaría como público en general"
              ></i>
            </div>
          </template>
        </Column>
        <Column field="telefono" header="Teléfonos" :pt="{ bodyCell: { 'data-label': 'Teléfonos' } }">
          <template #body="slotProps">
            <div class="chip-list">
              <span v-for="(tel, idx) in slotProps.data.telefonos" :key="idx" class="chip chip-telefono">
                <i class="pi pi-phone chip-icon tel"></i>{{ tel }}
              </span>
            </div>
          </template>
        </Column>
        <Column field="correo" header="Correo" :pt="{ bodyCell: { 'data-label': 'Correo' } }" />
        <Column field="direccion" header="Ciudad" :pt="{ bodyCell: { 'data-label': 'Ciudad' } }" />
        <Column header="Usuarios" :pt="{ bodyCell: { 'data-label': 'Usuarios' } }">
          <template #body="slotProps">
            <div class="chip-list">
              <span v-for="(u, idx) in slotProps.data.usuarios" :key="idx" class="chip chip-usuario">
                <i class="pi pi-user chip-icon usr"></i>{{ u }}
              </span>
            </div>
          </template>
        </Column>
        <Column header="Plataformas" :pt="{ bodyCell: { 'data-label': 'Plataformas' } }">
          <template #body="slotProps">
            <div class="chip-list">
              <span v-for="(p, idx) in slotProps.data.plataformas" :key="idx" class="chip chip-plataforma">
                <i class="pi pi-globe chip-icon plat"></i>{{ p }}
              </span>
            </div>
          </template>
        </Column>
        <Column header="Acciones" body-class="acciones-col">
          <template #body="slotProps">
            <Button icon="pi pi-pencil" class="p-button-sm p-button-rounded p-button-text" title="Editar" @click="editCliente(slotProps.data)" />
            <Button
              icon="pi pi-envelope" class="p-button-sm p-button-rounded p-button-text"
              title="Enviar liga para que capture sus datos fiscales"
              :loading="enviandoLigaId === slotProps.data.id"
              @click="enviarLigaFiscal(slotProps.data)"
            />
            <Button
              icon="pi pi-verified" class="p-button-sm p-button-rounded p-button-text"
              title="Validar información fiscal ante el SAT"
              :loading="validandoId === slotProps.data.id"
              @click="validarFiscal(slotProps.data)"
            />
            <Button icon="pi pi-trash" class="p-button-sm p-button-rounded p-button-text p-button-danger" title="Eliminar" @click="handleDeleteCliente(slotProps.data.id)" />
          </template>
        </Column>
      </DataTable>
    </div>
    <Dialog
      v-model:visible="showModal"
      :header="form.id ? 'Editar Cliente' : 'Nuevo Cliente'"
      :modal="true"
      :closable="true"
      class="clientes-dialog"
      style="width: 640px"
      :breakpoints="{ '768px': '92vw' }"
    >
      <div class="clientes-dialog-content compact-form">
        <div class="formgrid grid grid-responsive">
          <div class="field col-12 md:col-6">
            <label for="nombre"><i class="pi pi-user icon-inline"></i>Nombre:</label>
            <InputText id="nombre" v-model="form.nombre" class="w-full" placeholder="Nombre del cliente" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-phone icon-inline"></i>Teléfonos:</label>
            <div v-for="(tel, idx) in form.telefonos" :key="idx" class="input-row">
              <InputText v-model="form.telefonos[idx]" class="w-full" placeholder="Teléfono" />
              <Button icon="pi pi-minus" class="clientes-btn" @click="removeTelefono(idx)" v-if="form.telefonos.length > 1" />
            </div>
            <Button icon="pi pi-plus" class="clientes-btn" @click="addTelefono" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="correo"><i class="pi pi-envelope icon-inline"></i>Correo:</label>
            <InputText id="correo" v-model="form.correo" class="w-full" placeholder="Correo electrónico" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="direccion"><i class="pi pi-map-marker icon-inline"></i>Ciudad:</label>
            <InputText id="direccion" v-model="form.direccion" class="w-full" placeholder="Ciudad" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-user icon-inline"></i>Usuarios:</label>
            <div v-for="(u, idx) in form.usuarios" :key="idx" class="input-row">
              <InputText v-model="form.usuarios[idx]" class="w-full" placeholder="Usuario"
                 />
              <Button icon="pi pi-minus" class="clientes-btn" @click="removeUsuario(idx)" v-if="form.usuarios.length > 1 && idx !== 0" />
            </div>
            <Button icon="pi pi-plus" class="clientes-btn" @click="addUsuario" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-globe icon-inline"></i>Plataformas:</label>
            <div v-for="(plat, idx) in form.plataformas" :key="idx" class="input-row">
              <Dropdown v-model="form.plataformas[idx]" :options="['Wanway', 'Tracksolidpro']" class="w-full" />
              <Button icon="pi pi-minus" class="clientes-btn" @click="removePlataforma(idx)" v-if="form.plataformas.length > 1" />
            </div>
            <Button icon="pi pi-plus" class="clientes-btn" @click="addPlataforma" />
          </div>
          <div class="field col-12 md:col-6">
            <label><i class="pi pi-user-edit icon-inline"></i>Atendido por:</label>
            <div class="atendido-row">
              <InputText :value="atendidoPor" class="w-full" disabled />
            </div>
          </div>
          <div class="field col-12 md:col-6">
            <label for="rfc"><i class="pi pi-id-card icon-inline"></i>RFC:</label>
            <InputText id="rfc" v-model="form.rfc" class="w-full" placeholder="Dejar vacío = público en general (XAXX010101000)" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="calle_numero"><i class="pi pi-map icon-inline"></i>Calle y número:</label>
            <InputText id="calle_numero" v-model="form.calle_numero" class="w-full" placeholder="Ej: Jesus del Monte 4" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="colonia"><i class="pi pi-map icon-inline"></i>Colonia:</label>
            <InputText id="colonia" v-model="form.colonia" class="w-full" placeholder="Ej: Hacienda de las Palmas" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="codigo_postal"><i class="pi pi-map-marker icon-inline"></i>Código postal:</label>
            <InputText id="codigo_postal" v-model="form.codigo_postal" class="w-full" maxlength="5" placeholder="Ej: 52763" />
          </div>
          <div class="field col-12 md:col-6">
            <label for="regimen_fiscal"><i class="pi pi-id-card icon-inline"></i>Régimen fiscal:</label>
            <Dropdown
              id="regimen_fiscal"
              v-model="form.regimen_fiscal"
              :options="regimenesFiscales"
              optionLabel="label"
              optionValue="value"
              placeholder="Selecciona régimen fiscal"
              class="w-full"
              showClear
            />
          </div>
          <div class="field col-12 md:col-6">
            <label for="constancia"><i class="pi pi-file-pdf icon-inline"></i>Constancia Fiscal:</label>
            <input type="file" id="constancia" @change="onConstanciaFileChange" accept=".pdf,.png,.jpg,.jpeg" class="w-full" />
            <small v-if="archivoConstancia" class="file-selected">Archivo seleccionado: {{ archivoConstancia.name }}</small>
            <small v-if="form.constancia_path" class="file-existing">
              <a :href="constanciaUrl" download>Descargar constancia actual</a>
            </small>
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
// Genera usuario sugerido basado en el nombre, rellenando hasta 9 caracteres
function sugerirUsuario(nombre) {
  if (!nombre) return '';
  const partes = nombre.trim().split(/\s+/);
  let usuario = '';
  // Primer caracter: número aleatorio del 1 al 9
  usuario += Math.floor(Math.random() * 9) + 1;
  if (partes.length > 1) {
    for (let i = 0; i < partes.length - 1; i++) {
      usuario += partes[i][0] || '';
    }
    usuario += partes[partes.length - 1];
  } else {
    usuario += partes[0];
  }
  usuario = usuario.toLowerCase();
  // Si falta para llegar a 9, agrega dos dígitos aleatorios al final
  while (usuario.length < 9) {
    usuario += Math.floor(Math.random() * 10);
  }
  return usuario.slice(0, 9);
}
// ...existing code...
// ...existing imports...



// Inicializa usuarios con el nombre al abrir modal

function addUsuario() {
  form.value.usuarios.push('');
}
function removeUsuario(idx) {
  if (idx > 0) form.value.usuarios.splice(idx, 1);
}
import { ref, computed, onMounted, watch } from 'vue';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import InputText from 'primevue/inputtext';
import AutoComplete from 'primevue/autocomplete';
import Dropdown from 'primevue/dropdown';
import { useToast } from 'primevue/usetoast';
import DataTableLoader from '@/components/DataTableLoader.vue';
import {
  getClientes, addCliente, updateCliente, deleteCliente, uploadConstanciaCliente, extractRfcFromPdf,
  enviarLigaFiscalFacturapi, validarFiscalFacturapi,
} from '@/services/clientesService';
import { useLoginStore } from '@/stores/loginStore';
import { useRouter } from 'vue-router';

const toast = useToast();
const loginStore = useLoginStore();
const usuarioSesion = ref(loginStore.user?.username || '');
const atendidoPor = ref(loginStore.user?.username || '');

const archivoConstancia = ref(null);
const showModal = ref(false);
const loading = ref(false);
const clientes = ref([]);
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
  rfc: '',
  constancia_path: null,
  calle_numero: '',
  colonia: '',
  codigo_postal: '',
  regimen_fiscal: null
});

const regimenesFiscales = [
  { label: '601 - General de Ley Personas Morales', value: '601' },
  { label: '603 - Personas Morales con Fines no Lucrativos', value: '603' },
  { label: '605 - Sueldos y Salarios e Ingresos Asimilados a Salarios', value: '605' },
  { label: '606 - Arrendamiento', value: '606' },
  { label: '608 - Demás ingresos', value: '608' },
  { label: '610 - Residentes en el Extranjero sin Establecimiento Permanente en México', value: '610' },
  { label: '612 - Personas Físicas con Actividades Empresariales y Profesionales', value: '612' },
  { label: '616 - Sin obligaciones fiscales', value: '616' },
  { label: '621 - Incorporación Fiscal', value: '621' },
  { label: '626 - Régimen Simplificado de Confianza', value: '626' },
];

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

// Computed para la URL de descarga de constancia
const constanciaUrl = computed(() => {
  if (form.value.constancia_path) {
    const baseUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
    return baseUrl + '/' + form.value.constancia_path;
  }
  return null;
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

const onConstanciaFileChange = async (event) => {
  const file = event.target.files[0];
  if (file) {
    // Validar tipo y tamaño
    const allowedTypes = ['application/pdf', 'image/png', 'image/jpeg', 'image/jpg'];
    const maxSize = 8 * 1024 * 1024; // 8MB
    if (!allowedTypes.includes(file.type)) {
      toast.add({ severity: 'error', summary: 'Tipo no permitido', detail: 'Solo PDF, PNG, JPG.', life: 4000 });
      event.target.value = '';
      archivoConstancia.value = null;
      return;
    }
    if (file.size > maxSize) {
      toast.add({ severity: 'error', summary: 'Archivo grande', detail: 'Máximo 8MB.', life: 4000 });
      event.target.value = '';
      archivoConstancia.value = null;
      return;
    }
    archivoConstancia.value = file;

    // Si es PDF, extraer RFC
    if (file.type === 'application/pdf') {
      try {
        const extractedRfc = await extractRfcFromPdf(file);
        form.value.rfc = extractedRfc;
        toast.add({ severity: 'info', summary: 'RFC extraído', detail: `RFC ${extractedRfc} copiado al campo.`, life: 3000 });
      } catch (e) {
        toast.add({ severity: 'warn', summary: 'RFC no extraído', detail: 'No se pudo extraer el RFC del PDF.', life: 4000 });
      }
    }
  } else {
    archivoConstancia.value = null;
  }
};

const loadClientes = async () => {
  loading.value = true;
  try {
    clientes.value = await getClientes();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudieron cargar los clientes.', life: 4000 });
  }
  loading.value = false;
};

const RFC_PUBLICO_GENERAL = 'XAXX010101000';
// Distingue "cliente sin RFC propio" (facturaría como público en general)
// de "sí tiene RFC/CP/régimen capturados, solo falta sincronizar/validar" —
// antes ambos se veían igual porque el campo RFC traía el genérico prellenado.
function datosFiscalesCapturados(cliente) {
  return !!(cliente.rfc && cliente.rfc !== RFC_PUBLICO_GENERAL && cliente.codigo_postal && cliente.regimen_fiscal);
}

// Iniciales para el avatar de la columna Nombre (ej. "José Torres" -> "JT")
const inicialesDe = (nombre) => {
  const partes = (nombre || '').trim().split(/\s+/).filter(Boolean);
  if (!partes.length) return '?';
  return (partes[0][0] + (partes[1]?.[0] || '')).toUpperCase();
};

onMounted(loadClientes);

const router = useRouter();

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
    rfc: '',
    constancia_path: null,
    calle_numero: '',
    colonia: '',
    codigo_postal: '',
    regimen_fiscal: null
  };
  archivoConstancia.value = null;
  showModal.value = true;
};

const closeModal = () => {
  showModal.value = false;
};

const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;

const saveCliente = async () => {
  // Validar todos los campos obligatorios
  const nombreOk = !!form.value.nombre && form.value.nombre.trim() !== '';
  const telefonosOk = Array.isArray(form.value.telefonos) && form.value.telefonos.length > 0 && form.value.telefonos.every(t => t && t.trim() !== '');
  const correoOk = EMAIL_REGEX.test((form.value.correo || '').trim());
  const direccionOk = !!form.value.direccion && form.value.direccion.trim() !== '';
  const usuariosOk = Array.isArray(form.value.usuarios) && form.value.usuarios.length > 0 && form.value.usuarios.every(u => u && u.trim() !== '');
  const plataformasOk = Array.isArray(form.value.plataformas) && form.value.plataformas.length > 0 && form.value.plataformas.every(p => p && p.trim() !== '');

  if (!nombreOk || !telefonosOk || !correoOk || !direccionOk || !usuariosOk || !plataformasOk) {
    toast.add({
      severity: 'warn', summary: 'Campos obligatorios',
      detail: !correoOk && form.value.correo ? 'El correo no tiene un formato válido.' : 'Completa todos los campos antes de guardar.',
      life: 4000
    });
    return;
  }
  form.value.telefonos = form.value.telefonos.filter(t => t);
  form.value.usuarios = form.value.usuarios.filter(u => u);
  form.value.plataformas = form.value.plataformas.filter(p => p);
  form.value.atendidoPor = atendidoPor.value;
  form.value.usuarioSesion = usuarioSesion.value;
  try {
    let clienteId;
    if (form.value.id) {
      await updateCliente(form.value.id, form.value);
      clienteId = form.value.id;
      toast.add({ severity: 'success', summary: 'Cliente actualizado', detail: 'El cliente se actualizó correctamente.', life: 3000 });
    } else {
      const response = await addCliente(form.value);
      clienteId = response.id;
      toast.add({ severity: 'success', summary: 'Cliente agregado', detail: 'El cliente se agregó correctamente.', life: 3000 });
    }

    // Subir constancia fiscal si se seleccionó un archivo
    if (archivoConstancia.value) {
      try {
        await uploadConstanciaCliente(clienteId, archivoConstancia.value);
        toast.add({ severity: 'success', summary: 'Constancia subida', detail: 'La constancia fiscal se subió correctamente.', life: 3000 });
      } catch (e) {
        toast.add({ severity: 'error', summary: 'Error en constancia', detail: 'Error al subir la constancia fiscal.', life: 4000 });
      }
    }

    showModal.value = false;
    archivoConstancia.value = null; // Reset file input
    await loadClientes();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al guardar el cliente.', life: 4000 });
  }
};

const oldEditCliente = (cliente) => {
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
    rfc: cliente.rfc || '',
    constancia_path: cliente.constancia_path || null,
    calle_numero: cliente.calle_numero || '',
    colonia: cliente.colonia || '',
    codigo_postal: cliente.codigo_postal || '',
    regimen_fiscal: cliente.regimen_fiscal || null
  };
  usuarioSesion.value = form.value.usuarioSesion;
  atendidoPor.value = form.value.atendidoPor;
  archivoConstancia.value = null; // Reset file input
  showModal.value = true;
};

const editCliente = (cliente) => {
  oldEditCliente(cliente); // sin carga de constancia ahora
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

// Facturapi: liga de auto-captura fiscal — el cliente llena/corrige su RFC,
// domicilio y régimen directamente en Facturapi, sin que nosotros tengamos
// que adivinarlo. El backend sincroniza (crea si hace falta) antes de mandar.
const enviandoLigaId = ref(null);
const enviarLigaFiscal = async (cliente) => {
  enviandoLigaId.value = cliente.id;
  try {
    await enviarLigaFiscalFacturapi(cliente.id);
    toast.add({ severity: 'success', summary: 'Liga enviada', detail: `Se le mandó a ${cliente.correo || 'su correo'} la liga para capturar sus datos fiscales.`, life: 4500 });
    await loadClientes();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo enviar la liga.', life: 4500 });
  }
  enviandoLigaId.value = null;
};

const validandoId = ref(null);
const validarFiscal = async (cliente) => {
  validandoId.value = cliente.id;
  try {
    const resultado = await validarFiscalFacturapi(cliente.id);
    const valido = resultado?.is_valid ?? resultado?.valid;
    toast.add({
      severity: valido ? 'success' : 'warn',
      summary: valido ? 'Datos fiscales válidos' : 'Datos fiscales con problemas',
      detail: resultado?.message || (valido ? 'El SAT reconoce el RFC/régimen/domicilio capturados.' : 'Revisa el RFC/régimen/domicilio del cliente en Facturapi.'),
      life: 5000,
    });
    await loadClientes();
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: e?.response?.data?.detail || 'No se pudo validar la información fiscal.', life: 4500 });
  }
  validandoId.value = null;
};

const addTelefono = () => form.value.telefonos.push('');
const removeTelefono = (idx) => form.value.telefonos.splice(idx, 1);
const addPlataforma = () => form.value.plataformas.push('');
const removePlataforma = (idx) => form.value.plataformas.splice(idx, 1);

watch(filtroUsuario, (val) => {
  if (typeof val === 'object' && val !== null) filtroUsuario.value = val.label;
});
watch(filtroPlataforma, (val) => {
  if (typeof val === 'object' && val !== null) filtroPlataforma.value = val.label;
});

// Sincroniza el primer usuario con el nombre del cliente usando sugerirUsuario
watch(() => form.value.nombre, (nuevoNombre) => {
  // Solo sugerir usuario si estamos creando (id es null)
  if (form.value.id === null) {
    const sugerido = sugerirUsuario(nuevoNombre);
    if (form.value.usuarios && form.value.usuarios.length === 0) {
      form.value.usuarios = [sugerido];
    } else if (form.value.usuarios) {
      form.value.usuarios[0] = sugerido;
    }
  }
});

// Sincroniza el primer usuario con el nombre del cliente
</script>

<style scoped>
.clientes-page {
  background: linear-gradient(135deg, var(--color-bg) 80%, color-mix(in oklab, var(--color-primary) 12%, var(--color-bg)) 100%);
  min-height: 100vh;
  padding: 2rem 0.5rem;
}
.clientes-header-card {
  background: var(--color-card);
  border-radius: 16px;
  box-shadow: var(--shadow-2);
  padding: 1.2rem 2rem 1rem 2rem;
  margin-bottom: 1.5rem;
  display: flex;
  flex-direction: column;
  align-items: flex-start;
}
.clientes-title-row {
  display: flex;
  align-items: baseline;
  gap: 0.9rem;
  flex-wrap: wrap;
  margin-bottom: 0.8em;
}
.clientes-title {
  font-size: 2em;
  font-weight: 700;
  color: var(--color-primary, var(--color-title));
  display: flex;
  align-items: center;
  margin: 0;
}
.clientes-subtitle {
  font-size: 0.85rem;
  color: var(--color-text);
  opacity: 0.65;
  font-weight: 500;
}
.clientes-filtros {
  display: flex;
  gap: 1.2rem;
  margin-bottom: 0.5em;
  flex-wrap: wrap;
  align-items: center;
}
.filtro-input,
.filtro-autocomplete {
  flex: 1 1 220px;
  min-width: 190px;
}
.filtro-input :deep(input),
.filtro-autocomplete :deep(input) {
  width: 100%;
  border-radius: 10px;
}
.clientes-btn {
  border-radius: 8px;
  font-weight: 500;
  box-shadow: var(--shadow-1);
  background: linear-gradient(90deg, var(--color-card) 60%, var(--color-card) 100%);
  color: var(--color-title);
}
.clientes-table-card {
  background: var(--color-card);
  border-radius: 16px;
  box-shadow: var(--shadow-2);
  padding: 1.2rem 1rem 1rem 1rem;
}
.clientes-table {
  font-size: 1em;
  border-radius: 12px;
  background: transparent;
}
.clientes-table :deep(th) {
  background: var(--color-bg-light, transparent);
  font-size: 0.78rem;
  text-transform: uppercase;
  letter-spacing: 0.03em;
  color: var(--color-text);
}
.clientes-table :deep(tr:hover td) {
  background: color-mix(in srgb, var(--color-primary) 5%, transparent);
}
.cliente-nombre-cell {
  display: flex;
  align-items: center;
  gap: 0.6rem;
}
.cliente-avatar {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 2rem;
  height: 2rem;
  flex-shrink: 0;
  border-radius: 50%;
  background: color-mix(in srgb, var(--color-primary) 16%, transparent);
  color: var(--color-primary);
  font-size: 0.78rem;
  font-weight: 700;
}
.facturapi-badge {
  font-size: 0.9rem;
}
.facturapi-badge-validado {
  color: var(--color-success);
}
.facturapi-badge-sincronizado {
  color: color-mix(in oklab, var(--color-text) 40%, var(--color-primary));
}
.facturapi-badge-capturado {
  color: var(--color-warning);
}
.facturapi-badge-generico {
  color: var(--color-text);
  opacity: 0.45;
}
.clientes-empty {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.6rem;
  padding: 2.5rem 1rem;
  color: var(--color-text);
  opacity: 0.7;
}
.clientes-empty i {
  font-size: 2rem;
  color: var(--color-primary);
  opacity: 0.6;
}
.chip {
  display: inline-flex;
  align-items: center;
  padding: 0.18em 0.55em;
  border-radius: 7px;
  font-size: 0.97em;
  font-weight: 500;
  background: var(--color-bg-light);
  color: var(--color-text);
  border: 1px solid var(--color-border);
  box-shadow: var(--shadow-1);
  font-family: 'Montserrat', 'Roboto', Arial, sans-serif;
  margin-right: 0.18em;
  margin-bottom: 0.12em;
  transition: box-shadow 0.2s;
}
.chip i {
  font-size: 1em;
  margin-right: 0.32em;
  color: var(--color-text);
  opacity: 0.7;
}
.chip-usuario {
  background: var(--color-bg-light);
  color: color-mix(in oklab, var(--color-text) 65%, var(--color-primary));
}
.chip-plataforma {
  background: var(--color-bg-light);
  color: color-mix(in oklab, var(--color-text) 70%, var(--color-primary));
}
.chip-telefono {
  background: var(--color-bg-light);
  color: color-mix(in oklab, var(--color-text) 60%, var(--color-primary));
  font-weight: 500;
  border-radius: 12px;
  padding: 0.2em 0.7em;
  margin-right: 0.2em;
  display: inline-block;
}
.icon-accent { color: var(--color-primary); font-size: 1.5em; margin-right: 0.5em; }
.icon-inline { color: var(--color-primary); margin-right: 0.3em; }
.chip-icon { margin-right: 0.2em; opacity: 0.9; }
.chip-icon.tel { color: color-mix(in oklab, var(--color-text) 60%, var(--color-primary)); }
.chip-icon.usr { color: color-mix(in oklab, var(--color-text) 65%, var(--color-primary)); }
.chip-icon.plat { color: color-mix(in oklab, var(--color-text) 70%, var(--color-primary)); }
.acciones-col {
  min-width: 190px;
  display: flex;
  gap: 0.3rem;
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
    gap: 0.4rem;
    align-items: stretch;
  }
  .clientes-filtros > * {
    margin: 0;
    min-width: 0;
    width: 100%;
  }
  .filtro-autocomplete :deep(.p-autocomplete),
  .filtro-autocomplete :deep(.p-autocomplete-input) {
    width: 100%;
  }
  .clientes-title-row {
    flex-direction: column;
    align-items: flex-start;
    gap: 0.2rem;
  }
}

/* Mobile: la tabla deja de ser tabla y cada fila se vuelve una tarjeta
   (misma técnica clásica de "responsive table": thead se oculta, cada td
   se etiqueta con el nombre de su columna vía data-label + ::before). */
@media (max-width: 768px) {
  .clientes-table-card {
    background: transparent;
    box-shadow: none;
    padding: 0;
  }
  .clientes-table :deep(.p-datatable-thead) {
    display: none;
  }
  .clientes-table :deep(.p-datatable-tbody) > tr {
    display: block;
    background: var(--color-card) !important;
    border: 1px solid var(--color-border);
    border-radius: 14px;
    box-shadow: var(--shadow-1);
    margin-bottom: 0.85rem;
    padding: 0.85rem 1rem;
  }
  .clientes-table :deep(.p-datatable-tbody) > tr > td {
    display: flex;
    align-items: center;
    justify-content: space-between;
    gap: 0.75rem;
    padding: 0.45rem 0;
    border: none !important;
    text-align: right;
  }
  .clientes-table :deep(.p-datatable-tbody) > tr > td:not(:last-child) {
    border-bottom: 1px solid var(--color-border) !important;
  }
  .clientes-table :deep(.p-datatable-tbody) > tr > td::before {
    content: attr(data-label);
    font-weight: 700;
    font-size: 0.7rem;
    text-transform: uppercase;
    letter-spacing: 0.03em;
    color: var(--color-text);
    opacity: 0.55;
    text-align: left;
    flex-shrink: 0;
  }
  .clientes-table :deep(.p-datatable-tbody) > tr > td.acciones-col {
    justify-content: center;
    flex-wrap: wrap;
  }
  .clientes-table :deep(.p-paginator) {
    flex-wrap: wrap;
    justify-content: center;
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
.enlace-constancia { color: var(--color-primary); text-decoration: none; font-weight:500; }
.enlace-constancia:hover { text-decoration: underline; }
</style>