<template>
  <div class="nuevo-reporte-servicio-container">
    <h2 class="reporte-title">Nuevo Reporte de Servicio</h2>
    <div v-for="(servicio, idx) in serviciosReporteStore.servicios" :key="idx" class="servicio-card">
      <div class="card-header">
        <h3 class="section-header">Servicio #{{ idx + 1 }}</h3>
        <Button icon="pi pi-trash" class="p-button-danger p-button-sm" @click="eliminarServicio(idx)" v-if="serviciosReporteStore.servicios.length > 1" style="float:right" />
      </div>
      <div class="reporte-fields">
        <!-- ... Renderiza los mismos campos, pero usando servicio[prop] ... -->
        <div class="full-width-row">
          <div class="field-group">
            <label class="required-label">Tipo de servicio</label>
            <Dropdown v-model="servicio.tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full mb-4" />
          </div>
        </div>
        <div class="full-width-row" v-if="instaladores.length">
          <div class="field-group">
            <label class="required-label">Instalador</label>
            <Dropdown v-model="servicio.instalador" :options="instaladores" optionLabel="username" optionValue="username" placeholder="Selecciona instalador" class="w-full mb-4" />
          </div>
        </div>
        <div class="full-width-row" v-if="vendedores.length">
          <div class="field-group">
            <label class="required-label">Vendedor</label>
            <Dropdown v-model="servicio.vendedor" :options="vendedores" optionLabel="username" optionValue="username" placeholder="Selecciona vendedor" class="w-full mb-4" />
          </div>
        </div>
        <div class="full-width-row">
          <div class="field-group">
            <label class="required-label">Cliente</label>
            <Dropdown
              v-model="servicio.cliente"
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
            <Dropdown v-model="servicio.plataforma" :options="plataformasOptions" placeholder="Selecciona plataforma" class="w-full mb-4" />
          </div>
          <div class="field-group" style="flex:1;">
              <label>Lugar / Centro de instalación</label>
            <InputText v-model="servicio.lugar_instalacion" class="w-full" placeholder="Opcional" />
          </div>
        </div>
        <div class="row-group">
          <div class="field-group" v-if="usuariosOptions.length" style="flex:1; margin-right:1rem;">
            <label>Usuario</label>
            <Dropdown v-model="servicio.usuario" :options="usuariosOptions" placeholder="Selecciona usuario" class="w-full mb-4" />
          </div>
          <div class="field-group" style="flex:1;">
            <label class="required-label">Ubicación</label>
            <Dropdown v-model="servicio.ubicacion" :options="ubicaciones" optionLabel="nombre" optionValue="id" placeholder="Selecciona ubicación" class="w-full mb-4" />
          </div>
        </div>
      
      </div>
        
        
        <div style="margin-bottom:2rem;">
          <h4 style="font-size:1.1em; font-weight:bold; margin-bottom:1em;">Asignación de IMEIs y SIM</h4>
          <div style="margin-bottom:1em;">
            <label style="display:flex;align-items:center;gap:0.5em;">
              <input type="checkbox" v-model="servicio.noModificaStock" />
              No modifica stock
            </label>
            <span style="color:#888; margin-left:2em; font-size:0.95em;">Si está marcado, los IMEI y SIM se capturan manualmente y no modifican el stock.</span>
          </div>
        </div>


