<template>
  <div class="reporte-servicio-container">
    <h2 class="reporte-title">Reporte de Servicio</h2>
    <form class="reporte-form" @submit.prevent="guardar">
      <div class="form-row">
        <div class="form-col">
          <div class="form-group">
            <label>Tipo de servicio</label>
            <Dropdown v-model="form.tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full" />
          </div>
          <div class="form-group">
            <label>Lugar / Centro de instalación</label>
            <InputText v-model="form.lugar_instalacion" class="w-full" placeholder="Opcional" />
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
            <Dropdown v-model="form.imei" :options="imeiOptions" placeholder="IMEI (stock)" class="w-full mb-2" optionLabel="label" optionValue="value" :filter="true" />
            <Dropdown v-model="form.sim_serie" :options="simSerieOptions" placeholder="SIM (stock)" class="w-full mb-2" optionLabel="label" optionValue="value" :filter="true" />
            <InputText v-model="form.accesorios" placeholder="Accesorios adicionales (Botón/Micro/Etc.)" class="w-full mb-2" />
            <InputText v-model="form.ubicacion_gps" placeholder="Ubicación del GPS" class="w-full mb-2" />
            <InputText v-model="form.ubicacion_bloqueo" placeholder="Ubicación del Bloqueo (Bomba/Switch/Ignición/Etc.)" class="w-full mb-2" />
          </div>
          <div class="form-group">
            <label>Observaciones</label>
            <Textarea v-model="form.observaciones" rows="2" class="w-full" />
          </div>
          <h4 class="section-title">Datos del cobro</h4>
          <div class="form-group">
            <label>Subtotal (orden de servicio)</label>
            <InputText v-model="form.subtotal" placeholder="Subtotal" class="w-full mb-2" :disabled="true" />
          </div>
          <div class="form-group">
            <label>Total a cobrar</label>
            <InputNumber v-model="form.total" placeholder="Total a cobrar" class="w-full mb-2" />
            <small>El instalador puede modificar este valor si hay algún ajuste.</small>
          </div>
          <div class="form-group">
            <label>Método de pago</label>
            <InputText v-model="form.forma_pago" placeholder="Método de pago" class="w-full mb-2" :disabled="true" />
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
    </form>
    <Dialog v-model:visible="showResultDialog" header="Resultado" :modal="true" :closable="false">
      <div style="padding:1.5rem; text-align:center;">
        <span>{{ resultMessage }}</span>
      </div>
      <Button label="Aceptar" icon="pi pi-check" @click="onDialogAccept" class="mt-3" />
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
import { useRoute, useRouter } from 'vue-router';
import { getAsignacionesTecnicos } from '@/services/asignacionesService';
import { getUsuarios } from '@/services/usuariosService';
import { getVentas } from '@/services/ventasService';
import InputNumber from 'primevue/inputnumber';
import { getImeisPorUbicacion, getUbicaciones } from '@/services/ubicacionesService';

const emit = defineEmits(['close', 'saved']);

const route = useRoute();
const router = useRouter();
const asignacionIdValido = computed(() => Number.isInteger(Number(route.params.asignacionId)) && Number(route.params.asignacionId) > 0);
const asignacionIdCentral = computed(() => asignacionIdValido.value ? Number(route.params.asignacionId) : null);
const asignacion = ref(null);

// --- Ensure assignment ID is valid and centralize its use ---
const tiposServicio = ['Instalación', 'Reinstalación', 'Revisión', 'Desinstalación', 'Búsqueda'];
const formasPago = ['Efectivo Entregado al tecnico', 'Transferencia', 'Depósito', ];

const tecnicoNombre = ref('');
const tecnicoTelefono = ref('');
const proveedoresSim = [ { label: 'TELCEL', value: 'TELCEL' }, { label: 'ESPAÑOL', value: 'ESPAÑOL' } ];
const imeiOptions = ref([]); // Para IMEI (filtrado por artículos de la orden)
const simSerieOptions = ref([]); // Para Serie (todo el stock de la ubicación)
const allowedArticuloIds = ref(new Set());
const allowedArticuloNames = ref(new Set());
const ubicacionId = ref(null);

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
const saveSuccess = ref(false);
const imeiUpdateError = ref(false);

