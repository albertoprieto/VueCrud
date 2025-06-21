<template>
  <div class="registrar-container">
    <h2 class="registrar-title">Registrar IMEI</h2>
    <div class="registrar-card">
      <div class="form-group">
        <label for="imei">Número de IMEI:</label>
        <InputText v-model="imei" placeholder="Ingrese el número de IMEI" class="w-full" @keydown.enter="registerIMEI" />
      </div>
      <div class="actions-right">
        <Button label="Registrar" icon="pi pi-save" @click="registerIMEI" />
      </div>
    </div>

    <Dialog v-model:visible="showDialog" header="Registro Exitoso" :closable="false" :modal="true">
      <p>El IMEI ha sido registrado exitosamente.</p>
      <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
    </Dialog>

    <h3 class="registrar-subtitle">Últimos 5 IMEIs agregados</h3>
    <DataTable :value="lastIMEIs" responsiveLayout="scroll">
      <Column field="imei" header="IMEI" />
      <Column field="registeredBy" header="Registró" />
      <Column field="date" header="Fecha" />
      <Column field="status" header="Estado" />
    </DataTable>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { addIMEI, getIMEIs } from '@/services/imeiService';
import { registrarMovimiento } from '@/services/inventarioService';

const imei = ref('');
const imeis = ref([]);
const showDialog = ref(false);

const registerIMEI = async () => {
  if (!imei.value) return;
  await addIMEI({
    name: 'IMEI',
    imei: imei.value,
    // otros campos...
  });
  // REGISTRO DE MOVIMIENTO
  await registrarMovimiento({
    usuario: 'sistema', // o el usuario actual si tienes auth
    evento: 'alta',
    articulo_id: null,
    articulo_nombre: null,
    imei: imei.value,
    ubicacion_origen: null,
    ubicacion_destino: null,
    motivo: 'Registro de IMEI'
  });
  imei.value = '';
  await loadIMEIs();
  showDialog.value = true;
};

const closeDialog = () => {
  showDialog.value = false;
};

const loadIMEIs = async () => {
  imeis.value = await getIMEIs();
};

onMounted(loadIMEIs);

const lastIMEIs = computed(() => {
  if (!Array.isArray(imeis.value)) return [];
  return [...imeis.value]
    .sort((a, b) => new Date(b.date) - new Date(a.date))
    .slice(0, 5);
});
</script>

<style scoped>
.registrar-container {
  max-width: 500px;
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  background: #23272f;
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  color: #e4c8c8;
  text-align: center;
}
.registrar-title {
  text-align: center;
  margin-bottom: 2rem;
  color: #e4c8c8;
}
.registrar-card {
  background: #2d313a;
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
  margin-bottom: 2rem;
}
.form-group {
  margin-bottom: 1.5rem;
  text-align: left;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: #e4c8c8;
}
.w-full {
  width: 100%;
}
.actions-right {
  display: flex;
  justify-content: flex-end;
}
.registrar-subtitle {
  margin-top: 3rem;
  margin-bottom: 1rem;
  color: #e4c8c8;
}
</style>