<div class="field-group" style="flex:2;">
          <template v-if="servicio.tipo_servicio === 'Cambio de Equipo'">
            <div style="display:flex;gap:1em;margin-bottom:1em;">
              <div style="flex:1;display:flex;flex-direction:column;">
                <label>IMEI nuevo</label>
                <Dropdown
                  v-if="!servicio.noModificaStock && imeiOptions.length"
                  v-model="servicio.imei"
                  :options="imeiOptions.filter(opt => opt.status === 'Disponible')"
                  optionLabel="label"
                  optionValue="imei"
                  placeholder="Selecciona IMEI nuevo"
                  filter
                  :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                  :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
                />
                <InputText v-else v-model="servicio.imei" placeholder="Captura IMEI nuevo" />
              </div>
              <div style="flex:1;display:flex;flex-direction:column;">
                <label>SIM nuevo</label>
                <Dropdown
                  v-if="!servicio.noModificaStock && simOptions.length"
                  v-model="servicio.sim"
                  :options="simOptions.filter(opt => opt.status === 'Disponible')"
                  optionLabel="label"
                  optionValue="imei"
                  placeholder="Selecciona SIM nuevo"
                  filter
                  :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                  :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
                />
                <InputText v-else v-model="servicio.sim" placeholder="Captura SIM nuevo" />
              </div>
            </div>
            <div style="display:flex;gap:1em;margin-bottom:1em;">
              <div style="flex:1;display:flex;flex-direction:column;">
                <label>IMEI a devolver</label>
                <Dropdown
                  v-if="!servicio.noModificaStock && imeiOptions.length"
                  v-model="servicio.imeiDevolver"
                  :options="imeiOptions.filter(opt => opt.status === 'Devuelto')"
                  optionLabel="label"
                  optionValue="imei"
                  placeholder="Selecciona IMEI a devolver"
                  filter
                  :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                  :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
                />
                <InputText v-else v-model="servicio.imeiDevolver" placeholder="Captura IMEI a devolver" />
              </div>
              <div style="flex:1;display:flex;flex-direction:column;">
                <label>SIM a devolver</label>
                <Dropdown
                  v-if="!servicio.noModificaStock && simOptions.length"
                  v-model="servicio.simDevolver"
                  :options="simOptions.filter(opt => opt.status === 'Devuelto')"
                  optionLabel="label"
                  optionValue="imei"
                  placeholder="Selecciona SIM a devolver"
                  filter
                  :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                  :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
                />
                <InputText v-else v-model="servicio.simDevolver" placeholder="Captura SIM a devolver" />
              </div>
            </div>
          </template>
          <template v-else>
            <div style="display:flex;gap:1em;margin-bottom:1em;">
              <div style="flex:1;display:flex;flex-direction:column;">
                <label>IMEI 1</label>
                <Dropdown
                  v-if="!servicio.noModificaStock && imeiOptions.length"
                  v-model="servicio.imei"
                  :options="imeiOptions.filter(opt => opt.status === 'Disponible')"
                  optionLabel="label"
                  optionValue="imei"
                  placeholder="Selecciona IMEI"
                  filter
                  :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                  :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
                />
                <InputText v-else v-model="servicio.imei" placeholder="Captura IMEI manualmente" />
              </div>
              <div style="flex:1;display:flex;flex-direction:column;">
                <label>SIM 1</label>
                <Dropdown
                  v-if="!servicio.noModificaStock && simOptions.length"
                  v-model="servicio.sim"
                  :options="simOptions.filter(opt => opt.status === 'Disponible')"
                  optionLabel="label"
                  optionValue="imei"
                  placeholder="Selecciona SIM"
                  filter
                  :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                  :filterFunction="(value, option) => option.imei.slice(-6).includes(value)"
                />
                <InputText v-else v-model="servicio.sim" placeholder="Captura SIM manualmente" />
              </div>
            </div>
          </template>
