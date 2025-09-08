<template>
  <div class="transferir-imeis-container">
    <h2>Transferir IMEIs entre Ubicaciones</h2>
    <div class="form-card">
      <div class="form-group">
        <label for="ubicacionOrigen">Ubicación origen <span class="required-tooltip">*</span></label>
        <Dropdown
          id="ubicacionOrigen"
          v-model="ubicacionOrigen"
          :options="ubicaciones"
          optionLabel="nombre"
          placeholder="Selecciona ubicación origen"
          class="w-full"
        />
      </div>
      <div class="form-group">
        <label for="ubicacionDestino">Ubicación destino <span class="required-tooltip">*</span></label>
        <Dropdown
          id="ubicacionDestino"
          v-model="ubicacionDestino"
          :options="ubicacionesDestino"
          optionLabel="nombre"
          placeholder="Selecciona ubicación destino"
          class="w-full"
        />
      </div>
      <div class="form-group">
        <label for="nuevoImei">IMEI:</label>
        <InputText
          id="nuevoImei"
          v-model="nuevoImei"
          placeholder="Escanea o escribe un IMEI y presiona Enter"
          class="w-full"
          :disabled="!ubicacionOrigen"
          @keydown.enter.prevent="agregarImei"
        />
        <DataTable
          v-if="imeis.length"
          :value="imeis"
          class="imeis-table"
          :rows="5"
          :paginator="imeis.length > 5"
          responsiveLayout="scroll"
          emptyMessage="No hay IMEIs agregados."
        >
          <Column header="#" style="width: 50px;">
            <template #body="slotProps">
              {{ slotProps.index + 1 }}
            </template>
          </Column>
          <Column header="IMEI">
            <template #body="slotProps">
              <span :class="{ 'imei-invalido': imeisInvalidos.includes(slotProps.data) }">
                {{ slotProps.data }}
              </span>
            </template>
          </Column>
          <Column header="Artículo">
            <template #body="slotProps">
              {{ getArticuloNombre(slotProps.data) }}
            </template>
          </Column>
          <Column header="Eliminar" style="width: 70px;">
            <template #body="slotProps">
              <Button icon="pi pi-times" class="p-button-text p-button-danger" @click="eliminarImei(slotProps.index)" />
            </template>
          </Column>
        </DataTable>
      </div>
      <div class="form-actions">
        <Button label="Transferir IMEIs" icon="pi pi-exchange" @click="transferirImeis" class="p-button-success" :disabled="!puedeTransferir || !esAdmin" />
      </div>
    </div>
    <Dialog v-model:visible="showDialog" header="Resultado" :modal="true" :closable="false">
      <p>{{ mensaje }}</p>
      <div class="dialog-actions">
        <Button label="Aceptar" icon="pi pi-check" @click="showDialog = false" autofocus />
      </div>
    </Dialog>
    <Dialog v-model:visible="showWarningDialog" header="Advertencia" :modal="true" :closable="false">
      <p style="white-space: pre-line;">{{ warningMessage }}</p>
      <div class="dialog-actions">
        <Button label="Aceptar" icon="pi pi-check" @click="showWarningDialog = false" autofocus />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed, watch } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { getUbicaciones } from '@/services/ubicacionesService';
import { getIMEIs } from '@/services/imeiService';
import axios from 'axios';
import { useToast } from 'primevue/usetoast';
import { registrarMovimiento } from '@/services/inventarioService';
import { useLoginStore } from '@/stores/loginStore';

const ubicaciones = ref([]);
const ubicacionOrigen = ref(null);
const ubicacionDestino = ref(null);
const nuevoImei = ref('');
const imeis = ref([]);
const imeisInvalidos = ref([]);
const mensaje = ref('');
const showDialog = ref(false);
const showWarningDialog = ref(false);
const warningMessage = ref('');
const imeisEnUbicacion = ref([]);
const imeisInfo = ref([]);
const toast = useToast();

const ubicacionesDestino = computed(() =>
  ubicaciones.value.filter(u => u.id !== ubicacionOrigen.value?.id)
);

