<template>
  <Dialog :visible="visible" header="Agregar Reporte de Servicio" :modal="true" :closable="true" :style="{ width: '900px' }" @update:visible="val => emit('update:visible', val)" @hide="onClose">
    <ReporteServicio v-if="asignacionId" :key="asignacionId" />
  </Dialog>
</template>

<script setup>
import { defineProps, defineEmits, watch } from 'vue';
import Dialog from 'primevue/dialog';
import ReporteServicio from '@/modules/ReporteServicio.vue';

const props = defineProps({
  visible: Boolean,
  asignacionId: [Number, String]
});
const emit = defineEmits(['update:visible', 'close']);

function onClose() {
  emit('update:visible', false);
  emit('close');
}

watch(() => props.visible, (val) => {
  if (!val) emit('close');
});
</script>
