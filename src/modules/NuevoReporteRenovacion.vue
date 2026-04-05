<template>
  <div class="nuevo-reporte-servicio-container">
    <h2 class="reporte-title">Nuevo Reporte de Renovación</h2>
    <div class="servicio-card">
      <BuscadorPlataforma @seleccionar="onPlataformaSeleccionar" @busqueda-resultado="onBusquedaResultado" />

      <div class="reporte-fields">
        <div class="field-group">
          <label class="required-label">Tipo de servicio</label>
          <Dropdown v-model="tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full mb-4" />
        </div>
        <div class="field-group">
          <label class="required-label">Encargado</label>
          <Dropdown v-model="instalador" :options="instaladores" optionLabel="username" optionValue="username"
            placeholder="Selecciona encargado" class="w-full mb-4" />
        </div>
        <div class="field-group">
          <label class="required-label">Cliente</label>
          <Dropdown v-model="cliente" :options="clientes" optionLabel="nombre" optionValue="id"
            placeholder="Selecciona cliente" class="w-full mb-4" filter :filterPlaceholder="'Buscar cliente'" />
        </div>
          <div class="field-group" v-if="plataformasOptions.length" style="flex:1; margin-right:1rem;">
            <label>Plataforma</label>
            <Dropdown v-model="plataforma" :options="plataformasOptions" placeholder="Selecciona plataforma"
              class="w-full mb-4" />
          </div>
        </div>
        <div class="row-group">
          <div class="field-group" v-if="usuariosOptions.length" style="flex:1; margin-right:1rem;">
            <label>Usuario</label>
            <Dropdown v-model="usuario" :options="usuariosOptions" placeholder="Selecciona usuario"
              class="w-full mb-4" />
          </div>
      </div>
      <div style="margin-bottom:2rem;" >
        <h4 style="font-size:1.1em; font-weight:bold; margin-bottom:1em;">Asignación de IMEIs y SIM</h4>
        <div style="display:flex; gap:2rem; margin-bottom:1em; flex-wrap:wrap;">
        </div>
      </div>

      <div class="field-group" style="flex:2;">
        <!-- CAMBIO DE EQUIPO: Solo IMEI nuevo + IMEI a devolver (sin SIM) -->
        <template v-if="tipo_servicio === 'Cambio de Equipo'">
          <div style="display:flex;gap:1em;margin-bottom:1em;">
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>IMEI nuevo</label>
              <Dropdown v-if="!noModificaImei && imeiOptions.length" v-model="imei"
                :options="imeiOptions.filter(opt => opt.status === 'Disponible')" optionLabel="label" optionValue="imei"
                placeholder="Selecciona IMEI nuevo" filter :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                :filterFunction="(value, option) => option.imei.slice(-6).includes(value)" />
              <InputText v-else v-model="imei" placeholder="Captura IMEI nuevo" />
            </div>
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>IMEI a devolver</label>
              <Dropdown v-if="!noModificaImei && imeiOptions.length" v-model="imeiDevolver" :options="imeiOptions"
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
              <Dropdown v-if="!noModificaSim && simOptions.length" v-model="sim"
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
              <Dropdown v-if="noModificaImei" v-model="imei"
                :options="imeiOptions.filter(opt => opt.status === 'Disponible')" optionLabel="label" optionValue="imei"
                placeholder="Selecciona IMEI" filter :filterPlaceholder="'Buscar por últimos 6 dígitos'"
                :filterFunction="(value, option) => option.imei.slice(-6).includes(value)" />
              <InputText v-else v-model="imei" placeholder="Captura IMEI manualmente" />
            </div>
            <div style="flex:1;display:flex;flex-direction:column;">
              <label>SIM 1</label>
              <Dropdown v-if="noModificaSim" v-model="sim"
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
        </div>
        
        <div class="full-width-row">
          <InputText v-model="marca" class="w-full mb-4" placeholder="Marca" />
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

    <!-- Dialog para crear cliente nuevo desde plataforma -->
    <Dialog v-model:visible="showCrearClienteDialog" header="Crear cliente desde plataforma" modal :style="{ width: '500px' }">
      <p style="margin-bottom:1em;color:var(--text-color-secondary);">No se encontró un cliente con el usuario <strong>{{ nuevoClienteForm.usuarios[0] }}</strong>. Revisa y edita los datos antes de crearlo.</p>
      <div style="display:flex;flex-direction:column;gap:0.8em;">
        <div><label style="font-weight:600;">Nombre</label><InputText v-model="nuevoClienteForm.nombre" class="w-full" /></div>
        <div><label style="font-weight:600;">Teléfono</label><InputText v-model="nuevoClienteForm.telefonos[0]" class="w-full" /></div>
        <div><label style="font-weight:600;">Correo</label><InputText v-model="nuevoClienteForm.correo" class="w-full" /></div>
        <div><label style="font-weight:600;">Dirección</label><InputText v-model="nuevoClienteForm.direccion" class="w-full" /></div>
        <div><label style="font-weight:600;">Usuario (plataforma)</label><InputText v-model="nuevoClienteForm.usuarios[0]" class="w-full" /></div>
        <div><label style="font-weight:600;">Plataforma</label><InputText v-model="nuevoClienteForm.plataformas[0]" class="w-full" disabled /></div>
      </div>
      <template #footer>
        <Button label="Cancelar" @click="showCrearClienteDialog = false" class="p-button-secondary" />
        <Button label="Crear cliente" icon="pi pi-check" @click="confirmarCrearCliente" :loading="creandoCliente" />
      </template>
    </Dialog>
  </div>