</div>

         <div class="reporte-fields">
        
        <div class="full-width-row"><h4 class="section-header">Datos del vehículo</h4></div>
        <div class="field-group">
          <label>Marca</label>
          <InputText v-model="servicio.marca" class="w-full" placeholder="Marca" />
        </div>
        <div class="field-group">
          <label>Submarca</label>
          <InputText v-model="servicio.submarca" class="w-full" placeholder="Submarca" />
        </div>
        <div class="field-group">
          <label>Modelo</label>
          <InputText v-model="servicio.modelo" class="w-full" placeholder="Modelo" />
        </div>
        <div class="field-group">
          <label>Placas</label>
          <InputText v-model="servicio.placas" class="w-full" placeholder="Placas" />
        </div>
        <div class="field-group">
          <label>Color</label>
          <InputText v-model="servicio.color" class="w-full" placeholder="Color" />
        </div>
        <div class="field-group">
          <label>Número económico</label>
          <InputText v-model="servicio.numero_economico" class="w-full" placeholder="Número económico" />
        </div>
        <div class="full-width-row"><h4 class="section-header">Datos del dispositivo (opcionales)</h4></div>
        <div class="field-group">
          <label>Modelo GPS</label>
          <InputText v-model="servicio.modelo_gps" class="w-full" placeholder="Modelo GPS" />
        </div>
        <div class="field-group">
          <label>Accesorios adicionales (Botón/Micro/Etc.)</label>
          <InputText v-model="servicio.accesorios" class="w-full" placeholder="Accesorios" />
        </div>
        <div class="field-group">
          <label>Ubicación del GPS</label>
          <InputText v-model="servicio.ubicacion_gps" class="w-full" placeholder="Ubicación GPS" />
        </div>
        <div class="field-group">
          <label>Ubicación del Bloqueo (Bomba/Switch/Ignición/Etc.)</label>
          <InputText v-model="servicio.ubicacion_bloqueo" class="w-full" placeholder="Ubicación Bloqueo" />
        </div>
        <div class="full-width-row"><h4 class="section-header">Datos del cobro</h4></div>
        <div class="field-group">
          <label>Total pagado por el cliente</label>
          <InputText v-model="servicio.total" class="w-full" placeholder="Total" />
        </div>
        <div class="field-group">
          <label>Monto cobrado por el servicio del técnico</label>
          <InputText v-model="servicio.monto_tecnico" class="w-full" placeholder="Monto técnico" />
        </div>
        <div class="field-group">
          <label>Método de pago</label>
          <Dropdown v-model="servicio.metodo_pago" :options="metodoPagoOptions" optionLabel="label" optionValue="value" placeholder="Selecciona método de pago" class="w-full mb-4" />
        </div>
        <div class="field-group">
          <label>Viáticos cobrados por el técnico</label>
          <InputText v-model="servicio.viaticos" class="w-full" placeholder="Viáticos" />
        </div>
        <div class="full-width-row">
          <div class="field-group">
            <label>Observaciones</label>
            <Textarea v-model="servicio.observaciones" rows="3" class="w-full" />
          </div>
        </div>
      </div>
    </div>
    <div class="add-servicio-btn">
      <Button icon="pi pi-plus" label="Agregar servicio" class="p-button-success mt-3" @click="agregarServicio" />
    </div>
    <Button label="Generar reporte" class="p-button-primary mt-3" @click="generarReportesMultiples" />
    <Dialog v-model:visible="showDialog" :header="dialogTitle" modal :style="{ width: '400px' }">
      <div v-if="Array.isArray(dialogResults)">
        <ul style="padding-left: 1.2em;">
          <li v-for="r in dialogResults" :key="r.idx" style="margin-bottom: 0.7em;">
            <span v-if="r.status === 'ok'" style="color: var(--success-color, #4caf50); font-weight: 500;">✔</span>
            <span v-else style="color: var(--error-color, #f44336); font-weight: 500;">✖</span>
            <span style="margin-left: 0.5em;">Servicio #{{ r.idx }}: {{ r.message }}</span>
          </li>
        </ul>
      </div>
      <div v-else>
        <pre style="white-space:pre-wrap;word-break:break-word">{{ dialogMessage }}</pre>
      </div>
      <template #footer>
        <Button label="Cerrar" @click="showDialog = false" class="p-button-secondary" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick, onUnmounted } from 'vue';
onUnmounted(() => {
  serviciosReporteStore.limpiarServicios();
});
import { useServiciosReporteStore } from '@/stores/serviciosReporteStore';
const serviciosReporteStore = useServiciosReporteStore();

