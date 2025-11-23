<template>
  <div class="nuevo-reporte-servicio-container">
    <h2 class="reporte-title">Nuevo Reporte de Servicio</h2>
    <div class="reporte-fields">
      <!-- Encabezado principal, Tipo de servicio y Cliente en una sola columna -->
      <div class="full-width-row">
        <h3 class="section-header">Reporte de Servicio</h3>
      </div>
      <div class="full-width-row">
        <div class="field-group">
          <label class="required-label">Tipo de servicio</label>
          <Dropdown v-model="tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full mb-4" />
        </div>
      </div>
      <div class="full-width-row">
        <div class="field-group">
          <label class="required-label">Cliente</label>
          <Dropdown
            v-model="cliente"
            :options="clientes"
            optionLabel="nombre"
            optionValue="id"
            placeholder="Selecciona cliente"
            class="w-full mb-4"
            filter
            :filterPlaceholder="'Buscar cliente'"
          />
        </div>
      </div>

      <div class="row-group">
        <div class="field-group" v-if="plataformasOptions.length" style="flex:1; margin-right:1rem;">
          <label>Plataforma</label>
          <Dropdown v-model="plataforma" :options="plataformasOptions" placeholder="Selecciona plataforma" class="w-full mb-4" />
        </div>
        <div class="field-group" style="flex:1;">
            <label>Lugar / Centro de instalación</label>
          <InputText v-model="lugar_instalacion" class="w-full" placeholder="Opcional" />
        </div>
      </div>
      <div class="row-group">
        <div class="field-group" v-if="usuariosOptions.length" style="flex:1; margin-right:1rem;">
          <label>Usuario</label>
          <Dropdown v-model="usuario" :options="usuariosOptions" placeholder="Selecciona usuario" class="w-full mb-4" />
        </div>
        <div class="field-group" style="flex:1;">
          <label class="required-label">Ubicación</label>
          <Dropdown v-model="ubicacion" :options="ubicaciones" optionLabel="nombre" optionValue="id" placeholder="Selecciona ubicación" class="w-full mb-4" />
        </div>
      </div>      
      <div class="full-width-row"><h4 class="section-header">Asignación de IMEIs y SIM</h4></div>
      <div class="field-group">
        <label>IMEI 1</label>
        <Dropdown
          v-if="imeiOptions.length"
          v-model="imei"
          :options="imeiOptions"
          optionLabel="label"
          optionValue="imei"
          placeholder="Selecciona IMEI"
          class="w-full mb-4"
          filter
          :filterPlaceholder="'Buscar por últimos 6 dígitos'"
          :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
        />
        <InputText v-else v-model="imei" class="w-full mb-4" placeholder="Captura IMEI manualmente" />
      </div>
      <div class="field-group">
        <label>SIM 1</label>
        <Dropdown
          v-if="simOptions.length"
          v-model="sim"
          :options="simOptions"
          optionLabel="label"
          optionValue="imei"
          placeholder="Selecciona SIM"
          class="w-full mb-4"
          filter
          :filterPlaceholder="'Buscar por últimos 6 dígitos'"
          :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
        />
        <InputText v-else v-model="sim" class="w-full mb-4" placeholder="Captura SIM manualmente" />
      </div>
      <div class="full-width-row"><h4 class="section-header">Datos del vehículo</h4></div>
      <div class="field-group">
        <label>Marca</label>
        <InputText v-model="marca" class="w-full" placeholder="Marca" />
      </div>
      <div class="field-group">
        <label>Submarca</label>
        <InputText v-model="submarca" class="w-full" placeholder="Submarca" />
      </div>
      <div class="field-group">
        <label>Modelo</label>
        <InputText v-model="modelo" class="w-full" placeholder="Modelo" />
      </div>
      <div class="field-group">
        <label>Placas</label>
        <InputText v-model="placas" class="w-full" placeholder="Placas" />
      </div>
      <div class="field-group">
        <label>Color</label>
        <InputText v-model="color" class="w-full" placeholder="Color" />
      </div>
      <div class="field-group">
        <label>Número económico</label>
        <InputText v-model="numero_economico" class="w-full" placeholder="Número económico" />
      </div>
      <div class="full-width-row"><h4 class="section-header">Datos del dispositivo (opcionales)</h4></div>
      <div class="field-group">
        <label>Modelo GPS</label>
        <InputText v-model="modelo_gps" class="w-full" placeholder="Modelo GPS" />
      </div>
      <div class="field-group">
        <label>Accesorios adicionales (Botón/Micro/Etc.)</label>
        <InputText v-model="accesorios" class="w-full" placeholder="Accesorios" />
      </div>
      <div class="field-group">
        <label>Ubicación del GPS</label>
        <InputText v-model="ubicacion_gps" class="w-full" placeholder="Ubicación GPS" />
      </div>
      <div class="field-group">
        <label>Ubicación del Bloqueo (Bomba/Switch/Ignición/Etc.)</label>
        <InputText v-model="ubicacion_bloqueo" class="w-full" placeholder="Ubicación Bloqueo" />
      </div>
      <!-- Asignación de IMEIs y SIM moved above -->
      <div class="full-width-row"><h4 class="section-header">Datos del cobro</h4></div>
      <!-- <div class="field-group">
        <label>Subtotal (orden de servicio)</label>
        <InputText v-model="subtotal" class="w-full" placeholder="Subtotal" />
      </div> -->
      <div class="field-group">
        <label>Total pagado por el cliente</label>
        <InputText v-model="total" class="w-full" placeholder="Total" />
      </div>
