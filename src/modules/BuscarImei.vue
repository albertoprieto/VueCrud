<template>
  <div class="buscar-imei-container">
    <h2 class="buscar-imei-title">Buscar IMEI</h2>
    <div class="buscar-imei-filtros">
      <InputText
        v-model="filtro"
        placeholder="Filtra por últimos dígitos, artículo o ubicación..."
        class="buscar-imei-input"
      />
      <Button label="Limpiar" icon="pi pi-times" @click="filtro = ''" class="ml-2" />
    </div>
    <DataTable
      :value="imeisFiltrados"
      :paginator="true"
      :rows="10"
      responsiveLayout="scroll"
      class="buscar-imei-table"
      :loading="cargando"
      stripedRows
      :rowsPerPageOptions="[10, 20, 50]"
      emptyMessage="No se encontraron IMEIs."
    >
      <Column field="imei" header="IMEI" sortable />
      <!-- <Column field="articulo_nombre" header="Artículo" sortable /> -->
      <Column field="sku" header="SKU" sortable />
      <Column field="ubicacion" header="Ubicación" sortable />
      <Column field="status" header="Estado">
        <template #body="slotProps">
          <span
            :class="{
              'imei-disponible': slotProps.data.status === 'Disponible',
              'imei-vendido': slotProps.data.status === 'Vendido',
              'imei-devuelto': slotProps.data.status === 'Devuelto'
            }"
          >
            {{ slotProps.data.status }}
          </span>
        </template>
      </Column>
      <Column header="Acciones">
        <template #body="slotProps">
          <Button
            v-if="slotProps.data.status === 'Vendido'"
            label="Devolver"
            icon="pi pi-undo"
            class="p-button-text p-button-warning"
            @click="devolver(slotProps.data.imei)"
            :disabled="!esAdmin"
          />
          <Button
            v-if="slotProps.data.status === 'Devuelto'"
            label="Ver motivo"
            icon="pi pi-info-circle"
            class="p-button-text p-button-secondary"
            @click="verMotivo(slotProps.data.imei)"
          />
          <Button
            label="Transferir"
            icon="pi pi-exchange"
            class="p-button-text p-button-info ml-2"
            @click="transferir(slotProps.data.imei)"
            :disabled="!esAdmin"
          />
          <Button
            label="Cambiar Estado"
            icon="pi pi-refresh"
            class="p-button-text p-button-help ml-2"
            @click="abrirDialogoEstado(slotProps.data)"
            :disabled="!esAdmin"
          />
          <Button
            label="Eliminar"
            icon="pi pi-trash"
            class="p-button-text p-button-danger ml-2"
            @click="eliminar(slotProps.data.imei)"
            :disabled="!esAdmin"
          />
        </template>
      </Column>
    </DataTable>

    <Dialog v-model:visible="showConfirmDelete" header="Confirmar Eliminación" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>¿Seguro que deseas eliminar este IMEI?</span>
      </div>
      <div class="modal-actions">
        <Button label="Eliminar" icon="pi pi-trash" class="p-button-danger" @click="eliminarConfirmado" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showConfirmDelete = false" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showTransferDialog" header="Transferir IMEI" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>Selecciona la ubicación destino para transferir el IMEI:</span>
        <Dropdown
          v-model="ubicacionDestino"
          :options="ubicaciones"
          optionLabel="nombre"
          placeholder="Selecciona ubicación"
          class="w-full mt-3"
        />
      </div>
      <div class="modal-actions">
  <Button label="Transferir" icon="pi pi-exchange" class="p-button-info" @click="transferirConfirmado" :disabled="!ubicacionDestino || !esAdmin" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showTransferDialog = false" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showMotivoDialog" header="Motivo de devolución" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>Por favor, ingresa el motivo de la devolución:</span>
        <InputText v-model="motivoDevolucion" class="w-full mt-3" />
      </div>
      <div class="modal-actions">
        <Button label="Devolver" icon="pi pi-undo" class="p-button-warning" @click="confirmarDevolucion" :disabled="!motivoDevolucion" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="cancelarDevolucion" />
      </div>
    </Dialog>

    <Dialog v-model:visible="showMotivoViewDialog" header="Motivo de devolución" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ motivoDevolucionView }}</span>
      </div>
      <div class="modal-actions">
        <Button label="Cerrar" icon="pi pi-times" class="p-button-secondary" @click="showMotivoViewDialog = false" />
      </div>
    </Dialog>
  </div>

  <Dialog v-model:visible="showEstadoDialog" header="Cambiar Estado del IMEI" :modal="true" :closable="false">
    <div style="padding:1.5rem; text-align:center;">
      <span>Selecciona el nuevo estado para el IMEI <b>{{ imeiAEditarEstado?.imei }}</b>:</span>
      <Dropdown
        v-model="nuevoEstado"
        :options="estadosDisponibles"
        optionLabel="label"
        optionValue="value"
        placeholder="Selecciona estado"
        class="w-full mt-3"
      />
    </div>
    <div class="modal-actions">
      <Button label="Actualizar" icon="pi pi-refresh" class="p-button-help" @click="cambiarEstado" :disabled="!nuevoEstado" />
      <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="showEstadoDialog = false" />

    </div>
  </Dialog>