</template>

<script setup>
import { ref, watch, onMounted, nextTick } from 'vue';
import Dropdown from 'primevue/dropdown';
import InputText from 'primevue/inputtext';
import Textarea from 'primevue/textarea';
import Button from 'primevue/button';
import Dialog from 'primevue/dialog';
import axios from 'axios';
import { getIMEIs } from '@/services/imeiService';
import { verificarReportesActivaciones } from '@/services/activacionesService';
import { addCliente } from '@/services/clientesService';
import { useLoginStore } from '@/stores/loginStore';
import BuscadorPlataforma from '@/components/BuscadorPlataforma.vue';

const loginStore = useLoginStore();

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
const noModificaImei = ref(false);
const noModificaSim = ref(false);
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

const tiposServicio = [
  'Migracion 1 Año',
  'Migracion 10 año',
  'Renovacion 1año',
  'Renovacion 10 años',
  'Renovacion Sim Telcel',
  'Renovacion Sim Español'
];
// Tipos de servicio que NO modifican inventario
const tiposSinStock = ['Revisión', 'Desinstalación', 'Búsqueda', 'Vuelta en falso','Migracion 1 Año','Migracion 10 año','Renovacion 1año','Renovacion 10 años','Renovacion Sim Telcel','Renovacion Sim Español'];
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
  // Renovaciones no modifican stock, cargar todos los IMEIs sin filtrar por ubicación
  try {
    const imeis = await getIMEIs();
    imeiOptions.value = imeis.filter(i => !i.articulo_nombre.toLowerCase().includes('sim')).map(i => ({
      imei: i.imei,
      label: `${i.imei} — ${i.articulo_nombre}`,
      status: i.status
    }));
    simOptions.value = imeis.filter(i => i.articulo_nombre.toLowerCase().includes('sim')).map(i => ({
      imei: i.imei,
      label: `${i.imei} — ${i.articulo_nombre}`,
      status: i.status
    }));
  } catch (e) {
    imeiOptions.value = [];
    simOptions.value = [];
  }
  try {
    const res = await axios.get(`${import.meta.env.VITE_API_URL}/usuarios`);
    const usuarios = res.data || [];
    instaladores.value = [
      ...usuarios.filter(u => u.username === 'Mariah'),
      { username: 'Otro' }
    ];
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



const showDialog = ref(false);
const dialogMessage = ref('');
const dialogTitle = ref('');

// --- Crear cliente desde plataforma ---
const showCrearClienteDialog = ref(false);
const creandoCliente = ref(false);
const nuevoClienteForm = ref({
  nombre: '',
  telefonos: [''],
  correo: '',
  direccion: '',
  usuarios: [''],
  plataformas: [''],
  atendidoPor: '',
  usuarioSesion: '',
  rfc: 'XAXX010101000',
  constancia_path: null,
});

const onPlataformaSeleccionar = async ({ plataforma: plat, dispositivo }) => {
  if (dispositivo.imei) imei.value = dispositivo.imei;
  if (plat) plataforma.value = plat === 'iop' ? 'IOP' : 'Tracksolid';
  if (dispositivo.deviceName) modelo_gps.value = dispositivo.deviceName;
  if (dispositivo._userName) usuario.value = dispositivo._userName;
  if (dispositivo._accountName) usuario.value = dispositivo._accountName;
  if (dispositivo._account) usuario.value = dispositivo._account;
};

const onBusquedaResultado = ({ plataforma: plat, resultados: items }) => {
  if (!items || !items.length) return;
  const primer = items[0];
  const accountName = primer._accountName || primer._account || '';
  if (!accountName) return;
  const platNombre = plat === 'iop' ? 'Wanway' : 'Tracksolidpro';

  const clienteExistente = clientes.value.find(c =>
    c.usuarios?.some(u => u.toLowerCase() === accountName.toLowerCase())
  );
  if (clienteExistente) {
    cliente.value = clienteExistente.id;
    // Esperar a que el watch(cliente) pueble las opciones, luego auto-seleccionar
    nextTick(() => {
      if (plataformasOptions.value.includes(platNombre)) plataforma.value = platNombre;
      else if (plataformasOptions.value.length) plataforma.value = plataformasOptions.value[0];
      if (usuariosOptions.value.includes(accountName)) usuario.value = accountName;
      else if (usuariosOptions.value.length) usuario.value = usuariosOptions.value[0];
    });
  } else {
    nuevoClienteForm.value = {
      nombre: primer._userName || accountName,
      telefonos: [primer._contactTel || ''],
      correo: primer._email || '',
      direccion: primer.address || '',
      usuarios: [accountName],
      plataformas: [platNombre],
      atendidoPor: loginStore.user?.username || '',
      usuarioSesion: loginStore.user?.username || '',
      rfc: 'XAXX010101000',
      constancia_path: null,
    };
    showCrearClienteDialog.value = true;
  }
};

const confirmarCrearCliente = async () => {
  creandoCliente.value = true;
  try {
    await addCliente(nuevoClienteForm.value);
    // Refrescar lista de clientes
    const res = await axios.get(`${import.meta.env.VITE_API_URL}/clientes`);
    clientes.value = res.data || [];
    // Auto-seleccionar el cliente recién creado
    const nuevo = clientes.value.find(c =>
      c.usuarios?.some(u => u.toLowerCase() === nuevoClienteForm.value.usuarios[0].toLowerCase())
    );
    if (nuevo) {
      cliente.value = nuevo.id;
      nextTick(() => {
        const platNombre = nuevoClienteForm.value.plataformas[0];
        const acc = nuevoClienteForm.value.usuarios[0];
        if (plataformasOptions.value.includes(platNombre)) plataforma.value = platNombre;
        else if (plataformasOptions.value.length) plataforma.value = plataformasOptions.value[0];
        if (usuariosOptions.value.includes(acc)) usuario.value = acc;
        else if (usuariosOptions.value.length) usuario.value = usuariosOptions.value[0];
      });
    }
    showCrearClienteDialog.value = false;
  } catch (e) {
    dialogTitle.value = 'Error al crear cliente';
    dialogMessage.value = e?.response?.data?.detail || e.message || 'Error desconocido';
    showDialog.value = true;
  } finally {
    creandoCliente.value = false;
  }
};

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
  noModificaImei.value = false;
  noModificaSim.value = false;
  total.value = '';
  monto_tecnico.value = '';
  viaticos.value = '';
  observaciones.value = '';
  cliente.value = null;
  usuario.value = null;
  instalador.value = null;
  vendedor.value = null;
  plataforma.value = null;
  metodo_pago.value = '';
  lugar_instalacion.value = '';
};