const clienteUsuariosOptions = ref([]);
const clientePlataformasOptions = ref([]);
const pagos = ref([]);
const imeisStockRaw = ref([]);

async function cargarImeisDeUbicacion(id) {
  try {
    // Preferir /imeis completo y filtrar por ubicacion_id si la API pública es esa que compartiste
    const res = await fetch(`${import.meta.env.VITE_API_URL}/imeis`);
    const todos = await res.json();
    const imeisUbicacion = Array.isArray(todos) ? todos.filter(i => Number(i.ubicacion_id) === Number(id)) : [];
    imeisStockRaw.value = imeisUbicacion.filter(i => ['Disponible', 'Devuelto'].includes(i.status));
    // Para Serie (ESPAÑOL) dejamos todo el stock de la ubicación
  simSerieOptions.value = imeisStockRaw.value.map(i => ({ label: `${i.imei} — ${i.articulo_nombre || ''}`, value: String(i.imei) }));
    try {
      console.group('Reporte de Servicio');
      console.log('Ubicación (ID):', id);
      console.log('Stock de la ubicación (IMEIs):', imeisStockRaw.value);
      console.groupEnd();
    } catch (_) {}
  } catch (e) {
    console.error('Error cargando IMEIs (stock) desde /imeis:', e);
  }
}

function buildImeiOptions() {
  try {
    const byArticle = (r) => {
      const okId = r.articulo_id && allowedArticuloIds.value.has(Number(r.articulo_id));
      const okName = r.articulo_nombre && allowedArticuloNames.value.has(String(r.articulo_nombre).toLowerCase());
      return okId || okName;
    };
    const filtered = imeisStockRaw.value.filter(byArticle);
    imeiOptions.value = filtered.map(i => ({ label: `${i.imei} — ${i.articulo_nombre || ''}`, value: i.imei }));
  } catch (_) {
    imeiOptions.value = imeisStockRaw.value.map(i => ({ label: `${i.imei} — ${i.articulo_nombre || ''}`, value: i.imei }));
  }
}

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
  //
    
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
  //
      
      form.value.nombre_cliente = cliente.nombre || '';
      form.value.telefono_cliente = cliente.telefonos?.join(', ') || '';
      clienteUsuariosOptions.value = Array.isArray(cliente.usuarios)
        ? cliente.usuarios.map(u => ({ label: u, value: u }))
        : [];
      clientePlataformasOptions.value = Array.isArray(cliente.plataformas)
        ? cliente.plataformas.map(p => ({ label: p, value: p }))
        : [];
  //
      
    }
    if (asignacion.value.venta_id) {
      const ventas = await getVentas();
      const venta = ventas.find(v => v.id == asignacion.value.venta_id);
      if (venta) {
        console.log('Venta encontrada para la asignación:', venta);
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
          // Construir conjuntos de artículos permitidos para filtrar IMEIs
          try {
            const ids = new Set();
            const names = new Set();
            for (const d of detalle || []) {
              if (d.articulo_id) ids.add(Number(d.articulo_id));
              if (d.articulo_nombre) names.add(String(d.articulo_nombre).toLowerCase());
            }
            allowedArticuloIds.value = ids;
            allowedArticuloNames.value = names;
          } catch (_) {}
        } catch (e) {
          console.error('Error en getDetalleVenta:', e);
        }
        // Determinar ubicacion_id: 1) por nombre de almacén; 2) por campo venta.ubicacion_id; 3) deducir por IMEI
        try {
          const ubicaciones = await getUbicaciones();
          const uMatch = ubicaciones.find(u => String(u.nombre || '').toLowerCase() === String(venta.almacen || '').toLowerCase());
          if (uMatch?.id) {
            ubicacionId.value = uMatch.id;
          }
        } catch (e) {
          // ignora
        }
        if (!ubicacionId.value) {
          ubicacionId.value = venta.ubicacion_id || null;
        }
        if (ubicacionId.value) {
          await cargarImeisDeUbicacion(ubicacionId.value);
          buildImeiOptions();
        } else {
          // Intentar deducir la ubicación a partir del IMEI existente en el detalle
          const imeiBase = form.value.imei;
          if (imeiBase) {
            try {
              const res = await fetch(`${import.meta.env.VITE_API_URL}/buscar-imei?digitos=${encodeURIComponent(String(imeiBase))}`);
              const resultados = await res.json();
              const ubicacionNombre = Array.isArray(resultados) && resultados[0]?.ubicacion ? resultados[0].ubicacion : null;
              if (ubicacionNombre) {
                const ubicaciones = await getUbicaciones();
                const ubic = ubicaciones.find(u => (u.nombre || '').toLowerCase() === String(ubicacionNombre).toLowerCase());
                if (ubic?.id) {
                  ubicacionId.value = ubic.id;
                  await cargarImeisDeUbicacion(ubicacionId.value);
                  buildImeiOptions();
                }
              }
            } catch (e) {
              console.error('No se pudo deducir la ubicación desde IMEI:', e);
            }
          }
        }
      }
    }
  } catch (e) {
    console.error('Error en cargarDatosCliente:', e);
  }
}

