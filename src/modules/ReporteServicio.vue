<template>
  <div class="reporte-servicio-container">
    <h2 class="reporte-title">Reporte de Servicio</h2>
    <div v-if="!asignacionIdValido">
      <div class="alert-existente error-bg">
        Error: No se recibió un ID de asignación válido.<br>
        Verifica la navegación desde la pantalla anterior.<br>
        Consulta consola para más detalles.
      </div>
    </div>
    <form v-else class="reporte-form" @submit.prevent="guardar">
      <!-- <div class="abonos-section" v-if="form.total">
        <h4 class="section-title">Pagos y abonos</h4>
        <div v-if="pagos.length === 0" class="abonos-vacio">No hay pagos registrados para este servicio.</div>
        <div v-else>
          <table class="abonos-table">
            <thead>
              <tr><th>Fecha</th><th>Monto</th><th>Referencia</th><th>Concepto</th></tr>
            </thead>
            <tbody>
              <tr v-for="p in pagos" :key="p.id">
                <td>{{ formatearFecha(p.fecha) }}</td>
                <td>{{ formatoMoneda(p.monto) }}</td>
                <td>{{ p.referencia }}</td>
                <td>{{ p.concepto }}</td>
              </tr>
            </tbody>
          </table>
        </div>
        <div class="abonos-resumen">
          <span><b>Total servicio:</b> {{ formatoMoneda(Number(form.total)||0) }}</span>
          <span><b>Pagado:</b> {{ formatoMoneda(totalPagado) }}</span>
          <span :style="{color: saldoPendiente > 0 ? '#e53935' : '#43a047'}"><b>Saldo pendiente:</b> {{ formatoMoneda(saldoPendiente) }}</span>
        </div>
        <form class="abono-form" @submit.prevent="registrarAbono">
          <div class="form-group">
            <label>Nuevo abono</label>
            <InputNumber v-model="nuevoAbono" mode="currency" currency="MXN" locale="es-MX" :min="1" :step="0.01" placeholder="Monto del abono" class="w-full mb-2" required />
          </div>
          <div class="form-group">
            <InputText v-model="nuevaReferencia" placeholder="Referencia (opcional)" class="w-full mb-2" />
          </div>
          <Button type="submit" label="Registrar abono" icon="pi pi-plus" class="p-button-success" />
        </form>
      </div> -->

      <div v-if="loading" class="loader-overlay">
        <Loader />
      </div>
      <div v-else>
        <div v-if="reporteExistente" class="alert-existente">
          Ya existe un reporte de servicio para esta asignación. Elimínalo antes de crear uno nuevo.
        </div>
        <div v-else>
          <div class="form-row">
            <div class="form-col">
              <div class="form-group">
                <label>Tipo de servicio</label>
                <Dropdown v-model="form.tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full" />
              </div>
              <div class="form-group">
                <label>Lugar/Centro de instalación</label>
                <InputText v-model="form.lugar_instalacion" class="w-full" placeholder="Opcional" />
              </div>
              <h4 class="section-title">Datos del vehículo</h4>
              <div class="form-group">
                <InputText v-model="form.marca" placeholder="Marca" class="w-full mb-2" />
                <InputText v-model="form.submarca" placeholder="Submarca" class="w-full mb-2" />
                <InputText v-model="form.modelo" placeholder="Modelo" class="w-full mb-2" />
                <InputText v-model="form.placas" placeholder="Placas" class="w-full mb-2" />
                <InputText v-model="form.color" placeholder="Color" class="w-full mb-2" />
                <InputText v-model="form.numero_economico" placeholder="Número económico" class="w-full mb-2" />
              </div>
              <h4 class="section-title">Datos SIM (uso interno)</h4>
              <div class="form-group">
                <InputText v-model="form.sim_proveedor" placeholder="Proveedor" class="w-full mb-2" />
                <InputText v-model="form.sim_serie" placeholder="Serie" class="w-full mb-2" />
                <InputText :value="tecnicoNombre" placeholder="Técnico asignado" class="w-full mb-2" disabled />
                <!-- <InputText :value="tecnicoTelefono" placeholder="Teléfono del técnico" class="w-full mb-2" disabled /> -->
              </div>
              <h4 class="section-title">Aviso</h4>
              <div class="form-group">
                <label>Nombre del cliente</label>
                <InputText :value="form.nombre_cliente" placeholder="Nombre del cliente" class="w-full mb-2" disabled />
              </div>
              <div class="form-group">
                <label>Teléfono del cliente</label>
                <InputText :value="form.telefono_cliente" placeholder="Teléfono" class="w-full mb-2" disabled />
              </div>
              <!-- <div class="form-group">
                <InputText :value="tecnicoNombre" placeholder="Nombre del instalador" class="w-full mb-2" disabled />
              </div> -->
            </div>
            <div class="form-col">
              <h4 class="section-title">Datos del equipo</h4>
              <div class="form-group">
                <InputText v-model="form.equipo_plan" placeholder="Equipo/Plan" class="w-full mb-2" />
                <InputText v-model="form.imei" placeholder="IMEI" class="w-full mb-2" />
                <InputText v-model="form.serie" placeholder="Serie" class="w-full mb-2" />
                <InputText v-model="form.accesorios" placeholder="Accesorios adicionales" class="w-full mb-2" />
              </div>
              <h4 class="section-title">Datos de conexión y corte</h4>
              <div class="form-group">
                <InputText v-model="form.bateria" placeholder="Batería" class="w-full mb-2" />
                <InputText v-model="form.ignicion" placeholder="Ignición" class="w-full mb-2" />
                <InputText v-model="form.corte" placeholder="Corte bomba/switch" class="w-full mb-2" />
                <InputText v-model="form.ubicacion_corte" placeholder="Ubicación" class="w-full mb-2" />
              </div>
              <div class="form-group">
                <label>Observaciones de la unidad</label>
                <Textarea v-model="form.observaciones" rows="2" class="w-full" />
              </div>
              <h4 class="section-title">Plataforma y usuario</h4>
              <div class="form-group">
                <label>Plataformas del cliente</label>
                <Dropdown
                  v-model="form.plataforma"
                  :options="clientePlataformasOptions"
                  placeholder="Selecciona plataforma"
                  class="w-full mb-2"
                  optionLabel="label"
                  :disabled="false"
                />
              </div>
              <div class="form-group">
                <label>Usuarios del cliente</label>
                <Dropdown
                  v-model="form.usuario"
                  :options="clienteUsuariosOptions"
                  placeholder="Selecciona usuario"
                  class="w-full mb-2"
                  optionLabel="label"
                  :disabled="false"
                />
              </div>
              <h4 class="section-title">Venta y pago</h4>
              <div class="form-group">
                <label>Subtotal (orden de servicio)</label>
                <InputText v-model="form.subtotal" placeholder="Subtotal" class="w-full mb-2" :disabled="true" />
              </div>
              <div class="form-group">
                <label>Total a cobrar</label>
                <InputNumber v-model="form.total" placeholder="Total a cobrar" class="w-full mb-2" />
                <small>El instalador puede modificar este valor si hay algún ajuste.</small>
              </div>
              <!-- Método de pago (display-only) -->
              <div class="form-group">
                <label>Método de pago</label>
                <InputText v-if="form.value" v-model="form.value.forma_pago" disabled class="w-full" />
                <InputText v-else :value="''" disabled class="w-full" />
              </div>
              <div class="form-group">
                <label>Observaciones de la unidad o ajuste de cobro</label>
                <Textarea v-model="form.observaciones" rows="2" class="w-full" />
                <small>Si el total difiere del subtotal, explica aquí el motivo.</small>
              </div>
              <div class="form-group">
                <label>Monto cobrado por el técnico</label>
                <InputText v-model="form.monto_tecnico" type="number" class="w-full mb-2" />
              </div>
              <div class="form-group">
                <label>Viáticos</label>
                <InputText v-model="form.viaticos" type="number" class="w-full mb-2" />
              </div>
            </div>
          </div>
          <div class="modal-actions">
            <Button label="Guardar" icon="pi pi-save" type="submit" />
            <Button label="Cancelar" icon="pi pi-times" class="p-button-secondary" type="button" @click="cerrar" />
          </div>
        </div>
      </div>
    </form>
    <Dialog v-model:visible="showResultDialog" header="Resultado" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ resultMessage }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="showResultDialog = false" class="mt-3" />
    </Dialog>
  </div>
