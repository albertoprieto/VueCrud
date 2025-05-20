<template>
  <div class="header">
    <h2 style="color:#debdc9;">Crear Cotización</h2>
  </div>
  <div class="cotizacion">
    <form @submit.prevent="saveQuotation">
      <div class="form-section">
        <h4>Generales</h4>
        <div class="form-row">
          <div class="form-group">
            <label for="tipo">Tipo de cotización:</label>
            <Dropdown v-model="tipo" :options="tiposCotizacion" placeholder="Selecciona tipo" />
          </div>
          <div class="form-group">
            <label for="modelo">Modelo de GPS:</label>
            <Dropdown v-model="modelo" :options="modelosGPS" placeholder="Selecciona modelo" />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h4>Datos del Cliente</h4>
        <div class="form-row">
          <div class="form-group">
            <label for="cliente">Nombre del Cliente:</label>
            <InputText v-model="cliente" placeholder="Ingrese el nombre del cliente" />
          </div>
          <div class="form-group">
            <label for="telefono">Teléfono:</label>
            <InputText v-model="telefono" placeholder="10 dígitos" />
          </div>
        </div>
        <div class="form-row">
          <div class="form-group">
            <label for="correo">Correo electrónico:</label>
            <InputText v-model="correo" placeholder="Opcional" />
          </div>
        </div>
      </div>

      <div class="form-section">
        <h4>Detalles adicionales</h4>
        <div class="form-row">
          <div class="form-group">
            <label for="descripcion">Descripción:</label>
            <InputText v-model="descripcion" placeholder="Detalle del servicio o producto" />
          </div>

          <div class="form-group">
            <label for="observaciones">Observaciones:</label>
            <InputText v-model="observaciones" placeholder="Opcional" />
          </div>
        </div>
      </div>


      <div class="form-section">
        <h4>Datos de la cotización</h4>
 
        <div class=" actions-right">
          <div class="form-row">
            <div class="form-group">
              <label for="monto">Monto total:</label>
              <InputNumber v-model="monto" placeholder="Ingrese el monto total" />
            </div>
          </div>
        </div>

      </div>
      <div class="actions-right">
        <Button label="Guardar Cotización" icon="pi pi-save" type="submit" />
      </div>
    </form>

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
import Dropdown from 'primevue/dropdown';
import InputNumber from 'primevue/inputnumber';
import { addQuotation } from '@/services/quotationService';

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
  // Validaciones
  if (
    !cliente.value ||
    !telefono.value ||
    !descripcion.value ||
    !modelo.value ||
    !tipo.value ||
    !monto.value
  ) {
    alert('Por favor, complete todos los campos obligatorios.');
    return;
  }
  if (!/^\d{10}$/.test(telefono.value)) {
    alert('El teléfono debe tener 10 dígitos numéricos.');
    return;
  }
  if (correo.value && !/^[\w-.]+@([\w-]+\.)+[\w-]{2,4}$/.test(correo.value)) {
    alert('Ingrese un correo electrónico válido.');
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
    alert('Error al registrar la cotización');
  }
};

const closeDialog = () => {
  showDialog.value = false;
};
</script>

<style scoped>
.header {
  max-width: 700px;
  margin: 0 auto;
  text-align: left;
  padding: .5rem .1rem;
}

.cotizacion {
  max-width: 700px;
  margin: 0 auto;
  text-align: left;
  padding: .5rem .1rem;
}

form {
  width: 100%;
}

.form-section {
  margin-bottom: 2rem;
  border-bottom: 1px solid #444;
  padding-bottom: 1rem;
}

.form-section:last-child {
  border-bottom: none;
}

.form-section h4 {
  color: #e91e63;
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
}

@media (max-width: 700px) {
  .form-row {
    flex-direction: column;
    gap: 0.5rem;
  }

  .cotizacion {
    padding: 1rem 0.2rem;
  }
}

.actions-right {
  display: flex;
  justify-content: flex-end;
  margin-top: 1rem;
}
</style>