onMounted(async () => {
  loading.value = true;
  //
  //
  try {
  const asignaciones = await getAsignacionesTecnicos();
  //
  // Si asignacionIdCentral.value es venta_id, buscar por venta_id, si es id de asignación, buscar por id
  asignacion.value = asignaciones.find(a => String(a.id) === String(asignacionIdCentral.value) || String(a.venta_id) === String(asignacionIdCentral.value));
  //
    if (!asignacion.value) {
      loading.value = false;
      resultMessage.value = 'No se encontró la asignación para el ID proporcionado.';
      showResultDialog.value = true;
      return;
    }
    form.value.asignacion_id = asignacion.value.id;
    await cargarDatosTecnico();
    await cargarDatosCliente();
  //
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
  router.push('/');
}

async function guardar() {
  if (!asignacionIdValido.value) {
    resultMessage.value = 'ID de asignación inválido. No se puede guardar el reporte.';
    showResultDialog.value = true;
    return;
  }
  loading.value = true;
  try {
    saveSuccess.value = false;
    imeiUpdateError.value = false;
    let asignaciones = await getAsignacionesTecnicos();
    const asignacion = asignaciones.find(a => String(a.id) === String(asignacionIdCentral.value) || String(a.venta_id) === String(asignacionIdCentral.value));
    if (!asignacion || !asignacion.venta_id) {
      resultMessage.value = 'No se puede guardar el reporte: falta asignación o venta asociada.';
      loading.value = false;
      showResultDialog.value = true;
      return;
    }
    const payload = {
      asignacion_id: asignacion.id,
      tipo_servicio: form.value.tipo_servicio || '',
      lugar_instalacion: form.value.lugar_instalacion || '',
      marca: form.value.marca || '',
      submarca: form.value.submarca || '',
      modelo: form.value.modelo || '',
      placas: form.value.placas || '',
      color: form.value.color || '',
      numero_economico: form.value.numero_economico || '',
      equipo_plan: form.value.equipo_plan || '',
      imei: form.value.imei || '',
      serie: form.value.serie || '',
      accesorios: form.value.accesorios || '',
      sim_proveedor: form.value.sim_proveedor || '',
      sim_serie: form.value.sim_serie || '',
      sim_instalador: form.value.sim_instalador || '',
      sim_telefono: form.value.sim_telefono || '',
      bateria: form.value.bateria || '',
      ignicion: form.value.ignicion || '',
      corte: form.value.corte || '',
      ubicacion_corte: form.value.ubicacion_corte || '',
      observaciones: form.value.observaciones || '',
      plataforma: form.value.plataforma || '',
      usuario: form.value.usuario || '',
      subtotal: String(form.value.subtotal ?? ''),
      forma_pago: form.value.forma_pago || '',
      pagado: !!form.value.pagado,
      nombre_cliente: form.value.nombre_cliente || '',
      firma_cliente: form.value.firma_cliente || '',
      nombre_instalador: form.value.nombre_instalador || '',
      firma_instalador: form.value.firma_instalador || '',
      total: Number(form.value.total) || 0,
      monto_tecnico: Number(form.value.monto_tecnico) || 0,
      viaticos: Number(form.value.viaticos) || 0,
      modelo_gps: form.value.modelo_gps || '',
      ubicacion_gps: form.value.ubicacion_gps || '',
      ubicacion_bloqueo: form.value.ubicacion_bloqueo || ''
    };
    const resp = await addReporteServicio(payload);
    const baseMessage = (resp && typeof resp === 'object' && 'message' in resp)
      ? String(resp.message)
      : 'Reporte de servicio creado exitosamente';
    // Marcar IMEI y SIM como vendidos si se seleccionaron
    {
      const setImeis = new Set();
      if (payload.imei) setImeis.add(payload.imei);
      if (payload.sim_serie) setImeis.add(payload.sim_serie);
      try {
        for (const imei of Array.from(setImeis)) {
          await fetch(`${import.meta.env.VITE_API_URL}/imeis/${encodeURIComponent(imei)}`, {
            method: 'PUT',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ status: 'Vendido' })
          });
        }
      } catch (e) {
        console.error('Error marcando IMEIs como vendidos:', e);
        imeiUpdateError.value = true;
      }
    }
    if (!imeiUpdateError.value) {
      resultMessage.value = `${baseMessage}. Al aceptar te llevaré al inicio.`;
      saveSuccess.value = true;
    } else {
      resultMessage.value = `${baseMessage}, pero hubo un problema actualizando los IMEIs. Puedes revisar el estado en Inventario.`;
      saveSuccess.value = false;
    }
    emit('saved');
  } catch (e) {
    console.error('Error en guardar:', e);
    resultMessage.value = 'Error al guardar el reporte de servicio.';
    saveSuccess.value = false;
  } finally {
    loading.value = false;
    showResultDialog.value = true;
  }
}

