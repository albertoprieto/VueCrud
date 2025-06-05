<template>
  <div class="reporte">
    <h2>Hoja de Servicio - Instalación de GPS</h2>
    <div class="form-group">
      <label for="modelo">Modelo del Vehículo:</label>
      <InputText v-model="modelo" placeholder="Ingrese el modelo del vehículo" />
    </div>
    <div class="form-group">
      <label for="placa">Placa del Vehículo:</label>
      <InputText v-model="placa" placeholder="Ingrese la placa del vehículo" />
    </div>
    <div class="form-group">
      <label for="nombre">Nombre del Cliente:</label>
      <InputText v-model="nombre" placeholder="Ingrese el nombre del cliente" />
    </div>
    <Button label="Generar Reporte" icon="pi pi-file" @click="generateReport" />

    <!-- Modal de confirmación -->
    <Dialog v-model:visible="showDialog" header="Reporte Generado" :closable="false" :modal="true">
      <p>El reporte ha sido generado exitosamente.</p>
      <p><strong>Modelo:</strong> {{ modelo }}</p>
      <p><strong>Placa:</strong> {{ placa }}</p>
      <p><strong>Cliente:</strong> {{ nombre }}</p>
      <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useReportesStore } from '@/stores/reportesStore';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { useToast } from 'primevue/usetoast';

const modelo = ref('');
const placa = ref('');
const nombre = ref('');
const showDialog = ref(false);

const reportesStore = useReportesStore();
const toast = useToast();

const generateReport = () => {
  if (!modelo.value || !placa.value || !nombre.value) {
    toast.add({
      severity: 'warn',
      summary: 'Campos obligatorios',
      detail: 'Por favor, complete todos los campos.',
      life: 4000
    });
    return;
  }

  // Guardar el reporte en el store
  reportesStore.addReporte({
    modelo: modelo.value,
    placa: placa.value,
    cliente: nombre.value
  });

  showDialog.value = true; // Mostrar el modal
};

const closeDialog = () => {
  showDialog.value = false; // Cerrar el modal
  modelo.value = '';
  placa.value = '';
  nombre.value = '';
};
</script>

<style scoped>
.reporte {
  max-width: 600px;
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