<!--       <div class="field-group">
        <label>El instalador puede modificar este valor si hay algún ajuste.</label>
      </div> -->
      <div class="field-group">
        <label>Monto cobrado por el servicio del técnico</label>
        <InputText v-model="monto_tecnico" class="w-full" placeholder="Monto técnico" />
      </div>
      <div class="field-group">
        <label>Método de pago</label>
        <Dropdown v-model="metodo_pago" :options="metodoPagoOptions" optionLabel="label" optionValue="value" placeholder="Selecciona método de pago" class="w-full mb-4" />
      </div>
      <div class="field-group">
        <label>Viáticos cobrados por el técnico</label>
        <InputText v-model="viaticos" class="w-full" placeholder="Viáticos" />
      </div>
      <div class="full-width-row">
        <div class="field-group">
          <label>Observaciones</label>
          <Textarea v-model="observaciones" rows="3" class="w-full" />
        </div>
      </div>
      <!-- Ubicación dropdown moved above -->
    </div>
    <Button label="Cerrar" class="p-button-secondary mt-3" @click="$emit('close')" />
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import axios from 'axios';
import { getIMEIs } from '@/services/imeiService';

const lugar_instalacion = ref('');
const tipo_servicio = ref('');
const marca = ref('');
const submarca = ref('');
const modelo = ref('');
const placas = ref('');
const color = ref('');
const numero_economico = ref('');
const modelo_gps = ref('');
const accesorios = ref('');
const ubicacion_gps = ref('');
const ubicacion_bloqueo = ref('');
const imei = ref(null);
const imeiOptions = ref([]);
const sim = ref(null);
const simOptions = ref([]);
const subtotal = ref('');
const total = ref('');
const monto_tecnico = ref('');
const viaticos = ref('');
const observaciones = ref('');
const cliente = ref(null);
const clientes = ref([]);
const usuario = ref(null);
const plataforma = ref(null);
const usuariosOptions = ref([]);
const plataformasOptions = ref([]);
const ubicacion = ref(null);
const ubicaciones = ref([]);
const stockUbicacion = ref([]);
const tiposServicio = [
  'Instalación',
  'Reinstalación',
  'Revisión',
  'Desinstalación',
  'Búsqueda'
];
const metodo_pago = ref('');
const metodoPagoOptions = [
  { label: 'Pago en efectivo con el técnico', value: 'efectivo_tecnico' },
  { label: 'Pago con Tarjeta de Crédito', value: 'tarjeta_credito' },
  { label: 'Pago con Tarjeta de Débito', value: 'tarjeta_debito' },
  { label: 'Transferencia', value: 'transferencia' }
];

onMounted(async () => {
  try {
    const res = await axios.get(`${import.meta.env.VITE_API_URL}/clientes`);
    clientes.value = res.data || [];
  } catch (e) {
    clientes.value = [];
  }
  try {
    const res = await axios.get(`${import.meta.env.VITE_API_URL}/ubicaciones`);
    ubicaciones.value = res.data || [];
  } catch (e) {
    ubicaciones.value = [];
  }
});

watch(cliente, async (nuevoClienteId) => {
  const seleccionado = clientes.value.find(c => c.id === nuevoClienteId);
  usuariosOptions.value = seleccionado?.usuarios || [];
  plataformasOptions.value = seleccionado?.plataformas || [];
  usuario.value = null;
  plataforma.value = null;
});

watch(ubicacion, async (nuevaUbicacionId) => {
  if (!nuevaUbicacionId) {
    stockUbicacion.value = [];
    imeiOptions.value = [];
    simOptions.value = [];
    imei.value = null;
    sim.value = null;
    return;
  }
  try {
    const imeis = await getIMEIs();
    const stock = imeis.filter(i => i.ubicacion_id === nuevaUbicacionId && i.status === 'Disponible');
    stockUbicacion.value = stock;
    // IMEI options: items that are not SIMs
    imeiOptions.value = stock.filter(i => !i.articulo_nombre.toLowerCase().includes('sim')).map(i => ({
      imei: i.imei,
      label: `${i.imei} — ${i.articulo_nombre}`
    }));
    // SIM options: items that are SIMs
    simOptions.value = stock.filter(i => i.articulo_nombre.toLowerCase().includes('sim')).map(i => ({
      imei: i.imei,
      label: `${i.imei} — ${i.articulo_nombre}`
    }));
    imei.value = null;
    sim.value = null;
    console.log('Stock de la ubicación:', stock.length, stock);
  } catch (e) {
    stockUbicacion.value = [];
    imeiOptions.value = [];
    simOptions.value = [];
    imei.value = null;
    sim.value = null;
    console.log('Error obteniendo stock de la ubicación:', e);
  }
});
</script>

<style scoped>
.nuevo-reporte-servicio-container {
  max-width: 900px;
  margin: 1rem auto;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0,0,0,0.08);
}
.reporte-title {
  text-align: center;
  margin-bottom: 1rem;
}
.reporte-fields {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 1.5rem;
}
.full-width-row {
  grid-column: 1 / span 2;
}
.field-group {
  display: flex;
  flex-direction: column;
}
label {
  font-weight: 500;
  margin-bottom: 0.5rem;
}
.w-full {
  width: 100%;
}
.mt-3 {
  margin-top: 1.5rem;
}
</style>
