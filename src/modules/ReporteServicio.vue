<template>
  <div class="reporte-servicio-container">
    <h2 class="reporte-title">Reporte de Servicio</h2>
    <form class="reporte-form" @submit.prevent="guardar">
      <!-- Bloque global: una sola columna a lo ancho -->
      <div class="global-header col-block full-width">
        <div class="form-group">
          <label class="required-label">Tipo de servicio</label>
          <Dropdown v-model="form.tipo_servicio" :options="tiposServicio" placeholder="Selecciona" class="w-full" :class="{'p-invalid': isCampoInvalido('tipo_servicio')}" />
          <small v-if="isCampoInvalido('tipo_servicio')" class="error-msg">Requerido</small>
        </div>
        <div class="form-group">
          <label>Lugar / Centro de instalación</label>
          <InputText v-model="form.lugar_instalacion" class="w-full" placeholder="Opcional" />
        </div>
      </div>

      <!-- Bloques por artículo: máximo 2 columnas -->
      <div class="line-items-grid" :class="{ 'two-cols': shouldUseTwoCols }">
        <div class="col-block" v-for="linea in lineItems" :key="`art-${linea.lineaId}`">
          <h4 class="section-title articulo-title">Artículo: {{ linea.articulo_nombre }}</h4>

          <!-- Datos del vehículo (por artículo) -->
          <div class="form-group">
            <h5 class="section-subtitle">Datos del vehículo</h5>
            <div class="form-row">
              <InputText v-model="linea.marca" placeholder="Marca" class="w-full mb-2" />
              <InputText v-model="linea.submarca" placeholder="Submarca" class="w-full mb-2" />
            </div>
            <div class="form-row">
              <InputText v-model="linea.modelo" placeholder="Modelo" class="w-full mb-2" />
              <InputText v-model="linea.placas" placeholder="Placas" class="w-full mb-2" />
            </div>
            <div class="form-row">
              <InputText v-model="linea.color" placeholder="Color" class="w-full mb-2" />
              <InputText v-model="linea.numero_economico" placeholder="Número económico" class="w-full mb-2" />
            </div>
          </div>

          <!-- Datos del dispositivo (por artículo) -->
          <div class="form-group">
            <h5 class="section-subtitle">Datos del dispositivo (opcionales)</h5>
            <div class="form-row">
              <InputText v-model="linea.modelo_gps" placeholder="Modelo GPS" class="w-full mb-2" />
              <InputText v-model="linea.accesorios" placeholder="Accesorios adicionales (Botón/Micro/Etc.)" class="w-full mb-2" />
            </div>
            <div class="form-row">
              <InputText v-model="linea.ubicacion_gps" placeholder="Ubicación del GPS" class="w-full mb-2" />
              <InputText v-model="linea.ubicacion_bloqueo" placeholder="Ubicación del Bloqueo (Bomba/Switch/Ignición/Etc.)" class="w-full mb-2" />
            </div>
          </div>

          <!-- Asignación IMEIs y SIM por artículo/slot -->
          <div class="line-item-block">
            <div class="line-header">
              <strong>Asignación de IMEIs y SIM</strong>
            </div>
            <div class="slots-grid">
              <div v-for="(val, idx) in linea.selecciones" :key="`slot-${linea.lineaId}-${idx}`" class="slot-item">
                <div class="form-group">
                  <label>IMEI {{ idx+1 }}</label>
                  <Dropdown
                    :options="opcionesVisibles(linea, idx)"
                    optionLabel="label"
                    optionValue="value"
                    v-model="linea.selecciones[idx]"
                    placeholder="Selecciona IMEI"
                    class="w-full mb-2"
                  />
                </div>
                <div class="form-group">
                  <label>SIM {{ idx+1 }}</label>
                  <Dropdown
                    :options="simOpcionesVisiblesLinea(linea, idx)"
                    optionLabel="label"
                    optionValue="value"
                    v-model="linea.sims[idx]"
                    placeholder="Selecciona SIM"
                    class="w-full mb-2"
                  />
                </div>
              </div>
            </div>
          </div>
          <div v-if="linea.imeisPosibles.length < linea.selecciones.length" class="warning-block">
            <p><strong>Advertencia:</strong> Stock insuficiente para {{ linea.articulo_nombre }} (requiere {{ linea.selecciones.length }}, disponibles {{ linea.imeisPosibles.length }}).</p>
          </div>
        </div>
      </div>

      <!-- Sección de cobro y observaciones: 2 columnas -->
      <div class="cobro-section col-block full-width">
        <h4 class="section-title">Datos del cobro</h4>
        <div class="cobro-grid two-cols">
          <div class="form-group">
            <label class="required-label">Subtotal (orden de servicio)</label>
            <InputText v-model="form.subtotal" placeholder="Subtotal" class="w-full" :disabled="true" :class="{'p-invalid': isCampoInvalido('subtotal')}" />
          </div>
          <div class="form-group">
            <label class="required-label">Total a cobrar</label>
            <InputNumber v-model="form.total" placeholder="Total a cobrar" class="w-full" :class="{'p-invalid': isCampoInvalido('total')}" />
            <small>El instalador puede modificar este valor si hay algún ajuste.</small>
          </div>
          <div class="form-group monto-tecnico-group">
            <label>Monto cobrado por el técnico</label>
            <div class="monto-tecnico-row">
              <InputNumber v-model="form.monto_tecnico" placeholder="Monto técnico" class="w-full" :disabled="usarTotalMontoTecnico" />
              <div class="checkbox-inline">
                <Checkbox v-model="usarTotalMontoTecnico" :binary="true" inputId="chkUsarTotal" />
                <label for="chkUsarTotal" class="inline-label">Total</label>
              </div>
            </div>
          </div>
          <div class="form-group">
            <label>Método de pago</label>
            <InputText v-model="form.forma_pago" placeholder="Método de pago" class="w-full" :disabled="true" />
          </div>
          <div class="form-group">
            <label>Viáticos</label>
            <InputText v-model="form.viaticos" type="number" class="w-full" />
          </div>
          <div class="form-group span-2">
            <label>Observaciones</label>
            <Textarea v-model="form.observaciones" rows="3" class="w-full" />
          </div>
        </div>
      </div>

      <div class="modal-actions full-width">
        <Button label="Guardar" icon="pi pi-save" type="submit" :disabled="!formCompleto" :class="{ 'btn-disabled-force': !formCompleto }" />
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
import { ref, onMounted, computed, watch, nextTick } from 'vue';
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
import { getTodosArticulos } from '@/services/articulosService';