</template>

<script setup>
import { ref, onMounted, computed } from 'vue';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
import { addReporteServicio, getReportePorAsignacion } from '@/services/reportesServicio';
import { getDetalleVenta } from '@/services/ventasService';
import { useRoute } from 'vue-router';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { getUsuarios } from '@/services/usuariosService';
import { getVentas } from '@/services/ventasService';
import InputNumber from 'primevue/inputnumber';

const emit = defineEmits(['close', 'saved']);

const route = useRoute();
const asignacionIdValido = computed(() => Number.isInteger(Number(route.params.asignacionId)) && Number(route.params.asignacionId) > 0);
const asignacionIdCentral = computed(() => asignacionIdValido.value ? Number(route.params.asignacionId) : null);
const asignacion = ref(null);

// --- Ensure assignment ID is valid and centralize its use ---
const tiposServicio = ['Instalación', 'Reinstalación', 'Revisión', 'Desinstalación', 'Búsqueda'];
const formasPago = ['Efectivo Entregado al tecnico', 'Transferencia', 'Depósito', ];

const tecnicoNombre = ref('');
const tecnicoTelefono = ref('');

const form = ref({
  tipo_servicio: '',
  lugar_instalacion: '',
  marca: '',
  submarca: '',
  modelo: '',
  placas: '',
  color: '',
  numero_economico: '',
  equipo_plan: '',
  imei: '',
  serie: '',
  accesorios: '',
  sim_proveedor: '',
  sim_serie: '',
  sim_instalador: '',
  sim_telefono: '',
  bateria: '',
  ignicion: '',
  corte: '',
  ubicacion_corte: '',
  observaciones: '',
  plataforma: '',
  usuario: '',
  subtotal: '',
  forma_pago: '',
  pagado: false,
  nombre_cliente: '',
  firma_cliente: '',
  nombre_instalador: '',
  firma_instalador: '',
  asignacion_id: undefined, // Se setea en onMounted
  monto_tecnico: 0,
  viaticos: 0
});