function servicioVacio() {
  return {
    tipo_servicio: '',
    marca: '',
    submarca: '',
    modelo: '',
    placas: '',
    color: '',
    numero_economico: '',
    modelo_gps: '',
    accesorios: '',
    ubicacion_gps: '',
    ubicacion_bloqueo: '',
    imei: null,
    sim: null,
    imeiDevolver: '',
    simDevolver: '',
    validacionMsg: '',
    validacionOk: false,
    total: '',
    monto_tecnico: '',
    viaticos: '',
    observaciones: '',
    cliente: null,
    usuario: null,
    instalador: null,
    vendedor: null,
    plataforma: null,
    ubicacion: null,
    metodo_pago: '',
    noModificaStock: false,
  };
}

// Validación de IMEI/SIM para Cambio de Equipo
function validarImeiSim(servicio) {
  servicio.validacionMsg = '';
  servicio.validacionOk = false;
  if (!servicio.imei || !servicio.sim || !servicio.imeiDevolver || !servicio.simDevolver) {
    servicio.validacionMsg = 'Completa todos los campos para validar.';
    return;
  }
  getIMEIs().then(imeis => {
    const imeiList = imeis.map(i => i.imei);
    const okNuevo = imeiList.includes(servicio.imei);
    const okSim = imeiList.includes(servicio.sim);
    const okDevImei = imeiList.includes(servicio.imeiDevolver);
    const okDevSim = imeiList.includes(servicio.simDevolver);
    if (okNuevo && okSim && okDevImei && okDevSim) {
      servicio.validacionMsg = 'Todos los IMEI y SIM existen.';
      servicio.validacionOk = true;
    } else {
      let msg = 'No existen: ';
      if (!okNuevo) msg += 'IMEI nuevo. ';
      if (!okSim) msg += 'SIM nuevo. ';
      if (!okDevImei) msg += 'IMEI a devolver. ';
      if (!okDevSim) msg += 'SIM a devolver.';
      servicio.validacionMsg = msg;
    }
  });
}

if (serviciosReporteStore.servicios.length === 0) {
  serviciosReporteStore.agregarServicio(servicioVacio());
}

function agregarServicio() {
  serviciosReporteStore.agregarServicio(servicioVacio());
}
function eliminarServicio(idx) {
  serviciosReporteStore.eliminarServicio(idx);
}

function setupServicioWatchers(servicio) {
  watch(() => servicio.cliente, async (nuevoClienteId) => {
    const seleccionado = clientes.value.find(c => c.id === nuevoClienteId);
    usuariosOptions.value = seleccionado?.usuarios || [];
    plataformasOptions.value = seleccionado?.plataformas || [];
    servicio.usuario = null;
    servicio.plataforma = null;
    if (seleccionado) {
      console.log('Cliente seleccionado:', seleccionado.nombre);
    }
  });
  watch(() => servicio.ubicacion, async (nuevaUbicacionId) => {
    if (!nuevaUbicacionId) {
      stockUbicacion.value = [];
      imeiOptions.value = [];
      simOptions.value = [];
      servicio.imei = null;
      servicio.sim = null;
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
      servicio.imei = null;
      servicio.sim = null;
      console.log('Stock de la ubicación:', stock.length, stock);
    } catch (e) {
      stockUbicacion.value = [];
      imeiOptions.value = [];
      simOptions.value = [];
      servicio.imei = null;
      servicio.sim = null;
      console.log('Error obteniendo stock de la ubicación:', e);
    }
  });
}

serviciosReporteStore.servicios.forEach(servicio => setupServicioWatchers(servicio));
watch(() => serviciosReporteStore.servicios.length, async () => {
  await nextTick();
  serviciosReporteStore.servicios.forEach(servicio => setupServicioWatchers(servicio));
});
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
const subtotal = ref('');
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
  'Reinstalación',
  'Revisión',
  'Desinstalación',
  'Búsqueda',
  'Cambio de Equipo',
  'Cambio de Chip',
  'Vuelta en falso'
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