</template>

<script setup>
import { ref, computed, onMounted } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import DataTable from 'primevue/datatable';
import Dropdown from 'primevue/dropdown';
import Column from 'primevue/column';
import Dialog from 'primevue/dialog';
import axios from 'axios';
import { devolverIMEI, deleteIMEI, updateIMEI } from '@/services/imeiService';
import { getUbicaciones, asignarImeisUbicacion } from '@/services/ubicacionesService';
import { registrarMovimiento } from '@/services/inventarioService';
import { useToast } from 'primevue/usetoast';
import { useLoginStore } from '@/stores/loginStore';

const showEstadoDialog = ref(false);
const imeiAEditarEstado = ref(null);
const nuevoEstado = ref('');
const estadosDisponibles = [
  { label: 'Disponible', value: 'Disponible' },
  { label: 'Vendido', value: 'Vendido' },
  { label: 'Devuelto', value: 'Devuelto' }
];

// Roles
const loginStore = useLoginStore();
const esAdmin = computed(() => loginStore.user?.perfil === 'Admin');

function abrirDialogoEstado(imeiObj) {
  imeiAEditarEstado.value = imeiObj;
  nuevoEstado.value = imeiObj.status;
  showEstadoDialog.value = true;
}

async function cambiarEstado() {
  if (!esAdmin.value) {
    toast.add({ severity: 'warn', summary: 'Permiso denegado', detail: 'Solo un administrador puede cambiar el estado.', life: 4000 });
    showEstadoDialog.value = false;
    return;
  }
  if (!imeiAEditarEstado.value) return;
  try {
    await updateIMEI(imeiAEditarEstado.value.imei, { status: nuevoEstado.value });
    await cargarImeis();
    toast.add({ severity: 'success', summary: 'Estado actualizado', detail: 'El estado fue actualizado correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo actualizar el estado.', life: 4000 });
  }
  showEstadoDialog.value = false;
  imeiAEditarEstado.value = null;
}


const toast = useToast();

const imeis = ref([]);
const filtro = ref('');
const cargando = ref(false);

const showConfirmDelete = ref(false);
const imeiAEliminar = ref(null);

const showTransferDialog = ref(false);
const imeiATransferir = ref(null);
const ubicaciones = ref([]);
const ubicacionDestino = ref(null);

const showMotivoDialog = ref(false);
const motivoDevolucion = ref('');
const imeiADevolver = ref(null);

const showMotivoViewDialog = ref(false);
const motivoDevolucionView = ref('');

const cargarImeis = async () => {
  cargando.value = true;
  const res = await axios.get('https://api.gpsubicacionapi.com/buscar-imei?digitos=');
  imeis.value = res.data;
  cargando.value = false;
};

const cargarUbicaciones = async () => {
  ubicaciones.value = await getUbicaciones();
};

onMounted(async () => {
  await cargarImeis();
  await cargarUbicaciones();
});

const imeisFiltrados = computed(() => {
  if (!filtro.value) return imeis.value;
  //
  const f = filtro.value.toLowerCase();
  return imeis.value.filter(i =>
    i.imei?.toLowerCase().includes(f) ||
    i.imei?.slice(-5).includes(f) ||
    i.sku?.toLowerCase().includes(f) ||
    i.articulo_nombre?.toLowerCase().includes(f) ||
    i.ubicacion?.toLowerCase().includes(f)
  );
});

const devolver = (imei) => {
  imeiADevolver.value = imei;
  motivoDevolucion.value = '';
  showMotivoDialog.value = true;
};

