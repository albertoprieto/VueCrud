<template>
  <div class="reporte-servicio-container">
    <h2 class="reporte-title">Reporte de Servicio</h2>
    <form class="reporte-form" @submit.prevent="guardar">
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
                <InputText v-model="form.sim_instalador" placeholder="Instalador" class="w-full mb-2" />
                <InputText v-model="form.sim_telefono" placeholder="Teléfono" class="w-full mb-2" />
              </div>
              <h4 class="section-title">Firmas y aviso</h4>
              <div class="form-group">
                <InputText v-model="form.nombre_cliente" placeholder="Nombre del cliente" class="w-full mb-2" />
                <InputText v-model="form.firma_cliente" placeholder="Firma del cliente" class="w-full mb-2" />
                <InputText v-model="form.nombre_instalador" placeholder="Nombre del instalador" class="w-full mb-2" />
                <InputText v-model="form.firma_instalador" placeholder="Firma del instalador" class="w-full mb-2" />
              </div>
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
                <InputText v-model="form.plataforma" placeholder="Plataforma" class="w-full mb-2" :disabled="true" />
                <InputText v-model="form.usuario" placeholder="Usuario" class="w-full mb-2" :disabled="true" />
              </div>
              <h4 class="section-title">Venta y pago</h4>
              <div class="form-group">
                <InputText v-model="form.subtotal" placeholder="Subtotal" class="w-full mb-2" :disabled="true" />
                <Dropdown v-model="form.forma_pago" :options="formasPago" placeholder="Forma de pago" class="w-full mb-2" />
                <div class="checkbox-group mb-2">
                  <Checkbox v-model="form.pagado" :binary="true" inputId="pagado" />
                  <label for="pagado">Pagado</label>
                </div>
              </div>
              <div class="form-group">
                <small>Aviso de privacidad: Sus datos serán tratados conforme a la ley...</small>
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
import { ref, onMounted } from 'vue';
import Textarea from 'primevue/textarea';
import InputText from 'primevue/inputtext';
import Dropdown from 'primevue/dropdown';
import Button from 'primevue/button';
import Checkbox from 'primevue/checkbox';
import Dialog from 'primevue/dialog';
import { addReporteServicio, getReportePorAsignacion } from '@/services/reportesServicio';
import { useRoute } from 'vue-router';

const route = useRoute();
const asignacionId = Number(route.params.asignacionId);

const props = defineProps({ asignacionId: Number, ventaDetalle: Object, cliente: Object });
const emit = defineEmits(['close', 'saved']);

const tiposServicio = ['Instalación', 'Reinstalación', 'Revisión', 'Desinstalación', 'Búsqueda'];
const formasPago = ['Efectivo', 'Transferencia', 'Depósito'];

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
  plataforma: props.cliente?.plataformas?.[0] || '',
  usuario: props.cliente?.usuarios?.[0] || '',
  subtotal: props.ventaDetalle?.total || '',
  forma_pago: '',
  pagado: false,
  nombre_cliente: props.cliente?.nombre || '',
  firma_cliente: '',
  nombre_instalador: '',
  firma_instalador: '',
  asignacion_id: props.asignacionId
});

const loading = ref(false);
const showResultDialog = ref(false);
const resultMessage = ref('');
const reporteExistente = ref(false);

async function checkReporteExistente() {
  const reporte = await getReportePorAsignacion(props.asignacionId || asignacionId);
  reporteExistente.value = !!reporte;
}

onMounted(checkReporteExistente);

function cerrar() {
  emit('close');
}

async function guardar() {
  loading.value = true;
  try {
    form.value.asignacion_id = props.asignacionId || Number(route.params.asignacionId);
    await addReporteServicio(form.value);
    resultMessage.value = 'Reporte de servicio guardado correctamente.';
    emit('saved');
    await checkReporteExistente();
    cerrar();
  } catch (e) {
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
  color: #fff;
  background: #d32f2f;
  padding: 1rem;
  border-radius: 8px;
  margin-bottom: 1.5rem;
  text-align: center;
  font-weight: bold;
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