const emit = defineEmits(['close', 'saved']);

const route = useRoute();
const router = useRouter();
const asignacionIdValido = computed(() => Number.isInteger(Number(route.params.asignacionId)) && Number(route.params.asignacionId) > 0);
const asignacionIdCentral = computed(() => asignacionIdValido.value ? Number(route.params.asignacionId) : null);
const asignacion = ref(null);

const tiposServicio = ['Instalación', 'Reinstalación', 'Revisión', 'Desinstalación', 'Búsqueda'];
const formasPago = ['Efectivo Entregado al tecnico', 'Transferencia', 'Depósito', ];

const tecnicoNombre = ref('');
const tecnicoTelefono = ref('');
const proveedoresSim = [ { label: 'TELCEL', value: 'TELCEL' }, { label: 'ESPAÑOL', value: 'ESPAÑOL' } ];
const imeiOptions = ref([]); // Para IMEI (filtrado por artículos de la orden)
const simSerieOptions = ref([]); // Para Serie (stock de la ubicación filtrado)
// Eliminamos simSelecciones global a favor de sims por línea

const ubicacionId = ref(null); // Ubicación (almacén) asociada a la venta/asignación
const allowedArticuloIds = ref(new Set());
const allowedArticuloNames = ref(new Set());
const ALLOW_AUTO_UBICACION_DEDUCCION = false;

function buildImeiOptions(){
  imeiOptions.value = imeisStockRaw.value
    .filter(r => !esSimArticuloNombre(r.articulo_nombre))
    .map(r => ({ label: `${r.imei} — ${r.articulo_nombre}`, value: String(r.imei) }));
}

