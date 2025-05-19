<template>
  <div class="cotizacion">
    <h2>Crear Cotización</h2>
    <div class="form-group">
      <label for="cliente">Nombre del Cliente:</label>
      <InputText v-model="cliente" placeholder="Ingrese el nombre del cliente" />
    </div>
    <div class="form-group">
      <label for="descripcion">Descripción:</label>
      <InputText v-model="descripcion" placeholder="Ingrese la descripción" />
    </div>
    <div class="form-group">
      <label for="monto">Monto:</label>
      <InputText v-model="monto" placeholder="Ingrese el monto" />
    </div>
    <Button label="Guardar Cotización" icon="pi pi-save" @click="saveQuotation" />

    <!-- Modal de confirmación -->
    <Dialog v-model:visible="showDialog" header="Cotización Guardada" :closable="false" :modal="true">
      <p>La cotización ha sido guardada exitosamente.</p>
      <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { addQuotation } from '@/services/quotationService';

const cliente = ref('');
const descripcion = ref('');
const monto = ref('');
const showDialog = ref(false);

const saveQuotation = async () => {
  if (!cliente.value || !descripcion.value || !monto.value) {
    alert('Por favor, complete todos los campos.');
    return;
  }

  try {
    await addQuotation({
      cliente: cliente.value,
      descripcion: descripcion.value,
      monto: parseFloat(monto.value),
      date: new Date().toISOString().split('T')[0],
      status: 'Pendiente'
    });
    showDialog.value = true;
    cliente.value = '';
    descripcion.value = '';
    monto.value = '';
  } catch (error) {
    alert('Error al registrar la cotización');
  }
};

const closeDialog = () => {
  showDialog.value = false;
};
</script>

<style scoped>
.cotizacion {
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