function onDialogAccept() {
  showResultDialog.value = false;
  if (saveSuccess.value) {
    router.push('/');
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
@import '@/assets/main.css';
.reporte-servicio-container {
  max-width: 600px;
  margin: 2rem auto;
  background: var(--color-card);
  color: var(--color-text);
  border-radius: 10px;
  box-shadow: var(--shadow-1);
  padding: 2rem 1rem;
}
.reporte-title {
  color: var(--color-title);
  text-align: center;
  margin-bottom: 2rem;
  font-size: 1.5rem;
  font-weight: bold;
}
.reporte-form {
  width: 100%;
}
.form-row {
  display: flex;
  flex-direction: column;
  gap: 1.2rem;
  margin-bottom: 1.2rem;
}
.form-col {
  flex: 1 1 0;
  min-width: 0;
  display: flex;
  flex-direction: column;
}
.section-title {
  color: var(--color-title);
  margin-top: 1.5rem;
  margin-bottom: 1rem;
  font-size: 1rem;
  font-weight: 600;
}
.form-group {
  margin-bottom: 1rem;
}
label {
  display: block;
  margin-bottom: 0.5rem;
  font-weight: bold;
  color: var(--color-title);
}
.w-full {
  width: 100%;
}
.mb-2 {
  margin-bottom: 0.7rem;
}
.modal-actions {
  display: flex;
  justify-content: flex-end;
  gap: 1rem;
  margin-top: 2rem;
}
@media (max-width: 700px) {
  .reporte-servicio-container {
    padding: 1rem 0.5rem;
    max-width: 100vw;
  }
}
</style>