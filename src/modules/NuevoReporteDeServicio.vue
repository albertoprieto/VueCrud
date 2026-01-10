<template>
  <div class="nuevo-reporte-servicio-container">
    <h2 class="reporte-title">Nuevo Reporte de Servicio</h2>
    <div class="servicio-card">
      <div class="reporte-fields">
        <div class="full-width-row">
          <div class="field-group">
            <label class="required-label">Tipo de servicio</label>
            <Dropdown v-model="tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full mb-4" />
          </div>
        </div>
        <div class="full-width-row" v-if="instaladores.length">
          <div class="field-group">
            <label class="required-label">Instalador</label>
            <Dropdown v-model="instalador" :options="instaladores" optionLabel="username" optionValue="username"
              placeholder="Selecciona instalador" class="w-full mb-4" />
          </div>
        </div>
        <div class="full-width-row" v-if="vendedores.length">
          <div class="field-group">
            <label class="required-label">Vendedor</label>
            <Dropdown v-model="vendedor" :options="vendedores" optionLabel="username" optionValue="username"
              placeholder="Selecciona vendedor" class="w-full mb-4" />
          </div>
        </div>
        <div class="full-width-row">
          <div class="field-group">
            <label class="required-label">Cliente</label>
            <Dropdown v-model="cliente" :options="clientes" optionLabel="nombre" optionValue="id"
              placeholder="Selecciona cliente" class="w-full mb-4" filter :filterPlaceholder="'Buscar cliente'" />
          </div>
        </div>
        <div class="row-group">
          <div class="field-group" v-if="plataformasOptions.length" style="flex:1; margin-right:1rem;">
            <label>Plataforma</label>
            <Dropdown v-model="plataforma" :options="plataformasOptions" placeholder="Selecciona plataforma"
              class="w-full mb-4" />
          </div>
          <div class="field-group" style="flex:1;">
            <label>Lugar / Centro de instalación</label>
            <InputText v-model="lugar_instalacion" class="w-full" placeholder="Opcional" />
          </div>
        </div>
        <div class="row-group">
          <div class="field-group" v-if="usuariosOptions.length" style="flex:1; margin-right:1rem;">
            <label>Usuario</label>
            <Dropdown v-model="usuario" :options="usuariosOptions" placeholder="Selecciona usuario"
              class="w-full mb-4" />
          </div>
          <div class="field-group" style="flex:1;">
            <label class="required-label">Ubicación</label>
            <Dropdown v-model="ubicacion" :options="ubicaciones" optionLabel="nombre" optionValue="id"
              placeholder="Selecciona ubicación" class="w-full mb-4" />
          </div>
        </div>

      </div>


      <div style="margin-bottom:2rem;" >
        <h4 style="font-size:1.1em; font-weight:bold; margin-bottom:1em;">Asignación de IMEIs y SIM</h4>
        <div style="margin-bottom:1em;">
          <label style="display:flex;align-items:center;gap:0.5em;">
            <input type="checkbox" v-model="noModificaStock" />
            No modifica stock
          </label>
          <span style="color:#888; margin-left:2em; font-size:0.95em;">Si está marcado, los IMEI y SIM se capturan
            manualmente y no modifican el stock.</span>
        </div>
      </div>


      <div class="field-group" style="flex:2;">
        <!-- CAMBIO DE EQUIPO: Solo IMEI nuevo + IMEI a devolver (sin SIM) -->
        <template v-if="tipo_servicio === 'Cambio de Equipo'">
          <div style="display:flex;gap:1em;margin-bottom:1em;">
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>IMEI nuevo</label>
              <Dropdown v-if="!noModificaStock && imeiOptions.length" v-model="imei"
                :options="imeiOptions.filter(opt => opt.status === 'Disponible')" optionLabel="label" optionValue="imei"
                placeholder="Selecciona IMEI nuevo" filter :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                :filterFunction="(value, option) => option.imei.slice(-6).includes(value)" />
              <InputText v-else v-model="imei" placeholder="Captura IMEI nuevo" />
            </div>
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>IMEI a devolver</label>
              <Dropdown v-if="!noModificaStock && imeiOptions.length" v-model="imeiDevolver" :options="imeiOptions"
                optionLabel="label" optionValue="imei" placeholder="Selecciona IMEI a devolver" filter
                :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                :filterFunction="(value, option) => option.imei.slice(-6).includes(value)" />
              <InputText v-else v-model="imeiDevolver" placeholder="Captura IMEI a devolver" />
            </div>
          </div>
        </template>
        <!-- CAMBIO DE CHIP: Solo SIM nuevo + SIM a devolver (sin IMEI) -->
        <template v-else-if="tipo_servicio === 'Cambio de Chip'">
          <div style="display:flex;gap:1em;margin-bottom:1em;">
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>SIM nuevo</label>
              <Dropdown v-if="!noModificaStock && simOptions.length" v-model="sim"
                :options="simOptions.filter(opt => opt.status === 'Disponible')" optionLabel="label" optionValue="imei"
                placeholder="Selecciona SIM nuevo" filter :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                :filterFunction="(value, option) => option.imei.slice(-6).includes(value)" />
              <InputText v-else v-model="sim" placeholder="Captura SIM nuevo" />
            </div>
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>SIM a devolver (no regresa a stock)</label>
              <InputText v-model="simDevolver" placeholder="Captura SIM a devolver" />
            </div>
          </div>
        </template>
        <template v-else>
          <div style="display:flex;gap:1em;margin-bottom:1em;">
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>IMEI 1</label>
              <Dropdown v-if="!noModificaStock && imeiOptions.length" v-model="imei"
                :options="imeiOptions.filter(opt => opt.status === 'Disponible')" optionLabel="label" optionValue="imei"
                placeholder="Selecciona IMEI" filter :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                :filterFunction="(value, option) => option.imei.slice(-6).includes(value)" />
              <InputText v-else v-model="imei" placeholder="Captura IMEI manualmente" />
            </div>
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>SIM 1</label>
              <Dropdown v-if="!noModificaStock && simOptions.length" v-model="sim"
                :options="simOptions.filter(opt => opt.status === 'Disponible')" optionLabel="label" optionValue="imei"
                placeholder="Selecciona SIM" filter :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                :filterFunction="(value, option) => option.imei.slice(-6).includes(value)" />
              <InputText v-else v-model="sim" placeholder="Captura SIM manualmente" />
            </div>
          </div>
        </template>
      </div>

      <div class="reporte-fields">

        <div class="full-width-row">
          <h4 class="section-header">Datos del vehículo</h4>
        </div>
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
        <div class="full-width-row">
          <h4 class="section-header">Datos del dispositivo (opcionales)</h4>
        </div>
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
        <div class="full-width-row">
          <h4 class="section-header">Datos del cobro</h4>
        </div>
        <div class="field-group">
          <label>Total pagado por el cliente</label>
          <InputText v-model="total" class="w-full" placeholder="Total" />
        </div>
        <div class="field-group">
          <label>Monto cobrado por el servicio del técnico</label>
          <InputText v-model="monto_tecnico" class="w-full" placeholder="Monto técnico" />
        </div>
        <div class="field-group">
          <label>Método de pago</label>
          <Dropdown v-model="metodo_pago" :options="metodoPagoOptions" optionLabel="label" optionValue="value"
            placeholder="Selecciona método de pago" class="w-full mb-4" />
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
      </div>
    </div>
    <Button label="Generar reporte" class="p-button-primary mt-3" @click="generarReporte" />
    <Dialog v-model:visible="showDialog" :header="dialogTitle" modal :style="{ width: '400px' }">
      <div>
        <pre style="white-space:pre-wrap;word-break:break-word">{{ dialogMessage }}</pre>
      </div>
      <template #footer>
        <Button label="Cerrar" @click="showDialog = false" class="p-button-secondary" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
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
const imeiDevolver = ref('');
const simDevolver = ref('');
const noModificaStock = ref(false);
const total = ref('');
const monto_tecnico = ref('');
const viaticos = ref('');
const observaciones = ref('');
const cliente = ref(null);
const clientes = ref([]);
const usuario = ref(null);
const instalador = ref(null);
const instaladores = ref([]);
const vendedor = ref(null);
const vendedores = ref([]);
const plataforma = ref(null);
const usuariosOptions = ref([]);
const plataformasOptions = ref([]);
const ubicacion = ref(null);
const ubicaciones = ref([]);
const stockUbicacion = ref([]);
const tiposServicio = [
  'Instalación',
  'Solo Venta',
  'Reinstalación',
  'Revisión',
  'Desinstalación',
  'Búsqueda',
  'Cambio de Equipo',
  'Cambio de Chip',
  'Vuelta en falso'
];
// Tipos de servicio que NO modifican inventario
const tiposSinStock = ['Revisión', 'Desinstalación', 'Búsqueda', 'Vuelta en falso'];
const metodo_pago = ref('');
const metodoPagoOptions = [
  { label: 'Pago en efectivo con el técnico', value: 'efectivo_tecnico' },
  { label: 'Pago con Tarjeta de Crédito', value: 'tarjeta_credito' },
  { label: 'Pago con Tarjeta de Débito', value: 'tarjeta_debito' },
  { label: 'Transferencia', value: 'transferencia' },
  { label: 'Pago en Oficina', value: 'efectivo_oficina' }
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
  try {
    const res = await axios.get(`${import.meta.env.VITE_API_URL}/usuarios`);
    const usuarios = res.data || [];
    instaladores.value = usuarios.filter(u => u.perfil === 'Tecnico');
    vendedores.value = usuarios.filter(u => u.perfil === 'Vendedor');
  } catch (e) {
    instaladores.value = [];
    vendedores.value = [];
  }
});