function normalizeTexto(v){
  return String(v||'').toLowerCase().normalize('NFD').replace(/\p{Diacritic}/gu,'').trim();
}

function esSimArticuloNombre(nombre){
  return /\bsim\b/.test(normalizeTexto(nombre));
}

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
  asignacion_id: undefined,
  monto_tecnico: 0,
  viaticos: 0,
  modelo_gps: '',
  ubicacion_gps: '',
  ubicacion_bloqueo: ''
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
const articulosIndex = ref({});

const attemptedSubmit = ref(false);
const usarTotalMontoTecnico = ref(false);

async function cargarArticulos(){
  try {
    const arts = await getTodosArticulos();
    if (Array.isArray(arts)) {
      articulosIndex.value = Object.fromEntries(arts.map(a => [a.id, a]));
    }
  } catch (e) {
    console.error('Error cargando articulos:', e);
  }
}

async function cargarImeisDeUbicacion(id){
  try {
    const res = await fetch(`${import.meta.env.VITE_API_URL}/imeis`);
    const todos = await res.json();
    const imeisUbicacion = Array.isArray(todos) ? todos.filter(i => Number(i.ubicacion_id) === Number(id)) : [];
    imeisStockRaw.value = imeisUbicacion.filter(i => ['Disponible','Devuelto'].includes(i.status));
    buildSimSerieOptions();
    buildLineItems();
  } catch(e){ console.error('Error cargando IMEIs:', e); }
}

watch(ubicacionId, (val) => {
  if(val && !imeisStockRaw.value.length){
    cargarImeisDeUbicacion(val).then(()=>{ buildImeiOptions(); buildLineItems(); });
  }
});

function buildSimSerieOptions(){
  const sims = imeisStockRaw.value.filter(r => esSimArticuloNombre(r.articulo_nombre));
  simSerieOptions.value = sims.map(i => ({ label: `${i.imei} — ${i.articulo_nombre}`, value: String(i.imei) }));
}

function buildLineItems(){
  if(!detalleVentaRaw.value.length || !imeisStockRaw.value.length) { lineItems.value = []; return; }
  const resultado = [];
  for(const d of detalleVentaRaw.value){
    if(esSimArticuloNombre(d.articulo_nombre)) continue;
    if(/instalacion/.test(normalizeTexto(d.articulo_nombre||''))) continue;
    const cantidad = Number(d.cantidad || d.cantidad_articulos || 1) || 1;
    const nombreDetNorm = normalizeTexto(d.articulo_nombre || d.descripcion || '');
    const imeisPosibles = imeisStockRaw.value
      .filter(r => {
        if(esSimArticuloNombre(r.articulo_nombre)) return false;
        const sameId = r.articulo_id && d.articulo_id && Number(r.articulo_id) === Number(d.articulo_id);
        const sameName = nombreDetNorm && normalizeTexto(r.articulo_nombre) === nombreDetNorm;
        return sameId || sameName;
      })
      .map(r => ({ label:`${r.imei} — ${r.articulo_nombre}`, value:String(r.imei) }));

    // En lugar de un bloque con N slots, crear N bloques (uno por unidad)
    for (let i = 0; i < cantidad; i++) {
      resultado.push({
        lineaId: (d.id || d.detalle_id || `${d.articulo_id}-${Math.random().toString(36).slice(2,7)}`) + `-u${i+1}`,
        articulo_id: d.articulo_id || null,
        articulo_nombre: d.articulo_nombre || d.descripcion || 'Artículo',
        imeisPosibles,
        selecciones: [null],
        sims: [null],
        // Campos por artículo (independientes por unidad)
        marca: '', submarca: '', modelo: '', placas: '', color: '', numero_economico: '',
        modelo_gps: '', accesorios: '', ubicacion_gps: '', ubicacion_bloqueo: '',
        get seleccionesCompletas(){ return this.selecciones.every(v=>!!v); }
      });
    }
  }
  lineItems.value = resultado;
}

