<template>
  <div class="registrar">
    <h2 style="color:#debdc9;">Registrar IMEI</h2>
    <div class="form-group">
      <label for="imei" >Número de IMEI:</label>
      <InputText v-model="imei" placeholder="Ingrese el número de IMEI" @keydown.enter="registerIMEI" />
    </div>
    <Button label="Registrar" icon="pi pi-save" @click="registerIMEI" />

    <!-- Modal de confirmación -->
    <Dialog v-model:visible="showDialog" header="Registro Exitoso" :closable="false" :modal="true">
      <p>El IMEI ha sido registrado exitosamente.</p>
      <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
    </Dialog>

    <!-- Últimos 5 IMEIs agregados -->
    <h3 style="margin-top:4rem; color:#debdc9;">Últimos 5 IMEIs agregados</h3>
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
import { useLoginStore } from '@/stores/loginStore';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import DataTable from 'primevue/datatable';
import Column from 'primevue/column';
import { addIMEI, getIMEIs } from '@/services/imeiService';

const imei = ref('');
const showDialog = ref(false);
const loginStore = useLoginStore();
const imeis = ref([]);

const registerIMEI = async () => {
  if (!imei.value) {
    alert('Por favor, ingrese un número de IMEI.');
    return;
  }

  const currentUser = loginStore.currentUser?.username || 'Desconocido';
  const now = new Date();
  const currentDate = now.toISOString().split('T')[0];
  const currentTime = now.toTimeString().split(' ')[0];

  try {
    await addIMEI({
      name: 'IMEI',
      description: `${currentUser}`,
      imei: imei.value,
      registeredBy: currentUser,
      date: `${currentDate} ${currentTime}`,
      status: 'Disponible'
    });
    showDialog.value = true;
    imei.value = '';
    await loadIMEIs();
  } catch (error) {
    alert('Error al registrar el IMEI');
  }
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
.registrar {
  margin: 0 auto;
  text-align: center;
}

.form-group {
  margin-bottom: 1rem;
}

label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
}
</style>