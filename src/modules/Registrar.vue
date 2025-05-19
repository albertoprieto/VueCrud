<template>
  <div class="registrar">
    <h2>Registrar IMEI</h2>
    <div class="form-group">
      <label for="imei">Número de IMEI:</label>
      <InputText v-model="imei" placeholder="Ingrese el número de IMEI" />
    </div>
    <Button label="Registrar" icon="pi pi-save" @click="registerIMEI" />

    <!-- Modal de confirmación -->
    <Dialog v-model:visible="showDialog" header="Registro Exitoso" :closable="false" :modal="true">
      <p>El IMEI ha sido registrado exitosamente.</p>
      <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useLoginStore } from '@/stores/loginStore';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { addIMEI } from '@/services/imeiService';

const imei = ref('');
const showDialog = ref(false);
const loginStore = useLoginStore();

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
      description: `Registrado por ${currentUser}`,
      imei: imei.value,
      registeredBy: currentUser,
      date: `${currentDate} ${currentTime}`,
      status: 'Disponible'
    });
    showDialog.value = true;
    imei.value = '';
  } catch (error) {
    alert('Error al registrar el IMEI');
  }
};

const closeDialog = () => {
  showDialog.value = false;
};
</script>

<style scoped>
.registrar {
  max-width: 400px;
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