const loading = ref(false);
const showResultDialog = ref(false);
const resultMessage = ref('');
const reporteExistente = ref(false);

const clienteUsuariosOptions = ref([]);
const clientePlataformasOptions = ref([]);
const pagos = ref([]);

async function cargarPagos() {
  pagos.value = [];
  // Si tienes lógica real para cargar pagos, ponla aquí
}

async function cargarDatosTecnico() {
  try {
    if (!asignacion.value) return;
    let usuarios = await getUsuarios();
    let tecnico = usuarios.find(u => 
      u.username?.toLowerCase() === asignacion.value.tecnico?.toLowerCase() ||
      u.nombre?.toLowerCase() === asignacion.value.tecnico?.toLowerCase()
    );
    console.log('Datos del técnico:', tecnico);
    
    if (tecnico) {
      tecnicoNombre.value = tecnico.username || tecnico.nombre || '';
      tecnicoTelefono.value = tecnico.telefono || '';
      form.value.sim_instalador = tecnicoNombre.value;
      form.value.sim_telefono = tecnicoTelefono.value;
      form.value.nombre_instalador = tecnicoNombre.value;
    } else if (asignacion.value.tecnico) {
      tecnicoNombre.value = asignacion.value.tecnico;
      tecnicoTelefono.value = '';
      form.value.sim_instalador = asignacion.value.tecnico;
      form.value.nombre_instalador = asignacion.value.tecnico;
    }
  } catch (e) {
    console.error('Error en cargarDatosTecnico:', e);
  }
}