const confirmarDevolucion = async () => {
  if (!esAdmin.value) {
    toast.add({ severity: 'warn', summary: 'Permiso denegado', detail: 'Solo un administrador puede devolver IMEIs.', life: 4000 });
    showMotivoDialog.value = false;
    return;
  }
  try {
    await devolverIMEI(imeiADevolver.value, motivoDevolucion.value);
    await registrarMovimiento({
      usuario: 'sistema',
      evento: 'devolucion',
      articulo_id: null,
      articulo_nombre: null,
      imei: imeiADevolver.value,
      ubicacion_origen: null,
      ubicacion_destino: null,
      motivo: motivoDevolucion.value
    });
    await cargarImeis();
    toast.add({ severity: 'success', summary: 'IMEI devuelto', detail: 'El IMEI fue devuelto correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo devolver el IMEI.', life: 4000 });
  }
  showMotivoDialog.value = false;
  imeiADevolver.value = null;
  motivoDevolucion.value = '';
};

const cancelarDevolucion = () => {
  showMotivoDialog.value = false;
  imeiADevolver.value = null;
  motivoDevolucion.value = '';
};

const eliminar = (imei) => {
  imeiAEliminar.value = imei;
  showConfirmDelete.value = true;
};

const eliminarConfirmado = async () => {
  if (!esAdmin.value) {
    toast.add({ severity: 'warn', summary: 'Permiso denegado', detail: 'Solo un administrador puede eliminar IMEIs.', life: 4000 });
    showConfirmDelete.value = false;
    return;
  }
  if (!imeiAEliminar.value) return;
  try {
    await deleteIMEI(imeiAEliminar.value);
    await cargarImeis();
    toast.add({ severity: 'success', summary: 'IMEI eliminado', detail: 'El IMEI fue eliminado correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo eliminar el IMEI.', life: 4000 });
  }
  showConfirmDelete.value = false;
  imeiAEliminar.value = null;
};

const transferir = (imei) => {
  imeiATransferir.value = imei;
  ubicacionDestino.value = null;
  showTransferDialog.value = true;
};

const transferirConfirmado = async () => {
  if (!esAdmin.value) {
    toast.add({ severity: 'warn', summary: 'Permiso denegado', detail: 'Solo un administrador puede transferir IMEIs.', life: 4000 });
    showTransferDialog.value = false;
    return;
  }
  if (!imeiATransferir.value || !ubicacionDestino.value) return;
  try {
    await asignarImeisUbicacion(ubicacionDestino.value.id, [imeiATransferir.value]);
    await cargarImeis();
    toast.add({ severity: 'success', summary: 'IMEI transferido', detail: 'El IMEI fue transferido correctamente.', life: 3000 });
  } catch (e) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'No se pudo transferir el IMEI.', life: 4000 });
  }
  showTransferDialog.value = false;
  imeiATransferir.value = null;
  ubicacionDestino.value = null;
};

const verMotivo = async (imei) => {
  // Si ya tienes el motivo en imeis, puedes buscarlo localmente:
  const encontrado = imeis.value.find(i => i.imei === imei);
  if (encontrado && encontrado.motivo_devolucion) {
    motivoDevolucionView.value = encontrado.motivo_devolucion;
    showMotivoViewDialog.value = true;
    return;
  }
  // Si no, puedes pedirlo al backend:
  try {
    const res = await axios.get(`https://api.gpsubicacionapi.com/imeis/${imei}`);
    motivoDevolucionView.value = res.data.motivo_devolucion || 'Sin motivo registrado';
    showMotivoViewDialog.value = true;
  } catch (e) {
    motivoDevolucionView.value = 'No se pudo obtener el motivo.';
    showMotivoViewDialog.value = true;
  }
};
</script>



<style scoped>
.buscar-imei-container {
  margin: 2rem auto;
  color: var(--color-text, #fff);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  padding: 2rem 1.5rem;
}
.buscar-imei-title {
  margin-bottom: 1.5rem;
  color: var(--color-title, #bd3838);
  text-align: center;
}
.buscar-imei-filtros {
  display: flex;
  align-items: center;
  gap: 1rem;
  margin-bottom: 1rem;
}
.buscar-imei-input {
  flex: 1;
}
.buscar-imei-table {
  margin-top: 1rem;
}
.imei-devuelto {
  background: #ffe082;
  color: #795548;
  font-weight: bold;
}


</style>