const generarReporte = async () => {
  const clienteSeleccionado = clientes.value.find(c => c.id === cliente.value);
  const nombreCliente = clienteSeleccionado ? clienteSeleccionado.nombre : '';
  // Determinar si no debe modificar stock (por tipo de servicio o por checkbox)
  const esTipoSinStock = tiposSinStock.includes(tipo_servicio.value);
  
  // Observaciones siempre debe incluir 'Renovacion', y si el usuario agrega texto, concatenar
  let obs = 'Renovacion';
  if (observaciones.value && observaciones.value.trim() !== '') {
    obs = `Renovacion, ${observaciones.value.trim()}`;
  }
  const payload = {
    tipo_servicio: tipo_servicio.value || 'NA',
    cliente_id: cliente.value || 0,
    nombre_cliente: nombreCliente || 'NA',
    usuario: usuario.value || 'NA',
    nombre_instalador: instalador.value || 'NA',
    vendedor: 'NA',
    plataforma: plataforma.value || 'NA',
    lugar_instalacion: 'NA',
    ubicacion_id: 0,
    imei: imei.value || 'NA',
    sim_serie: sim.value || 'NA',
    imei_devolver: imeiDevolver.value || 'NA',
    sim_devolver: simDevolver.value || 'NA',
    no_modifica_imei: esTipoSinStock || noModificaImei.value,
    no_modifica_sim: esTipoSinStock || noModificaSim.value,
    marca: 'NA',
    submarca: 'NA',
    modelo: 'NA',
    placas: placas.value || 'NA',
    color: 'NA',
    numero_economico:'NA',
    modelo_gps: modelo_gps.value || 'NA',
    accesorios: 'NA',
    ubicacion_gps: 'NA',
    ubicacion_bloqueo: 'NA',
    subtotal: total.value || 0,
    total: total.value || 0,
    monto_tecnico: 0,
    forma_pago: metodo_pago.value || 'NA',
    viaticos: 0,
    observaciones: obs,
    folio: `${Date.now()}`
  };
  try {
    const res = await axios.post(`${import.meta.env.VITE_API_URL}/reportes-servicio`, payload);
    // El backend ahora maneja la actualización de IMEIs según el campo no_modifica_stock
    dialogTitle.value = 'Reporte generado';
    dialogMessage.value = res.data.message || 'Reporte creado exitosamente';
    showDialog.value = true;
    limpiarFormulario();
    
    // Sincronizar activaciones recientes para que el IMEI quede marcado como "con reporte"
    try {
      await verificarReportesActivaciones();
    } catch (syncErr) {
      console.log('Sincronización de activaciones:', syncErr.message);
    }
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
