<template>
  <div class="cotizacion-container">
    <h2 class="cotizacion-title">Crear Cotización</h2>
    <div class="cotizacion-card">
      <form @submit.prevent="saveQuotation">
        <div class="form-section">
          <h4>Generales</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="tipo">Tipo de cotización:</label>
              <Dropdown v-model="tipo" :options="tiposCotizacion" placeholder="Selecciona tipo" class="w-full" />
            </div>
            <div class="form-group">
              <label for="modelo">Modelo de GPS:</label>
              <Dropdown v-model="modelo" :options="modelosGPS" placeholder="Selecciona modelo" class="w-full" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h4>Datos del Cliente</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="cliente">Nombre del Cliente:</label>
              <InputText v-model="cliente" placeholder="Ingrese el nombre del cliente" class="w-full" />
            </div>
            <div class="form-group">
              <label for="telefono">Teléfono:</label>
              <InputText v-model="telefono" placeholder="10 dígitos" class="w-full" />
            </div>
          </div>
          <div class="form-row">
            <div class="form-group">
              <label for="correo">Correo electrónico:</label>
              <InputText v-model="correo" placeholder="Opcional" class="w-full" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h4>Detalles adicionales</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="descripcion">Descripción:</label>
              <InputText v-model="descripcion" placeholder="Detalle del servicio o producto" class="w-full" />
            </div>
            <div class="form-group">
              <label for="observaciones">Observaciones:</label>
              <InputText v-model="observaciones" placeholder="Opcional" class="w-full" />
            </div>
          </div>
        </div>

        <div class="form-section">
          <h4>Datos de la cotización</h4>
          <div class="form-row">
            <div class="form-group">
              <label for="monto">Monto total:</label>
              <InputNumber v-model="monto" placeholder="Ingrese el monto total" class="w-full" />
            </div>
          </div>
        </div>

        <div class="actions-right">
          <Button label="Guardar Cotización" icon="pi pi-save" type="submit" />
        </div>
      </form>
    </div>

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
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import { addQuotation } from '@/services/quotationService';
import { useToast } from 'primevue/usetoast';

const toast = useToast();

const cliente = ref('');
const telefono = ref('');
const correo = ref('');
const descripcion = ref('');
const modelo = ref('');
const modelosGPS = [
  'Ninguno',
  'GPS TK303',
  'GPS GT06N',
  'GPS Coban',
  'GPS Teltonika',
  'GPS Queclink'
];
const tipo = ref('');
const tiposCotizacion = [
  'Venta',
  'Instalación/Servicio',
  'Mixto'
];
const monto = ref('');
const observaciones = ref('');
const showDialog = ref(false);

const saveQuotation = async () => {
  if (
    !cliente.value ||
    !telefono.value ||
    !descripcion.value ||
    !modelo.value ||
    !tipo.value ||
    !monto.value
  ) {
    toast.add({ severity: 'warn', summary: 'Campos obligatorios', detail: 'Por favor, complete todos los campos obligatorios.', life: 4000 });
    return;
  }
  if (!/^\d{10}$/.test(telefono.value)) {
    toast.add({ severity: 'warn', summary: 'Teléfono inválido', detail: 'El teléfono debe tener 10 dígitos numéricos.', life: 4000 });
    return;
  }
  if (correo.value && !/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(correo.value)) {
    toast.add({ severity: 'warn', summary: 'Correo inválido', detail: 'Ingrese un correo electrónico válido.', life: 4000 });
    return;
  }

  try {
    await addQuotation({
      cliente: cliente.value,
      telefono: telefono.value,
      correo: correo.value,
      descripcion: descripcion.value,
      modelo: modelo.value,
      tipo: tipo.value,
      monto: monto.value,
      observaciones: observaciones.value,
      fecha: new Date().toISOString().split('T')[0],
      status: 'Pendiente'
    });
    showDialog.value = true;
    cliente.value = '';
    telefono.value = '';
    correo.value = '';
    descripcion.value = '';
    modelo.value = '';
    tipo.value = '';
    monto.value = '';
    observaciones.value = '';
  } catch (error) {
    toast.add({ severity: 'error', summary: 'Error', detail: 'Error al registrar la cotización', life: 4000 });
  }
};

const closeDialog = () => {
  showDialog.value = false;
};
</script>

<style scoped>
.cotizacion-container {
  max-width: 700px;
  margin: 2rem auto;
  padding: 2rem 1.5rem;
  background: var(--color-bg);
  border-radius: 12px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.10);
  color: var(--color-text);
}
.cotizacion-title {
  text-align: center;
  margin-bottom: .5rem;
  color: var(--color-title); /* rosa opaco llamativo */
}
.cotizacion-card {
  background: var(--color-card);
  border-radius: 8px;
  padding: 1.5rem;
  box-shadow: 0 2px 8px rgba(0,0,0,0.08);
}
form {
  width: 100%;
}
.form-section {
  margin-bottom: .5rem;
  border-bottom: 1px solid var(--color-border);
  padding-bottom: 1rem;
}
.form-section:last-child {
  border-bottom: none;
}
.form-section h4 {
  color: var(--color-title); /* rosa opaco llamativo */
  margin-bottom: 1rem;
  margin-top: 0;
}
.form-row {
  display: flex;
  gap: 1.5rem;
  flex-wrap: wrap;
  margin-bottom: 1rem;
}
.form-group {
  flex: 1 1 220px;
  min-width: 220px;
  margin-bottom: 0.5rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-title); /* rosa opaco llamativo */
}
.w-full {
  width: 100%;
}
.actions-right {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
@media (max-width: 700px) {
  .cotizacion-container {
    padding: 1rem 0.2rem;
  }
  .form-row {
    flex-direction: column;
    gap: 0.5rem;
  }
}
</style>