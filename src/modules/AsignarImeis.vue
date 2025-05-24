<template>
  <div class="asignar-imeis-container">
    <h2>Asignar IMEIs a Artículo</h2>
    <div class="form-card">
      <div class="form-group">
        <label for="articulo">Artículo:</label>
        <Dropdown
          id="articulo"
          v-model="selectedArticulo"
          :options="articulos"
          optionLabel="nombre"
          placeholder="Selecciona artículo"
          class="w-full"
        />
      </div>
      <div class="form-group">
        <label for="imeis">IMEIs:</label>
        <Textarea
          id="imeis"
          v-model="imeisInput"
          placeholder="Escanea o pega los IMEIs, uno por línea"
          rows="8"
          class="w-full"
        />
      </div>
      <div class="form-actions">
        <Button label="Registrar y asignar IMEIs" icon="pi pi-save" @click="registrarYAsignar" class="p-button-success" />
      </div>
    </div>
    <Dialog v-model:visible="showDialog" header="Resultado" :modal="true" :closable="false">
      <p>{{ mensaje }}</p>
      <div class="dialog-actions">
        <Button label="Aceptar" icon="pi pi-check" @click="showDialog = false" autofocus />
      </div>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import Dropdown from 'primevue/dropdown';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import { getArticulos } from '@/services/articulosService';
import { registrarYAsignarIMEIsPorNombre } from '@/services/imeiService';

const articulos = ref([]);
const selectedArticulo = ref(null);
const imeisInput = ref('');
const mensaje = ref('');
const showDialog = ref(false);

onMounted(async () => {
  articulos.value = await getArticulos();
});

const registrarYAsignar = async () => {
  if (!selectedArticulo.value || !imeisInput.value) return;
  const imeis = imeisInput.value.split('\n').map(i => i.trim()).filter(Boolean);
  try {
    await registrarYAsignarIMEIsPorNombre(selectedArticulo.value.nombre, imeis);
    mensaje.value = `${imeis.length} IMEIs asignados al artículo "${selectedArticulo.value.nombre}" correctamente.`;
  } catch (e) {
    mensaje.value = 'Ocurrió un error al asignar los IMEIs.';
  }
  showDialog.value = true;
  imeisInput.value = '';
};
</script>

<style scoped>
.asignar-imeis-container {
  max-width: 500px;
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  color: var(--color-text);
}
h2 {
  text-align: center;
  margin-bottom: 2rem;
  color: var(--color-title);
  /* Rosa opaco llamativo */
}
.form-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
.form-group {
  margin-bottom: 1.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: 600;
  color: var(--color-title);
}
.w-full {
  width: 100%;
}
.form-actions {
  display: flex;
  justify-content: flex-end;
}
.dialog-actions {
  display: flex;
  justify-content: flex-end;
  margin-top: 1.5rem;
}
</style>