async function cargarPagos() { pagos.value = []; }

async function cargarDatosTecnico() {
  try {
    if (!asignacion.value) return;
    let usuarios = await getUsuarios();
    let tecnico = usuarios.find(u => 
      u.username?.toLowerCase() === asignacion.value.tecnico?.toLowerCase() ||
      u.nombre?.toLowerCase() === asignacion.value.tecnico?.toLowerCase()
    );
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
  } catch (e) { console.error('Error en cargarDatosTecnico:', e); }
}

const detalleVentaRaw = ref([]);
const lineItems = ref([]);

const selectedImeisGlobal = computed(() => {
  const s = new Set();
  for (const li of lineItems.value) {
    for (const val of li.selecciones) if (val) s.add(val);
    for (const sim of li.sims || []) if (sim) s.add(sim);
  }
  return s;
});

function esArticuloServicio(d){
  const art = d?.articulo_id ? articulosIndex.value[d.articulo_id] : null;
  const tipo = String(art?.tipo || d?.tipo || '').toLowerCase();
  return tipo === 'servicio';
}

function opcionesVisibles(linea, slotIdx){
  const current = linea.selecciones[slotIdx];
  return linea.imeisPosibles.filter(opt => !selectedImeisGlobal.value.has(opt.value) || opt.value === current);
}

function simOpcionesVisiblesLinea(linea, slotIdx){
  const current = (linea.sims || [])[slotIdx];
  return simSerieOptions.value.filter(opt => !selectedImeisGlobal.value.has(opt.value) || opt.value === current);
}

function limpiarLinea(linea) {
  linea.selecciones.splice(0, linea.selecciones.length, ...Array(linea.selecciones.length).fill(null));
  linea.sims.splice(0, linea.sims.length, ...Array(linea.sims.length).fill(null));
}

const stockInsuficiente = computed(() => {
  const arr = [];
  for (const li of lineItems.value) {
    const requerido = li.selecciones.length;
    const disponibles = li.imeisPosibles.length;
    if (disponibles < requerido) arr.push({ lineaId: li.lineaId, articulo_nombre: li.articulo_nombre, requerido, disponibles });
  }
  return arr;
});

// Mantener sim_serie base por compatibilidad: primer SIM seleccionado en todos los bloques
const firstSelectedSim = computed(() => {
  for (const li of lineItems.value) {
    const s = (li.sims || []).find(Boolean);
    if (s) return s;
  }
  return '';
});
watch(firstSelectedSim, (v) => { form.value.sim_serie = v || ''; });

watch(selectedImeisGlobal, (setVal) => {
  if (!form.value.imei) {
    const first = Array.from(setVal).find(v => v !== form.value.sim_serie);
    if (first) form.value.imei = first;
  }
});

function validarAsignacionesImeis() {
  if (!lineItems.value.length) return true;
  const allSelected = [];
  for (const li of lineItems.value) allSelected.push(...li.selecciones.filter(Boolean));
  if (new Set(allSelected).size !== allSelected.length) {
    resultMessage.value = 'Hay IMEIs duplicados en las asignaciones de artículos.';
    showResultDialog.value = true;
    return false;
  }
  const incompletos = lineItems.value.filter(li => li.imeisPosibles.length >= li.selecciones.length && !li.selecciones.every(v => !!v));
  if (incompletos.length) {
    resultMessage.value = 'Debes completar todos los slots de IMEI o eliminar los sobrantes.';
    showResultDialog.value = true;
    return false;
  }
  return true;
}