const showDialog = ref(false);
const dialogMessage = ref('');
const dialogTitle = ref('');
const dialogResults = ref(null);

const generarReportesMultiples = async () => {
  let folioBase = Date.now();
  let resultados = [];
  for (let i = 0; i < serviciosReporteStore.servicios.length; i++) {
    const servicio = serviciosReporteStore.servicios[i];
    const clienteSeleccionado = clientes.value.find(c => c.id === servicio.cliente);
    const nombreCliente = clienteSeleccionado ? clienteSeleccionado.nombre : '';
    const payload = {
      tipo_servicio: servicio.tipo_servicio,
      cliente_id: servicio.cliente,
      nombre_cliente: nombreCliente,
      usuario: servicio.usuario,
      nombre_instalador: servicio.instalador,
      vendedor: servicio.vendedor,
      plataforma: servicio.plataforma,
      lugar_instalacion: servicio.lugar_instalacion,
      ubicacion_id: servicio.ubicacion,
      imei: servicio.imei,
      sim_serie: servicio.sim,
      marca: servicio.marca,
      submarca: servicio.submarca,
      modelo: servicio.modelo,
      placas: servicio.placas,
      color: servicio.color,
      numero_economico: servicio.numero_economico,
      modelo_gps: servicio.modelo_gps,
      accesorios: servicio.accesorios,
      ubicacion_gps: servicio.ubicacion_gps,
      ubicacion_bloqueo: servicio.ubicacion_bloqueo,
      subtotal: servicio.total,
      total: servicio.total,
      monto_tecnico: servicio.monto_tecnico,
      forma_pago: servicio.metodo_pago,
      viaticos: servicio.viaticos,
      observaciones: servicio.observaciones,
      folio: `${folioBase}-${i+1}`
    };
    try {
      const res = await axios.post(`${import.meta.env.VITE_API_URL}/reportes-servicio`, payload);
      // Marcar como Vendido los nuevos
      if (servicio.sim) {
        await axios.put(`${import.meta.env.VITE_API_URL}/imeis/${servicio.sim}`, { status: 'Vendido' });
      }
      if (servicio.imei) {
        await axios.put(`${import.meta.env.VITE_API_URL}/imeis/${servicio.imei}`, { status: 'Vendido' });
      }
      // Marcar como Devuelto los que se devuelven en Cambio de Equipo
      if (servicio.tipo_servicio === 'Cambio de Equipo') {
        if (servicio.imeiDevolver) {
          await axios.put(`${import.meta.env.VITE_API_URL}/imeis/${servicio.imeiDevolver}`, { status: 'Devuelto' });
        }
        if (servicio.simDevolver) {
          await axios.put(`${import.meta.env.VITE_API_URL}/imeis/${servicio.simDevolver}`, { status: 'Devuelto' });
        }
      }
      resultados.push({ idx: i+1, status: 'ok', message: res.data.message });
    } catch (e) {
      resultados.push({ idx: i+1, status: 'error', message: e?.response?.data ? e.response.data : e.message });
    }
  }
  dialogTitle.value = 'Resultados de generación de reportes';
  dialogResults.value = resultados;
  dialogMessage.value = '';
  showDialog.value = true;
  serviciosReporteStore.limpiarServicios();
  serviciosReporteStore.agregarServicio(servicioVacio());
};
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
.servicio-card {
  border-radius: 8px;
  box-shadow: 0 2px 8px var(--card-shadow, rgba(0,0,0,0.07));
  margin-bottom: 2rem;
  padding: 1rem;
  transition: box-shadow 0.2s;
  background: var(--card-bg, inherit);
}
.servicio-card:hover {
  box-shadow: 0 4px 16px var(--card-shadow-hover, rgba(0,0,0,0.12));
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
.add-servicio-btn {
  text-align: center;
  margin-bottom: 2rem;
}
</style>
