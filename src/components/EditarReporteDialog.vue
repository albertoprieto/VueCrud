<template>
  <Dialog :visible="!!reporte" header="Editar Reporte de Servicio" :modal="true" @update:visible="$emit('cerrar')">
    <form v-if="form" @submit.prevent="guardar">
      <div class="form-group">
        <label>Tipo de Servicio</label>
        <InputText v-model="form.tipo_servicio" class="w-full" />
      </div>
      <div class="form-group">
        <label>Fecha</label>
        <input type="date" v-model="fechaStr" class="w-full" />
      </div>
      <div class="form-group">
        <label>Vendedor</label>
        <InputText v-model="form.vendedor" class="w-full" />
      </div>
      <div class="form-group">
        <label>Lugar / Centro de instalación</label>
        <InputText v-model="form.lugar_instalacion" class="w-full" />
      </div>
      <h4 class="section-title">Datos del vehículo</h4>
      <div class="form-group">
        <InputText v-model="form.marca" placeholder="Marca" class="w-full mb-2" />
        <InputText v-model="form.submarca" placeholder="Submarca" class="w-full mb-2" />
        <InputText v-model="form.modelo" placeholder="Modelo" class="w-full mb-2" />
        <InputText v-model="form.placas" placeholder="Placa" class="w-full mb-2" />
        <InputText v-model="form.color" placeholder="Color" class="w-full mb-2" />
        <InputText v-model="form.numero_economico" placeholder="Número económico" class="w-full mb-2" />
      </div>
      <h4 class="section-title">Datos del dispositivo</h4>
      <div class="form-group">
        <InputText v-model="form.modelo_gps" placeholder="Modelo GPS" class="w-full mb-2" />
        <InputText v-model="form.imei" placeholder="IMEI" class="w-full mb-2" />
        <InputText v-model="form.sim_serie" placeholder="SIM" class="w-full mb-2" />
        <InputText v-model="form.accesorios" placeholder="Accesorios adicionales" class="w-full mb-2" />
        <InputText v-model="form.ubicacion_gps" placeholder="Ubicación del GPS" class="w-full mb-2" />
        <InputText v-model="form.ubicacion_bloqueo" placeholder="Ubicación del Bloqueo" class="w-full mb-2" />
      </div>
      <div class="form-group">
        <label>Observaciones</label>
        <InputText v-model="form.observaciones" class="w-full" />
      </div>
      <h4 class="section-title">Datos del cobro</h4>
      <div class="form-group">
        <label>Total a cobrar</label>
        <InputText v-model="form.total" class="w-full mb-2" />
      </div>
      <div class="form-group">
        <label>Método de pago</label>
        <InputText v-model="form.forma_pago" class="w-full mb-2" disabled />
      </div>
      <div class="form-group">
        <label>Monto cobrado por el técnico</label>
        <InputText v-model="form.monto_tecnico" type="number" class="w-full mb-2" />
      </div>
      <div class="form-group">
        <label>Viáticos</label>
        <InputText v-model="form.viaticos" type="number" class="w-full mb-2" />
      </div>
      <div class="modal-actions">
        <Button label="Guardar" icon="pi pi-save" type="submit" :loading="guardando" :disabled="guardando" />
        <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary ml-2" @click="$emit('cerrar')" type="button" :disabled="guardando" />
      </div>
    </form>
  </Dialog>
</template>

<script setup>
import { ref, computed, watch } from 'vue';
import axios from 'axios';
import Dialog from 'primevue/dialog';
import Button from 'primevue/button';
import InputText from 'primevue/inputtext';
import { useToast } from 'primevue/usetoast';
import { getNotaById, actualizarCamposNota } from '@/services/pagosService';

// reporte: fila a editar (null = cerrado). notaId: nota que lo agrupa, si tiene.
const props = defineProps({
  reporte: { type: Object, default: null },
  notaId: { type: Number, default: null },
});
const emit = defineEmits(['cerrar', 'guardado']);

const toast = useToast();
const form = ref(null);
const guardando = ref(false);

watch(() => props.reporte, (r) => { form.value = r ? { ...r } : null; });

const fechaStr = computed({
  get: () => form.value?.fecha ? String(form.value.fecha).slice(0, 10) : '',
  set: (val) => { form.value.fecha = val; },
});

async function guardar() {
  guardando.value = true;
  try {
    await axios.put(`${import.meta.env.VITE_API_URL}/reportes-servicio/${form.value.id}`, form.value);

    // La nota suma varios reportes: se ajusta por la diferencia, no se pisa
    // con el total de este reporte.
    const diferencia = (Number(form.value.total) || 0) - (Number(props.reporte.total) || 0);
    if (props.notaId && diferencia) {
      try {
        const nota = await getNotaById(props.notaId);
        await actualizarCamposNota(props.notaId, { total: (Number(nota.total) || 0) + diferencia });
      } catch {
        toast.add({ severity: 'warn', summary: 'Aviso', detail: 'El reporte se guardó, pero no se pudo actualizar el total de la nota asociada.', life: 4500 });
      }
    }

    toast.add({ severity: 'success', summary: 'Actualizado', detail: 'Reporte actualizado correctamente.', life: 3000 });
    emit('guardado', form.value);
  } catch {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al guardar los cambios.', life: 4000 });
  }
  guardando.value = false;
}
</script>

<style scoped>
.form-group {
  margin-bottom: 1rem;
  text-align: left;
}
.w-full {
  width: 100%;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 1.5rem;
}
</style>