async function cargarDatosCliente() {
  try {
    if (!asignacion.value) return;
    const { getClientes } = await import('@/services/clientesService');
    const clientes = await getClientes();
    const cliente = clientes.find(c => c.id == asignacion.value.cliente_id);
    if (cliente) {
      form.value.nombre_cliente = cliente.nombre || '';
      form.value.telefono_cliente = cliente.telefonos?.join(', ') || '';
      clienteUsuariosOptions.value = Array.isArray(cliente.usuarios)
        ? cliente.usuarios.map(u => ({ label: u, value: u }))
        : [];
      clientePlataformasOptions.value = Array.isArray(cliente.plataformas)
        ? cliente.plataformas.map(p => ({ label: p, value: p }))
        : [];
    }
    if (asignacion.value.venta_id) {
      const ventas = await getVentas();
      const venta = ventas.find(v => v.id == asignacion.value.venta_id);
      if (venta) {
        form.value.subtotal = venta.total || '';
        form.value.total = venta.total || '';
        form.value.forma_pago = venta.terminos_pago || '';
        try {
          const detalle = await getDetalleVenta(venta.id);
          if (Array.isArray(detalle) && detalle.length > 0) {
            detalleVentaRaw.value = detalle;
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
        } catch (e) { console.error('Error en getDetalleVenta:', e); }
        try {
          const ubicaciones = await getUbicaciones();
          const uMatch = ubicaciones.find(u => String(u.nombre || '').toLowerCase() === String(venta.almacen || '').toLowerCase());
          if (uMatch?.id) { ubicacionId.value = uMatch.id; }
        } catch (e) {}
        if (!ubicacionId.value) { ubicacionId.value = venta.ubicacion_id || null; }
        if (ubicacionId.value) {
          await cargarImeisDeUbicacion(ubicacionId.value);
          buildImeiOptions();
          buildLineItems();
        }
      }
    }
  } catch (e) { console.error('Error en cargarDatosCliente:', e); }
}

onMounted(async () => {
  loading.value = true;
  try {
    await cargarArticulos();
    const asignaciones = await getAsignacionesTecnicos();
    asignacion.value = asignaciones.find(a => String(a.id) === String(asignacionIdCentral.value) || String(a.venta_id) === String(asignacionIdCentral.value));
    if (!asignacion.value) {
      loading.value = false;
      resultMessage.value = 'No se encontró la asignación para el ID proporcionado.';
      showResultDialog.value = true;
      return;
    }
    form.value.asignacion_id = asignacion.value.id;
    await cargarDatosTecnico();
    await cargarDatosCliente();
    try { await cargarPagos(); } catch (e) { console.error('Error en cargarPagos:', e); }
    loading.value = false;
  } catch (e) { console.error('Error en onMounted:', e); loading.value = false; }
});

function cerrar() { emit('close'); router.push('/'); }

async function guardar() {
  attemptedSubmit.value = true;
  if (!asignacionIdValido.value) {
    resultMessage.value = 'ID de asignación inválido. No se puede guardar el reporte.';
    showResultDialog.value = true;
    scrollFocusFirstIssue();
    return;
  }
  if(!formCompleto.value){ scrollFocusFirstIssue(); }
  if (!validarAsignacionesImeis()) { scrollFocusFirstIssue(); return; }
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

    // Preparar payload por línea con datos de vehículo/dispositivo + IMEIs + SIMs
    const imeisArticulosPayload = lineItems.value.map(li => ({
      articulo_id: li.articulo_id,
      linea_id: li.lineaId,
      imeis: [...li.selecciones],
      sims: [...(li.sims || [])],
      marca: li.marca || '',
      submarca: li.submarca || '',
      modelo: li.modelo || '',
      placas: li.placas || '',
      color: li.color || '',
      numero_economico: li.numero_economico || '',
      modelo_gps: li.modelo_gps || '',
      accesorios: li.accesorios || '',
      ubicacion_gps: li.ubicacion_gps || '',
      ubicacion_bloqueo: li.ubicacion_bloqueo || ''
    }));

    // Compatibilidad: setear campos base con el primer IMEI/SIM seleccionado
    if (!form.value.sim_serie) {
      const firstSim = firstSelectedSim.value;
      if (firstSim) form.value.sim_serie = firstSim;
    }
    if (!form.value.imei && selectedImeisGlobal.value.size) {
      const firstImei = Array.from(selectedImeisGlobal.value).find(v => v !== form.value.sim_serie);
      if (firstImei) form.value.imei = firstImei;
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
      ubicacion_bloqueo: form.value.ubicacion_bloqueo || '',
      imeis_articulos: imeisArticulosPayload,
      // Compatibilidad: también enviar colección aplanada de SIMs si backend aún la usa
      sim_series: lineItems.value.flatMap(li => (li.sims || []).filter(Boolean))
    };

    const resp = await addReporteServicio(payload);
    const baseMessage = (resp && typeof resp === 'object' && 'message' in resp)
      ? String(resp.message)
      : 'Reporte de servicio creado exitosamente';

    // Marcar IMEIs/SIM como vendidos (si existe lógica posterior)
    try {
      // Aquí quedaría la llamada a servicio de inventario si aplica
    } catch (e) { imeiUpdateError.value = true; }

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

function onDialogAccept() { showResultDialog.value = false; if (saveSuccess.value) { router.push('/'); } }

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

const baseObligatorios = ['tipo_servicio','subtotal','total'];
function isCampoObligatorio(c){
  return baseObligatorios.includes(c);
}
function isCampoInvalido(c){
  if(!isCampoObligatorio(c)) return false;
  const val = form.value[c];
  if(c === 'total') return val === null || val === undefined || val === '' || isNaN(val);
  return !String(val ?? '').trim();
}
const formCompleto = computed(() => baseObligatorios.filter(isCampoObligatorio).every(c => !isCampoInvalido(c)));

watch(usarTotalMontoTecnico, val => { if (val) { form.value.monto_tecnico = Number(form.value.total) || 0; } });
watch(() => form.value.total, val => { if (usarTotalMontoTecnico.value) { form.value.monto_tecnico = Number(val) || 0; } });

function scrollFocusFirstIssue(){
  nextTick(() => {
    const container = document.querySelector('.reporte-form');
    if(!container) return;
    const firstInvalid = container.querySelector('.p-invalid');
    if(firstInvalid){
      firstInvalid.scrollIntoView({behavior:'smooth', block:'center'});
      const focusable = firstInvalid.querySelector('input,textarea,.p-dropdown');
      if(focusable && 'focus' in focusable) focusable.focus();
    }
  });
}

const shouldUseTwoCols = computed(() => (lineItems.value?.length || 0) >= 2);
</script>

<style scoped>
@import '@/assets/main.css';
.reporte-servicio-container { max-width: 1280px; margin: 2rem auto; padding: 1.75rem; }
.reporte-title { text-align: center; margin: 0 0 1rem; }

/* Header global más centrado y aireado */
.global-header { max-width: 960px; margin: 0 auto 1.25rem; }

/* Espaciado general de bloques e inputs */
.col-block { padding: 0.75rem 1rem; }
.col-block .form-group { margin-bottom: 0.9rem; }

/* Grid de artículos: 1 columna móvil, 2 columnas en desktop si hay 2+ artículos */
.line-items-grid { display: grid; grid-template-columns: 1fr; gap: 1.5rem; }
@media (min-width: 768px) { .line-items-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); } }

/* Sección de cobro: 1 columna móvil, 2 columnas desktop */
.cobro-section { margin-top: 1.25rem; }
.cobro-grid { display: grid; grid-template-columns: 1fr; gap: 1.25rem; }
@media (min-width: 768px) { .cobro-grid.two-cols { grid-template-columns: repeat(2, minmax(0, 1fr)); } }
.span-2 { grid-column: 1 / -1; }

/* Títulos centrados solicitados */
.articulo-title { text-align: center; margin: 0 0 .75rem; }
.line-header { text-align: center; margin: .25rem 0 .5rem; }

/* Slots con más separación */
.slots-grid { display: grid; grid-template-columns: 1fr; gap: .75rem; }

.required-label::after { content: ' *'; color: #d32f2f; }
.error-msg { color:#d32f2f; font-size:0.7rem; margin-top:-0.25rem; display:block; }
.monto-tecnico-row { display:flex; gap:.75rem; align-items:flex-start; }
.checkbox-inline { display:flex; align-items:center; gap:.35rem; margin-top:.25rem; }
.inline-label { font-weight:normal; margin:0; }
</style>