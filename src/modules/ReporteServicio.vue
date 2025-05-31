<template>
  <Dialog
    :visible="visible"
    @update:visible="emit('update:visible', $event)"
    header="Reporte de Servicio"
    :modal="true"
  >
    <div class="form-group">
      <label>Descripción del servicio</label>
      <Textarea v-model="form.descripcion" rows="3" class="w-full" />
    </div>
    <div class="form-group">
      <label>Observaciones</label>
      <Textarea v-model="form.observaciones" rows="2" class="w-full" />
    </div>
    <div class="modal-actions">
      <Button label="Guardar" icon="pi pi-save" @click="guardar" />
      <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" @click="cerrar" />
    </div>
  </Dialog>
</template>

<script setup>
import { ref } from 'vue';
import Dialog from 'primevue/dialog';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import { addReporteServicio } from '@/services/reportesServicio';

const props = defineProps({ asignacionId: Number, visible: Boolean });
const emit = defineEmits(['close', 'saved', 'update:visible']);
const form = ref({ descripcion: '', observaciones: '' });

function cerrar() {
  emit('update:visible', false);
  emit('close');
}
async function guardar() {
  await addReporteServicio({ ...form.value, asignacion_id: props.asignacionId });
  emit('saved');
  cerrar();
}
</script>