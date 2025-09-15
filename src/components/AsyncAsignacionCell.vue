<template>
  <span v-if="loading">Cargando...</span>
  <span v-else>
    <span>{{ asignacion.fecha_servicio || '-' }} {{ asignacion.hora_servicio || '' }}</span>
    <Button v-if="asignacion.venta_id" icon="pi pi-pencil" class="p-button-sm p-button-text ml-2" @click="emitEdit" />
  </span>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import { getAsignacionVenta } from '@/services/asignacionesService';
import Button from 'primevue/button';

const props = defineProps({ ventaId: Number });
const emit = defineEmits(['edit']);
const asignacion = ref({});
const loading = ref(true);

onMounted(async () => {
  loading.value = true;
  try {
    asignacion.value = await getAsignacionVenta(props.ventaId);
  } catch (e) {
    asignacion.value = {};
  }
  loading.value = false;
});

function emitEdit() {
  emit('edit', { ventaId: props.ventaId, asignacion: asignacion.value });
}
</script>