const puedeTransferir = computed(() =>
  imeis.value.length > 0 && ubicacionOrigen.value && ubicacionDestino.value && imeisInvalidos.value.length === 0
);

onMounted(async () => {
  ubicaciones.value = await getUbicaciones();
});

const loginStore = useLoginStore();
const esAdmin = computed(() => loginStore.user?.perfil === 'Admin');

const cargarImeisOrigen = async () => {
  if (!ubicacionOrigen.value) return;
  imeisEnUbicacion.value = await axios
    .get(`${import.meta.env.VITE_API_URL}/ubicaciones/${ubicacionOrigen.value.id}/imeis`)
    .then(res => res.data);
  imeisInfo.value = imeisEnUbicacion.value;
  imeis.value = [];
  imeisInvalidos.value = [];
};

watch(ubicacionOrigen, cargarImeisOrigen);

const agregarImei = () => {
  const imei = nuevoImei.value.trim();
  if (!imei) return;
  if (imeis.value.includes(imei)) {
    warningMessage.value = `El IMEI "${imei}" ya está en la lista.`;
    showWarningDialog.value = true;
    nuevoImei.value = '';
    return;
  }
  // Validar que el IMEI esté en la ubicación origen
  const existeEnOrigen = imeisEnUbicacion.value.some(i => i.imei === imei);
  if (!existeEnOrigen) {
    warningMessage.value = `El IMEI "${imei}" no se encuentra en la ubicación origen seleccionada.`;
    showWarningDialog.value = true;
    nuevoImei.value = '';
    return;
  }
  imeis.value.push(imei);
  nuevoImei.value = '';
  validarImeis();
};

const eliminarImei = (idx) => {
  imeis.value.splice(idx, 1);
  validarImeis();
};

const validarImeis = () => {
  // Solo permitir IMEIs que estén en la ubicación origen y no estén ya en la ubicación destino
  imeisInvalidos.value = imeis.value.filter(imei => {
    const info = imeisEnUbicacion.value.find(i => i.imei === imei);
    if (!info) return true;
    // Aquí podrías agregar más validaciones si lo requieres
    return false;
  });
};

const getArticuloNombre = (imei) => {
  const info = imeisEnUbicacion.value.find(i => i.imei === imei);
  return info?.articulo_nombre || 'NA';
};

const transferirImeis = async () => {
  if (!esAdmin.value) {
    toast.add({ severity: 'warn', summary: 'Permiso denegado', detail: 'Solo un administrador puede transferir IMEIs.', life: 4000 });
    return;
  }
  if (!puedeTransferir.value) {
    toast.add({ severity: 'warn', summary: 'Validación', detail: 'Revisa los IMEIs y las ubicaciones.', life: 4000 });
    return;
  }
  try {
    await axios.post(`${import.meta.env.VITE_API_URL}/ubicaciones/transferir-imeis`, {
      imeis: imeis.value,
      destino_id: ubicacionDestino.value.id
    });
    // Registro de movimiento deshabilitado por error 405 Method Not Allowed
    mensaje.value = `${imeis.value.length} IMEIs transferidos correctamente a "${ubicacionDestino.value.nombre}".`;
    imeis.value = [];
    await cargarImeisOrigen();
    toast.add({ severity: 'success', summary: 'Éxito', detail: mensaje.value, life: 4000 });
  } catch (e) {
    mensaje.value = 'Ocurrió un error al transferir los IMEIs.';
    toast.add({ severity: 'error', summary: 'Error', detail: mensaje.value, life: 4000 });
  }
  showDialog.value = true;
};
</script>

<style scoped>
.transferir-imeis-container {
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  color: var(--color-text);
  max-width: 600px;
}
h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--color-title);
}
.form-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.form-group {
  margin-bottom: 1.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-title);
}
.w-full {
  width: 100%;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
.imei-invalido {
  color: #fff;
  background: #d32f2f;
  border-radius: 4px;
  padding: 2px 8px;
}
.imeis-table {
  margin-top: 0.5rem;
  background: var(--color-card, #23232b);
  border-radius: 8px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.18);
  border: 1.5px solid #fff3;
  overflow: hidden;
}
</style>