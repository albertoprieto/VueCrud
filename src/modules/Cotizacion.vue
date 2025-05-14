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
import { useQuotationStore } from '@/stores/quotationStore';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';

const cliente = ref('');
const descripcion = ref('');
const monto = ref('');
const showDialog = ref(false);

const quotationStore = useQuotationStore();

const saveQuotation = () => {
  if (!cliente.value || !descripcion.value || !monto.value) {
    alert('Por favor, complete todos los campos.');
    return;
  }

  quotationStore.addQuotation({
    cliente: cliente.value,
    descripcion: descripcion.value,
    monto: parseFloat(monto.value),
    date: new Date().toISOString().split('T')[0]
  });

  showDialog.value = true; // Mostrar el modal
  cliente.value = '';
  descripcion.value = '';
  monto.value = '';
};

const closeDialog = () => {
  showDialog.value = false; // Cerrar el modal
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