<template>
  <div class="crear-evento">
    <h2>Crear Evento</h2>
    <div class="form-group">
      <label for="titulo">Título del Evento:</label>
      <InputText v-model="titulo" placeholder="Ingrese el título del evento" />
    </div>
    <div class="form-group">
      <label for="fecha">Fecha del Evento:</label>
      <Calendar v-model="fecha" placeholder="Seleccione una fecha" />
    </div>
    <Button label="Guardar Evento" icon="pi pi-save" @click="saveEvent" />

    <!-- Modal de confirmación -->
    <Dialog v-model:visible="showDialog" header="Evento Guardado" :closable="false" :modal="true">
      <p>El evento ha sido guardado exitosamente.</p>
      <Button label="Aceptar" icon="pi pi-check" @click="closeDialog" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useEventosStore } from '@/stores/eventosStore';
import InputText from 'primevue/inputtext';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import Calendar from 'primevue/calendar';

const titulo = ref('');
const fecha = ref(null);
const showDialog = ref(false);

const eventosStore = useEventosStore();

const saveEvent = () => {
  if (!titulo.value || !fecha.value) {
    alert('Por favor, complete todos los campos.');
    return;
  }

  // Registrar el evento en el store de eventos
  eventosStore.addEvento({
    titulo: titulo.value,
    fecha: fecha.value
  });

  showDialog.value = true; // Mostrar el modal de confirmación
  titulo.value = ''; // Limpiar el campo de título
  fecha.value = null; // Limpiar el campo de fecha
};

const closeDialog = () => {
  showDialog.value = false; // Cerrar el modal
};
</script>

<style scoped>
.crear-evento {
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