watch(cliente, async (nuevoClienteId) => {
  const seleccionado = clientes.value.find(c => c.id === nuevoClienteId);
  usuariosOptions.value = seleccionado?.usuarios || [];
  plataformasOptions.value = seleccionado?.plataformas || [];
  usuario.value = null;
  plataforma.value = null;
  if (seleccionado) {
    console.log('Cliente seleccionado:', seleccionado.nombre);
  }
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
    const stock = imeis.filter(i => i.ubicacion_id === nuevaUbicacionId);
    stockUbicacion.value = stock;
    imeiOptions.value = stock.filter(i => !i.articulo_nombre.toLowerCase().includes('sim')).map(i => ({
      imei: i.imei,
      label: `${i.imei} — ${i.articulo_nombre}`,
      status: i.status
    }));
    simOptions.value = stock.filter(i => i.articulo_nombre.toLowerCase().includes('sim')).map(i => ({
      imei: i.imei,
      label: `${i.imei} — ${i.articulo_nombre}`,
      status: i.status
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

const showDialog = ref(false);
const dialogMessage = ref('');
const dialogTitle = ref('');

const limpiarFormulario = () => {
  tipo_servicio.value = '';
  marca.value = '';
  submarca.value = '';
  modelo.value = '';
  placas.value = '';
  color.value = '';
  numero_economico.value = '';
  modelo_gps.value = '';
  accesorios.value = '';
  ubicacion_gps.value = '';
  ubicacion_bloqueo.value = '';
  imei.value = null;
  sim.value = null;
  imeiDevolver.value = '';
  simDevolver.value = '';
  noModificaStock.value = false;
  total.value = '';
  monto_tecnico.value = '';
  viaticos.value = '';
  observaciones.value = '';
  cliente.value = null;
  usuario.value = null;
  instalador.value = null;
  vendedor.value = null;
  plataforma.value = null;
  ubicacion.value = null;
  metodo_pago.value = '';
  lugar_instalacion.value = '';
};

const generarReporte = async () => {
  const clienteSeleccionado = clientes.value.find(c => c.id === cliente.value);
  const nombreCliente = clienteSeleccionado ? clienteSeleccionado.nombre : '';
  // Determinar si no debe modificar stock
  const noModificaInventario = noModificaStock.value === true || tiposSinStock.includes(tipo_servicio.value);
  
  const payload = {
    tipo_servicio: tipo_servicio.value,
    cliente_id: cliente.value,
    nombre_cliente: nombreCliente,
    usuario: usuario.value || '',
    nombre_instalador: instalador.value || '',
    vendedor: vendedor.value || '',
    plataforma: plataforma.value || '',
    lugar_instalacion: lugar_instalacion.value || '',
    ubicacion_id: ubicacion.value,
    imei: imei.value || '',
    sim_serie: sim.value || '',
    // NUEVO: indicar al backend si NO debe modificar stock
    no_modifica_stock: noModificaInventario,
    marca: marca.value,
    submarca: submarca.value,
    modelo: modelo.value,
    placas: placas.value,
    color: color.value,
    numero_economico: numero_economico.value,
    modelo_gps: modelo_gps.value,
    accesorios: accesorios.value,
    ubicacion_gps: ubicacion_gps.value,
    ubicacion_bloqueo: ubicacion_bloqueo.value,
    subtotal: total.value,
    total: total.value,
    monto_tecnico: monto_tecnico.value,
    forma_pago: metodo_pago.value,
    viaticos: viaticos.value,
    observaciones: observaciones.value,
    folio: `${Date.now()}`
  };
  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/reportes-servicio`, payload);
    // El backend ahora maneja la actualización de IMEIs según el campo no_modifica_stock
    dialogTitle.value = 'Reporte generado';
    dialogMessage.value = res.data.message || 'Reporte creado exitosamente';
    showDialog.value = true;
    limpiarFormulario();
  } catch (e) {
    dialogTitle.value = 'Error';
    dialogMessage.value = e?.response?.data ? JSON.stringify(e.response.data) : e.message;
    showDialog.value = true;
  }
};
</script>

<style scoped>
.nuevo-reporte-servicio-container {
  max-width: 900px;
  margin: 1rem auto;
  padding: 1rem;
  border-radius: 12px;
  box-shadow: 0 2px 12px rgba(0, 0, 0, 0.08);
}

.reporte-title {
  text-align: center;
  margin-bottom: 1rem;
}

.servicio-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--card-shadow, rgba(0, 0, 0, 0.07));
  margin-bottom: 2rem;
  padding: 1rem;
  transition: box-shadow 0.2s;
  background: var(--card-bg, inherit);
}

.servicio-card:hover {
  box-shadow: 0 4px 16px var(--card-shadow-hover, rgba(0, 0, 0, 0.12));
}

.card-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
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