async function cargarDatosCliente() {
  try {
    if (!asignacion.value) return;
    const { getClientes } = await import('@/services/clientesService');
    const clientes = await getClientes();
    const cliente = clientes.find(c => c.id == asignacion.value.cliente_id);
    if (cliente) {
      console.log('Datos del cliente:', cliente);
      
      form.value.nombre_cliente = cliente.nombre || '';
      form.value.telefono_cliente = cliente.telefonos?.join(', ') || '';
      clienteUsuariosOptions.value = Array.isArray(cliente.usuarios)
        ? cliente.usuarios.map(u => ({ label: u, value: u }))
        : [];
      clientePlataformasOptions.value = Array.isArray(cliente.plataformas)
        ? cliente.plataformas.map(p => ({ label: p, value: p }))
        : [];
      console.log('Plataformas del cliente:', clientePlataformasOptions.value);
      
    }
    if (asignacion.value.venta_id) {
      const ventas = await getVentas();
      const venta = ventas.find(v => v.id == asignacion.value.venta_id);
      if (venta) {
        console.log('Datos de la venta:', venta);
        
        form.value.subtotal = venta.total || '';
        form.value.total = venta.total || '';
        form.value.forma_pago = venta.terminos_pago || '';
        try {
          const detalle = await getDetalleVenta(venta.id);
          if (Array.isArray(detalle) && detalle.length > 0) {
            const art = detalle[0];
            form.value.modelo = art.modelo || art.modelo_gps || '';
            form.value.imei = art.imei || '';
            form.value.serie = art.serie || '';
            form.value.equipo_plan =  '';
            form.value.placas = art.placas || '';
            form.value.color = art.color || '';
            form.value.numero_economico = art.numero_economico || '';
            form.value.accesorios = art.accesorios || '';
          }
        } catch (e) {
          console.error('Error en getDetalleVenta:', e);
        }
      }
    }
  } catch (e) {
    console.error('Error en cargarDatosCliente:', e);
  }
}

async function checkReporteExistente() {
  try {
    if (!asignacionIdValido.value) {
      reporteExistente.value = false;
      return;
    }
    const reporte = await getReportePorAsignacion(Number(asignacionIdCentral.value));
    console.log('Reporte existente:', reporte);
    reporteExistente.value = !!reporte;
  } catch (e) {
    console.error('Error en checkReporteExistente:', e);
    reporteExistente.value = false;
  }
}


onMounted(async () => {
  loading.value = true;
  console.log('route:', route);
  console.log('asignacionIdCentral:', asignacionIdCentral.value);
  try {
  const asignaciones = await getAsignacionesTecnicos();
  console.log('Asignaciones recibidas:', asignaciones);
  // Si asignacionIdCentral.value es venta_id, buscar por venta_id, si es id de asignación, buscar por id
  asignacion.value = asignaciones.find(a => String(a.id) === String(asignacionIdCentral.value) || String(a.venta_id) === String(asignacionIdCentral.value));
  console.log('Asignación encontrada:', asignacion.value?.id);
    if (!asignacion.value) {
      loading.value = false;
      resultMessage.value = 'No se encontró la asignación para el ID proporcionado.';
      showResultDialog.value = true;
      return;
    }
    form.value.asignacion_id = asignacion.value.id;
    await checkReporteExistente();
    await cargarDatosTecnico();
    await cargarDatosCliente();
    console.log('Datos del formulario cargados:', form.value);
    try {
      await cargarPagos();
    } catch (e) {
      console.error('Error en cargarPagos:', e);
    }
    loading.value = false;
  } catch (e) {
    console.error('Error en onMounted:', e);
    loading.value = false;
  }
});

function cerrar() {
  emit('close');
}

async function guardar() {
  if (!asignacionIdValido.value) {
    resultMessage.value = 'ID de asignación inválido. No se puede guardar el reporte.';
    showResultDialog.value = true;
    return;
  }
  loading.value = true;
  try {
    let asignaciones = await getAsignacionesTecnicos();
    const asignacion = asignaciones.find(a => String(a.id) === String(asignacionIdCentral.value) || String(a.venta_id) === String(asignacionIdCentral.value));
    if (!asignacion || !asignacion.venta_id) {
      resultMessage.value = 'No se puede guardar el reporte: falta asignación o venta asociada.';
      loading.value = false;
      showResultDialog.value = true;
      return;
    }
    const payload = {
      ...form.value,
      plataforma: typeof form.value.plataforma === 'object' ? form.value.plataforma.value : form.value.plataforma,
      usuario: typeof form.value.usuario === 'object' ? form.value.usuario.value : form.value.usuario,
      subtotal: String(form.value.subtotal ?? ''),
      asignacion_id: asignacion.id
    };
    await addReporteServicio(payload);
    resultMessage.value = 'Reporte de servicio guardado correctamente.';
    emit('saved');
    await checkReporteExistente();
    cerrar();
  } catch (e) {
    console.error('Error en guardar:', e);
    resultMessage.value = 'Error al guardar el reporte de servicio.';
  } finally {
    loading.value = false;
    showResultDialog.value = true;
  }
}

function formatearFecha(fecha) {
  if (!fecha) return '';
  const d = new Date(fecha);
  const dia = String(d.getDate()).padStart(2, '0');
  const mes = String(d.getMonth() + 1).padStart(2, '0');
  const anio = d.getFullYear();
  return `${dia}/${mes}/${anio}`;
}

function formatoMoneda(valor) {
  if (isNaN(valor)) return '$0.00';
  return valor.toLocaleString('es-MX', { style: 'currency', currency: 'MXN', minimumFractionDigits: 2 });
}
</script>

<style scoped>
.reporte-servicio-container {
  max-width: 900px;
  margin: 2.5rem auto;
  background: var(--color-card);
  color: var(--color-text);
  border-radius: 16px;
  box-shadow: 0 4px 24px rgba(0,0,0,0.13);
  padding: 2.5rem 2rem;
}
.reporte-title {
  color: var(--color-title, #ff4081);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 2rem;
  font-weight: bold;
  letter-spacing: 1px;
}
.reporte-form {
  width: 100%;
}
.form-row {
  display: flex;
  gap: 2.5rem;
  margin-bottom: 1.2rem;
}
.form-col {
  flex: 1 1 0;
  min-width: 320px;
  display: flex;
  flex-direction: column;
}
.section-title {
  color: var(--color-title, #ff4081);
  margin-top: 2rem;
  margin-bottom: 1rem;
  font-size: 1.15rem;
  font-weight: 600;
  letter-spacing: 0.5px;
}
.form-group {
  margin-bottom: 1.2rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-title, #ff4081);
}
.w-full {
  width: 100%;
}
.mb-2 {
  margin-bottom: 0.7rem;
}
.checkbox-group {
  display: flex;
  align-items: center;
  gap: 0.5rem;
  margin-top: 0.5rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}
.loader-overlay {
  position: absolute;
  top: 0; left: 0; right: 0; bottom: 0;
  background: rgba(0,0,0,0.2);
  display: flex;
  align-items: center;
  justify-content: center;
  z-index: 10;
}
.alert-existente {
  color: var(--color-on-error);
  background: var(--color-error);
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: bold;
}
.error-bg {
  color: var(--color-on-error);
  background: var(--color-error);
}
@media (max-width: 900px) {
  .form-row {
    flex-direction: column;
    gap: 1.2rem;
  }
  .form-col {
    min-width: 0;
  }
}
@media (max-width: 700px) {
  .reporte-servicio-container {
    padding: 1rem 0.5rem;
  }
}
</style>